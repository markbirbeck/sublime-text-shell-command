import os
import shlex
import subprocess
import threading
import select

import sublime

from . import SublimeHelper as SH


def process(commands, callback=None, working_dir=None, **kwargs):

    # If there's no callback method then just return the output as
    # a string:
    #
    if callback is None:
        return _process(commands, working_dir=working_dir, **kwargs)

    # If there is a callback then run this asynchronously:
    #
    else:
        thread = threading.Thread(target=_process, kwargs={
            'commands': commands,
            'callback': callback,
            'working_dir': working_dir
        })
        thread.start()


def _process(commands, callback=None, working_dir=None, **kwargs):
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

            # We're going to keep polling the command and either:
            #
            #   1. we get None to tell us that the command is still running, or;
            #   2. we get a return code to indicate that the command has finished.
            #
            return_code = None
            while return_code is None:
                return_code = proc.poll()

                # If there's no error then see what we got from the command:
                #
                if return_code is None or return_code == 0:
                    r, _, _ = select.select([proc.stdout], [], [])
                    if r:
                        # Process whatever output we can get:
                        #
                        output = True
                        while output:
                            output = proc.stdout.readline().decode()

                            # If there is no callback function, then batch up
                            # the output. Otherwise pass it back to the
                            # caller as it becomes available:
                            #
                            if callback is None:
                                results += output
                            else:
                                SH.main_thread(callback, output, **kwargs)

        except subprocess.CalledProcessError as e:

            SH.main_thread(callback, e.returncode)

        except OSError as e:

            if e.errno == 2:
                sublime.message_dialog('Command not found\n\nCommand is: %s' % command)
            else:
                raise e

    # Concatenate all of the results and return the value. If we've been
    # using the callback then just make one last call with 'None' to indicate
    # that we're finished:
    #
    result = ''.join(results)

    if callback is None:
        return result

    SH.main_thread(callback, None, **kwargs)
