import os
import shlex
import subprocess
import threading
import select

import sublime

from . import SublimeHelper as SH


def process(commands, callback=None, stdin=None, settings=None, working_dir=None, wait_for_completion=None, **kwargs):

    # If there's no callback method then just return the output as
    # a string:
    #
    if callback is None:
        return _process(commands, stdin=stdin, settings=settings, working_dir=working_dir, wait_for_completion=wait_for_completion, **kwargs)

    # If there is a callback then run this asynchronously:
    #
    else:
        thread = threading.Thread(target=_process, kwargs={
            'commands': commands,
            'callback': callback,
            'stdin': stdin,
            'settings': settings,
            'working_dir': working_dir,
            'wait_for_completion': wait_for_completion
        })
        thread.start()


def _process(commands, callback=None, stdin=None, settings=None, working_dir=None, wait_for_completion=None, **kwargs):
    '''Process one or more OS commands.'''

    if wait_for_completion is None:
        wait_for_completion = False

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

        # See if there are any interactive shell settings that we could use:
        #
        bash_env = None
        if settings is not None and settings.has('shell_configuration_file'):
            bash_env = settings.get('shell_configuration_file')
        else:
            bash_env = os.getenv('ENV')

        if bash_env is not None:
            command = '. {} && {}'.format(bash_env, command)

        try:

            proc = subprocess.Popen(command,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=True,
                                    cwd=working_dir,
                                    startupinfo=startupinfo)

            if stdin is not None:
                proc.stdin.write(stdin.encode('utf-8'))
                proc.stdin.close();
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
                    # Process whatever output we can get:
                    #
                    output = True
                    while output:
                        output = proc.stdout.readline().decode()

                        # If the caller wants everything in one go, or
                        # there is no callback function, then batch up
                        # the output. Otherwise pass it back to the
                        # caller as it becomes available:
                        #
                        if wait_for_completion is True or callback is None:
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

    if wait_for_completion is True:
        SH.main_thread(callback, result, **kwargs)

    SH.main_thread(callback, None, **kwargs)
