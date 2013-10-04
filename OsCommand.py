from . import SublimeHelper as SH
from . import OsShell


class OsCommandCommand(SH.TextCommand):

    def run(self, edit, command='', prompt=None, region=False, arg_required=False, panel=False, title=None):

        # If regions should be used then work them out, and append
        # them to the command:
        #
        if region is True:
            arg = self.get_region().strip()

            if arg == '':
                if arg_required is True:
                    SH.error_message('This command requires a parameter.')
                    return
            else:
                command = command + ' ' + arg

        # Setup a closure to run the command:
        #
        def _C(command):

            self.run_os_command(command, panel=panel, title=title)

        # If no command is specified then we prompt for one, otherwise
        # we can just execute the command:
        #
        if command.strip() == '':
            if prompt is None:
                prompt = 'OS Command'
            self.view.window().show_input_panel(prompt, '', _C, None, None)
        else:
            _C(command)

    def run_os_command(self, command, panel=False, title=None):

        view = self.view
        window = view.window()

        if command.strip() == '':
            SH.error_message('No command provided.')
            return

        working_dir = self.get_working_dir()

        # Run the command and write any output to the buffer:
        #
        def _C(output):

            output = output.strip()
            if output == '':
                output = 'Shell command succeeded with no output'

            # If we didn't get any output then don't do anything:
            #
            if output != '':
                # If a panel has been requested then create one and show it,
                # otherwise create a new buffer, and set its caption:
                #
                if panel is True:
                    console = window.get_output_panel('os-command')
                    window.run_command('show_panel', {'panel': 'output.os-command'})
                else:
                    console = window.new_file()
                    caption = title if title else '*Shell Command Output*'
                    console.set_name(caption)

                # Indicate that this buffer is a scratch buffer:
                #
                console.set_scratch(True)

                # Insert the output into the buffer:
                #
                console.set_read_only(False)
                console.run_command('insert_text', {'pos': 0, 'msg': output})
                console.set_read_only(True)

        OsShell.process(command, _C, working_dir=working_dir)
