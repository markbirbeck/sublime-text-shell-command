# Helper functions and classes to wrap common Sublime Text idioms:
#
import functools
import os

import sublime
import sublime_plugin


def main_thread(callback, *args, **kwargs):

    sublime.set_timeout_async(functools.partial(callback, *args, **kwargs), 0)


class TextCommand(sublime_plugin.TextCommand):

    def get_region(self, view=None, can_select_entire_buffer=False):
        '''Get the value under the cursor, or cursors.'''

        value = ''

        if view is None:
            view = self.view

        # If there is no view then all bets are off:
        #
        if view is not None:

            # Get the selection:
            #
            selection = view.sel()

            # If there is no selection then optionally use the entire buffer:
            #
            if can_select_entire_buffer is True:
                if len(selection) == 1 and selection[0].empty():
                    selection = [sublime.Region(0, view.size())]

            if selection is not None:

                # For each region in the selection, either use it directly,
                # or expand it to take in the 'word' that the cursor is on:
                #
                for region in selection:
                    if region.empty():
                        region = view.expand_by_class(
                            region,
                            sublime.CLASS_WORD_START | sublime.CLASS_WORD_END,
                            ' ():'
                        )
                    value = value + ' ' + view.substr(region)

        return value

    def get_working_dir(self):
        '''Get the view's current working directory.'''

        view = self.view
        folders = []

        if view is not None:
            # If there is a working directory defined in the data settings then use
            # it:
            #
            if self.data_key is not None:
                settings = view.settings()
                if settings.has(self.data_key):
                    data = settings.get(self.data_key + '_data', None)
                    if data is not None:
                        if 'working_dir' in data:
                            folders.append(data['working_dir'])

            settings = view.settings()
            if settings.has('working_dir'):
                folders.append(settings.get('working_dir'))

            window = view.window()
            if window is not None:

                # If there is a project file in the window then use it to work
                # out a working directory:
                #
                file_name = window.project_file_name()
                if file_name is not None:
                    dirname, _ = os.path.split(os.path.abspath(file_name))
                    folders.append(dirname)

                # Alternatively, see if there are any open folders, and if so, use the
                # path of the first one:
                #
                folders.extend(window.folders())

            # If there is a file in the active view then use it to work out
            # a working directory using "folders" as a priority list and 
            # looking for a common ancestor to the current view's file:
            #
            file_name = view.file_name()
            if file_name is not None:
                dirname, _ = os.path.split(os.path.abspath(file_name))
                folders.append(dirname)
                for folder in folders:
                    if os.path.commonprefix([folder, dirname]) == dirname:
                        return dirname
            # otherwise just return the first folder
            if folders:
                return folders[0]
        return None


# The command that is executed to insert text into a view:
#
class SublimeHelperInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, pos, msg):

        if msg is not None:
            self.view.insert(edit, pos, msg)


# The command that is executed to erase text in a view:
#
class SublimeHelperEraseTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, a, b):

        self.view.erase(edit, sublime.Region(a, b))


# The command that is executed to clear a buffer:
#
class SublimeHelperClearBufferCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        view = self.view
        view.run_command('sublime_helper_erase_text', {'a': 0, 'b': view.size()})


class OutputTarget():

    def __init__(self, window, data_key, command, working_dir, title=None, syntax=None, panel=False, console=None):

        # If a panel has been requested then create one and show it,
        # otherwise create a new buffer, and set its caption:
        #
        if console is not None:
            self.console = console
        else:
            if panel is True:
                self.console = window.get_output_panel('ShellCommand')
                window.run_command('show_panel', {'panel': 'output.ShellCommand'})
            else:
                self.console = window.new_file()
                caption = title if title else '*Shell Command Output*'
                self.console.set_name(caption)

            # Indicate that this buffer is a scratch buffer:
            #
            self.console.set_scratch(True)
            self.console.set_read_only(True)

            # Set the syntax for the output:
            #
            if syntax is not None:
                resources = sublime.find_resources(syntax + '.tmLanguage')
                self.console.set_syntax_file(resources[0])

            # Set a flag on the view that we can use in key bindings:
            #
            settings = self.console.settings()
            settings.set(data_key, True)

            # Also, save the command and working directory for later,
            # since we may need to refresh the panel/window:
            #
            data = {
                'command': command,
                'working_dir': working_dir
            }
            settings.set(data_key + '_data', data)

    def append_text(self, output):

        console = self.console

        # Insert the output into the buffer:
        #
        console.set_read_only(False)
        console.run_command('sublime_helper_insert_text', {'pos': console.size(), 'msg': output})
        console.set_read_only(True)

    def set_status(self, tag, message):

        self.console.set_status(tag, message)


# Code largely taken from the nifty class in sublime_package_control:
#
#   https://github.com/wbond/sublime_package_control/blob/master/package_control/thread_progress.py
#
# The minor changes made are simply so that we deal with a view rather than a
# thread, which allows us to relate the status messages more closely with their
# corresponding buffer. It does mean that it's then the caller's responsibility
# to call start() and stop(), though.
#
class ProgressDisplay():
    """
    Animates an indicator, [=   ], in the status area until stopped

    :param view:
        The view that 'owns' the activity

    :param tag:
        The tag to identify the message within sublime

    :param message:
        The message to display next to the activity indicator
    """

    def __init__(self, view, tag, message, heartbeat=None):
        self.view = view
        self.tag = tag
        self.message = message
        self.addend = 1
        self.size = 8
        self.heartbeat = heartbeat if heartbeat is not None else 100
        self.stop()
        sublime.set_timeout(lambda: self.run(), self.heartbeat)

    def start(self):
        self._running = True
        self.counter = 0
        self.run()

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running

    def set_status(self, message):
        self.view.set_status(self.tag, message)

    def run(self):
        if not self.is_running():
            self.set_status('')
            return

        i = self.counter

        before = i % self.size
        after = (self.size - 1) - before

        self.set_status('%s [%s=%s]' % (self.message, ' ' * before, ' ' * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        self.counter += self.addend

        sublime.set_timeout(lambda: self.run(), self.heartbeat)
