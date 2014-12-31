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
        self.output_written = False

    def run(self, edit, command=None, command_prefix=None, prompt=None, region=None, arg_required=None, stdin=None, panel=None, title=None, syntax=None, refresh=None, wait_for_completion=None, root_dir=False):

        # Map previous use of 'region' parameter:
        #
        if region is True:
            region = 'arg'

        if arg_required is None:
            arg_required = False

        if panel is None:
            panel = False

        if refresh is None:
            refresh = False

        # If regions should be used as arguments for the command then
        # create an argument from the current selection, ready to
        # append to the command:
        #
        arg = None
        if region == 'arg':
            arg = self.get_region().strip()

            if arg == '':
                if arg_required is True:
                    sublime.message_dialog('This command requires a parameter.')
                    return

        # If regions should be used as input to the command then
        # pipe the current selection to the command as stdin:
        #
        if region == 'stdin' and stdin is None:
            stdin = self.get_region(can_select_entire_buffer=True)

        # Setup a closure to run the command:
        #
        def _C(command):

            if command_prefix is not None:
                command = command_prefix + ' ' + command

            if arg is not None:
                command = command + ' ' + arg

            self.run_shell_command(command, stdin=stdin, panel=panel, title=title, syntax=syntax, refresh=refresh, wait_for_completion=wait_for_completion, root_dir=root_dir)

        # If no command is specified then we prompt for one, otherwise
        # we can just execute the command:
        #
        if command is None:
            if prompt is None:
                prompt = self.default_prompt
            self.view.window().show_input_panel(prompt, '', _C, None, None)
        else:
            _C(command)

    def run_shell_command(self, command=None, stdin=None, panel=False, title=None, syntax=None, refresh=False, console=None, working_dir=None, wait_for_completion=None, root_dir=False):

        view = self.view
        window = view.window()
        settings = sublime.load_settings('ShellCommand.sublime-settings')

        if command is None:
            sublime.message_dialog('No command provided.')
            return

        if working_dir is None:
            working_dir = self.get_working_dir(root_dir=root_dir)

        # Run the command and write any output to the buffer:
        #
        message = self.default_prompt + ': (' + ''.join(command)[:20] + ')'

        self.finished = False
        self.output_target = None
        self.output_written = False

        # Start our progress bar in the initiating window. If a new window
        # gets opened then the progress bar will get moved to that:
        #
        self.progress = SH.ProgressDisplay(view, message, message,
          settings.get('progress_display_heartbeat'))
        self.progress.start()

        def _C(output):

            # If output is None then the command has finished:
            #
            if output is None:
                self.finished = True

                # If there has been no output:
                #
                if self.output_written is False:
                    show_message = settings.get('show_success_but_no_output_message')
                    if show_message:
                        output = settings.get('success_but_no_output_message')

                # Check whether the initiating view needs refreshing:
                #
                if refresh is True:
                    view.run_command('shell_command_refresh')

                # Stop the progress bar:
                #
                self.progress.stop()

            # If there is something to output...
            #
            if output is not None:

                # ...only allow blank lines if something else has already been
                # written:
                #
                if self.output_written is True or len(output.strip()) > 0:

                    # If no output window has been created yet then create one now:
                    #
                    if self.output_target is None:
                        self.output_target = SH.OutputTarget(window,
                                                             self.data_key,
                                                             command,
                                                             working_dir,
                                                             title=title,
                                                             syntax=syntax,
                                                             panel=panel,
                                                             console=console)

                        # Switch our progress bar to the new window:
                        #
                        if self.finished is False:
                            self.progress.stop()
                            self.progress = SH.ProgressDisplay(self.output_target, message, message,
                              settings.get('progress_display_heartbeat'))
                            self.progress.start()

                    # Append our output to whatever buffer is being used, and
                    # track that some output has now been written:
                    #
                    self.output_target.append_text(output)
                    self.output_written = True

        OsShell.process(command, _C, stdin=stdin, settings=settings, working_dir=working_dir, wait_for_completion=wait_for_completion)


class ShellCommandPromptCommand(ShellCommandCommand):

    ''' User can input with prompt panel through ${1} like variables.
    EX) git branch -m ${current_branch} ${new_branch:Enter branch name}
    in $, colon(:) is a separator, ${<variable_name>:<Prompt message if not exist>}.
    User input invoked from left to right.
    '''

    def run_shell_command(self, command=None, stdin=None, panel=False, title=None, syntax=None, refresh=False, console=None, working_dir=None, wait_for_completion=None, root_dir=False):
        if not command:
            return  # FIXME: command is empty, should return error message.

        asks, template = self.parse_command(command)
        argdict = {}
        def _on_input_end(argdict):
            if len(asks) != len(argdict):
                return  # NOTE: assertion code (Please remove after well tested)
            argstr = template.format(**argdict)
            super(__class__, self).run_shell_command(argstr, stdin, panel, title, syntax, refresh, console, working_dir, wait_for_completion, root_dir)
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
        import re

        parsed = re.split(r'\${(.*?)}', command)
        # if not variables, return command itself
        if len(parsed) == 1:
            return [], command
        template_parts = []
        asks = []
        for idx, item in enumerate(parsed, start=1):
            # variable
            auto_variable = 0
            if idx % 2 == 0:
                chs = item.split(':')
                variable_name = chs[0]
                if not variable_name:
                    variable_name = '_' + str(auto_variable)
                    auto_variable += 1
                v = self.find_defined_value(variable_name)
                if v:
                    template_parts.append(v)
                    continue
                # defined variable not found. Start prompting.
                if len(chs) == 1:
                    prompt_message = variable_name + ':'
                    default_value = ''
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

        ShellCommandCommand.run(self, edit, command=command, command_prefix=command_prefix, prompt=prompt, region='stdin', arg_required=True, panel=panel, title=title, syntax=syntax, refresh=refresh)


# Refreshing a shell command simply involves re-running the original command:
#
class ShellCommandRefreshCommand(ShellCommandCommand):

    def run(self, edit, callback=None):

        console = self.view

        settings = console.settings()
        if settings.has(self.data_key):
            data = settings.get(self.data_key + '_data', None)
            if data is not None:

                console.set_read_only(False)
                console.run_command('sublime_helper_clear_buffer')
                console.set_read_only(True)

                self.run_shell_command(command=data['command'], console=console, working_dir=data['working_dir'])

