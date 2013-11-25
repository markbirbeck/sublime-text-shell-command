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

    def run(self, edit, command=None, command_prefix=None, prompt=None, region=None, arg_required=None, panel=None, title=None, syntax=None, refresh=None, wait_for_completion=None):

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

            self.run_shell_command(command, panel=panel, title=title, syntax=syntax, refresh=refresh, wait_for_completion=wait_for_completion)

        # If no command is specified then we prompt for one, otherwise
        # we can just execute the command:
        #
        if command is None:
            if prompt is None:
                prompt = self.default_prompt
            self.view.window().show_input_panel(prompt, '', _C, None, None)
        else:
            _C(command)

    def run_shell_command(self, command=None, panel=False, title=None, syntax=None, refresh=False, console=None, working_dir=None, wait_for_completion=None):

        view = self.view
        window = view.window()
        settings = sublime.load_settings('ShellCommand.sublime-settings')

        if command is None:
            sublime.message_dialog('No command provided.')
            return

        if working_dir is None:
            working_dir = self.get_working_dir()

        # Run the command and write any output to the buffer:
        #
        output_target = SH.OutputTarget(window, self.data_key, command, working_dir, title=title, syntax=syntax, panel=panel, console=console)
        message = self.default_prompt + ': (' + ''.join(command)[:20] + ')'
        progress = SH.ProgressDisplay(output_target, message, message,
                                      settings.get('progress_display_heartbeat'))

        def _C(output):

            if output is not None:
                output_target.append_text(output)
                self.output_written = True
                progress.start()
            else:
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

                progress.stop()

        OsShell.process(command, _C, working_dir=working_dir, wait_for_completion=wait_for_completion)


class ShellCommandOnRegionCommand(ShellCommandCommand):

    def run(self, edit, command=None, command_prefix=None, prompt=None, arg_required=None, panel=None, title=None, syntax=None, refresh=None):

        ShellCommandCommand.run(self, edit, command=command, command_prefix=command_prefix, prompt=prompt, region=True, arg_required=True, panel=panel, title=title, syntax=syntax, refresh=refresh)


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

