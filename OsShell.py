import os
import shlex
import subprocess

from . import SublimeHelper as SH


def process(commands, callback=None, working_dir=None, **kwargs):
    '''Process one or more OS commands.'''

    # We're expecting a list of commands, so if we only have one, convert
    # it to a list:
    #
    if isinstance(commands, str):
        commands = [commands]

    results = []

    # Windows needs STARTF_USESHOWWINDOW in order to start the process with a
    # hidden window.
    #
    # See:
    #
    #  http://stackoverflow.com/questions/1016384/cross-platform-subprocess-with-hidden-window
    #
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Now we can execute each command:
    #
    for command in commands:

        # Split the command properly, in case it has options and
        # parameters:
        #
        command = shlex.split(command)

        try:

            proc = subprocess.Popen(command,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    cwd=working_dir,
                                    startupinfo=startupinfo)
            output, _ = proc.communicate()

            results += output.decode()

        except subprocess.CalledProcessError as e:

            SH.main_thread(callback, e.returncode)

        except OSError as e:

            if e.errno == 2:
                SH.error_message('Command not found\n\nCommand is: %s' % command)
            else:
                raise e

    # Concatenate all of the results and then either return the value
    # or pass the value to the callback:
    #
    result = ''.join(results)

    if callback is None:
        return result

    SH.main_thread(callback, result, **kwargs)
