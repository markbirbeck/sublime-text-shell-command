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
                    SH.error_message('This command requires a parameter.')
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
            SH.error_message('No command provided.')
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


class ShellCommandOnRegionCommand(ShellCommandCommand):

    def run(self, edit, command=None, command_prefix=None, prompt=None, arg_required=None, panel=None, title=None, syntax=None, refresh=None):

        ShellCommandCommand.run(self, edit, command=command, command_prefix=command_prefix, prompt=prompt, region=True, arg_required=True, panel=panel, title=title, syntax=syntax, refresh=refresh)


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
