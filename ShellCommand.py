import sublime

from . import SublimeHelper as SH
from . import OsShell


class ShellCommandCommand(SH.TextCommand):

    def __init__(self, plugin, default_prompt=None, **kwargs):

        SH.TextCommand.__init__(self, plugin, **kwargs)
        if default_prompt is None:
            self.default_prompt = 'Shell Command'
        else:
            self.default_prompt = default_prompt
        self.data_key = 'ShellCommand'

    def run(self, edit, command=None, command_prefix=None, prompt=None, region=None, arg_required=None, panel=None, title=None, syntax=None, refresh=None):

        if region is None:
            region is False

        if arg_required is None:
            arg_required = False

        if panel is None:
            panel = False

        if refresh is None:
            refresh = False

        arg = None

        # If regions should be used then work them out, and append
        # them to the command:
        #
        if region is True:
            arg = self.get_region().strip()

            if arg == '':
                if arg_required is True:
                    sublime.message_dialog('This command requires a parameter.')
                    return

        # Setup a closure to run the command:
        #
        def _C(command):

            if command_prefix is not None:
                command = command_prefix + ' ' + command

            if arg is not None:
                command = command + ' ' + arg

            self.run_shell_command(command, panel=panel, title=title, syntax=syntax, refresh=refresh)

        # If no command is specified then we prompt for one, otherwise
        # we can just execute the command:
        #
        if command is None:
            if prompt is None:
                prompt = self.default_prompt
            self.view.window().show_input_panel(prompt, '', _C, None, None)
        else:
            _C(command)

    def run_shell_command(self, command=None, panel=False, title=None, syntax=None, refresh=False):

        view = self.view
        window = view.window()

        if command is None:
            sublime.message_dialog('No command provided.')
            return

        working_dir = self.get_working_dir()

        # Run the command and write any output to the buffer:
        #
        def _C(output):

            output = output.strip()
            if output == '':
                settings = sublime.load_settings('ShellCommand.sublime-settings')
                show_message = settings.get('show_success_but_no_output_message')
                if show_message:
                    output = settings.get('success_but_no_output_message')

            # If we didn't get any output then don't do anything:
            #
            if output != '':
                # If a panel has been requested then create one and show it,
                # otherwise create a new buffer, and set its caption:
                #
                if panel is True:
                    console = window.get_output_panel('ShellCommand')
                    window.run_command('show_panel', {'panel': 'output.ShellCommand'})
                else:
                    console = window.new_file()
                    caption = title if title else '*Shell Command Output*'
                    console.set_name(caption)

                # Indicate that this buffer is a scratch buffer:
                #
                console.set_scratch(True)

                # Set the syntax for the output:
                #
                if syntax is not None:
                    resources = sublime.find_resources(syntax + '.tmLanguage')
                    console.set_syntax_file(resources[0])

                # Insert the output into the buffer:
                #
                console.set_read_only(False)
                console.run_command('sublime_helper_insert_text', {'pos': 0, 'msg': output})
                console.set_read_only(True)

                # Set a flag on the view that we can use in key bindings:
                #
                settings = console.settings()
                settings.set(self.data_key, True)

                # Also, save the command and working directory for later,
                # since we may need to refresh the panel/window:
                #
                data = {
                    'command': command,
                    'working_dir': working_dir
                }
                settings.set(self.data_key + '_data', data)

            if refresh is True:
                view.run_command('shell_command_refresh')

        OsShell.process(command, _C, working_dir=working_dir)


class ShellCommandPromptCommand(ShellCommandCommand):

    ''' User can input with prompt panel through ${1} like variables.
    EX) git branch -m ${current_branch} ${new_branch:Enter branch name}
    in $, colon(:) is a separator, ${<variable_name>:<Prompt message if not exist>}.
    User input invoked from left to right.
    '''

    def run_shell_command(self, command=None, panel=False, title=None, syntax=None, refresh=False):
        if not command:
            return  # FIXME: command is empty, should return error message.

        asks, template = self.parse_command(command)
        argdict = {}
        def _on_input_end(arglist):
            if len(asks) != len(arglist):
                return  # NOTE: assertion code (Please remove after well tested)
            argstr = template.format(**arglist)
            super(__class__, self).run_shell_command(argstr, panel, title, syntax, refresh)
        if asks:
            self.ask_to_user(asks, _on_input_end)
        else:
            self.run_shell_command(template, out_to=out_to, title=title, syntax=syntax,
                                   refresh=refresh, output_filter=output_filter)

    def ask_to_user(self, asks, callback):
        askstack = asks[:]
        arglist = []

        def _on_done(arg):
            arglist.append(arg)
            if askstack:
                _run()
            else:
                # all variable input
                argdict = {x['variable']:y for x, y in zip(asks, arglist)}
                callback(argdict)

        def _on_cancel():
            callback([])

        def _run():
            ask = askstack.pop(0)
            self.view.window().show_input_panel(ask['message'], ask['default'], _on_done, None, _on_cancel)
        _run()

    def parse_command(self, command):
        ''' Inspired by Sublime's snippet syntax; "${...}" is a variable.
        But it's slightly different, ${<variable_name>:<Prompt message if not exist>[:default value]}
        EX) git branch -m ${current_branch} ${new_branch:Enter branch name}
        '''
        parsed = re.split(r'\${(.*?)}', command)
        # if not variables, return command itself
        if len(parsed) == 1:
            return [], command
        template_parts = []
        asks = []
        for idx, item in enumerate(parsed, start=1):
            # variable
            if idx % 2 == 0:
                chs = item.split(':')
                variable_name = chs[0]
                v = self.find_defined_value(variable_name)
                if v:
                    template_parts.append(v)
                    continue
                # defined variable not found. Start prompting.
                if len(chs) == 1:
                    prompt_message = variable_name + ':'
                else:
                    prompt_message = chs[1]
                    default_value = chs[2] if len(chs) > 2 else ''
                asks.append(dict(variable=variable_name, message=prompt_message, default=default_value))
                template_parts.append('{%s}' % variable_name)
            else:
                template_parts.append(item)
        return asks, ''.join(template_parts)

    def find_defined_value(self, item):
        window = self.view.window()
        if item == 'project_folders':
            return ' '.join(window.folders() or [])
        elif item == 'project_name':
            project_path = window.project_file_name()
            if not project_path:
                return ''
            return os.path.basename(project_path).replace('.sublime-project', '')

class ShellCommandOnRegionCommand(ShellCommandCommand):

    def run(self, edit, command=None, command_prefix=None, prompt=None, arg_required=None, panel=None, title=None, syntax=None, refresh=None):

        ShellCommandCommand.run(self, edit, command=command, command_prefix=command_prefix, prompt=prompt,
                                region=True, arg_required=True, panel=panel, title=title, syntax=syntax, refresh=refresh)


# Refreshing a shell command simply involves re-running the original command:
#
class ShellCommandRefreshCommand(ShellCommandCommand):

    def run(self, edit, callback=None):

        view = self.view

        settings = view.settings()
        if settings.has(self.data_key):
            data = settings.get(self.data_key + '_data', None)
            if data is not None:

                # Create a local function that will re-write the buffer contents:
                #
                def _C(output, **kwargs):

                    console = view

                    console.set_read_only(False)
                    region = sublime.Region(0, view.size())
                    console.run_command('sublime_helper_erase_text', {'a': region.a, 'b': region.b})
                    console.run_command('sublime_helper_insert_text', {'pos': 0, 'msg': output})
                    console.set_read_only(True)

                    if callback is not None:
                        callback()

                OsShell.process(data['command'], _C, working_dir=data['working_dir'])
