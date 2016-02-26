# Helper functions and classes to wrap common Sublime Text idioms:
#
import functools
import os

import sublime
import sublime_plugin


def main_thread(callback, *args, **kwargs):

    sublime.set_timeout_async(functools.partial(callback, *args, **kwargs), 0)


class TextCommand(sublime_plugin.TextCommand):

    def get_view_and_window(self, view=None):

        # Find a window to attach any prompts, panels and new views to.
        # If view that was active when the command was run has a window
        # then we can use that:
        #
        if view is None:
            view = self.view

        if view is not None:
            window = view.window()

        # But if the view doesn't have a window, or there is no view at
        # all, then use the active window and view as set in the Sublime
        # module:
        #
        if view is None or window is None:
            window = sublime.active_window()
            view = window.active_view()

        return view, window

    def get_region(self, view=None, can_select_entire_buffer=False):
        '''Get the value under the cursor, or cursors.'''

        value = ''

        view, window = self.get_view_and_window(view)

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

    def get_working_dir(self, root_dir=False):
        '''Get the view's current working directory.'''

        view, window = self.get_view_and_window()

        if view is not None:

            # This list will contain a set of directories that are candidates
            # for the working directory:
            #
            folders = []

            # If there is a working directory defined in the data settings then use
            # it:
            #
            if self.data_key is not None:
                settings = view.settings()
                if settings.has(self.data_key):
                    data = settings.get(self.data_key + '_data', None)
                    if data is not None:
                        if 'working_dir' in data and data['working_dir'] is not None:
                            folders.append(data['working_dir'])

            if window is not None:

                # If there is a project file in the window then use it to work
                # out a working directory:
                #
                file_name = window.project_file_name()
                if file_name is not None:
                    dirname, _ = os.path.split(os.path.abspath(file_name))
                    folders.append(dirname)

                # Now see if there are any open folders, and if so, add them
                # to the list:
                #
                folders.extend(window.folders())

            # If there is a file in the active view then use it to work out
            # a working directory:
            #
            file_name = view.file_name()
            if file_name is not None:
                dirname, _ = os.path.split(os.path.abspath(file_name))
                folders.append(dirname)

                # Now see if any of the directories in the priority list (in
                # folders[]) is a common ancestor to the current view's file:
                #
                for folder in folders:
                    commonprefix = os.path.commonprefix([folder, dirname])

                    # If we want the root directory then the match must be against
                    # the folder:
                    #
                    if root_dir is True:
                        if commonprefix == folder:
                            return folder
                    else:
                        # If we're not bothered about the root then the match must
                        # be against the file's directory:
                        #
                        if commonprefix == dirname:
                            return dirname

            # If there is no view file, or it has no relationship to any of
            # the directories in the priority list, then just return the first
            # folder in the list (if there is one):
            #
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

    def __init__(self, window, data_key, command, working_dir, title=None, syntax=None, panel=False, console=None, target=None):

        self.target = target
        if target == 'point' and console is None:
            console = window.active_view()

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
                caption = title if title else '*ShellCommand Output*'
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

    def append_text(self, output, scroll_show_maximum_output=False):

        console = self.console

        # If the buffer is read only then temporarily disable that:
        #
        is_read_only = console.is_read_only()
        if is_read_only:
            console.set_read_only(False)

        # If the target is 'point' then the insertion point is the current
        # cursor position, overwriting any selection there might be:
        #
        if self.target == 'point':
            sel = console.sel()[0]
            if not sel.empty():
                console.run_command('sublime_helper_erase_text', {'a': sel.begin(), 'b': sel.end()})
            pos = sel.begin()

        # If the target is not 'point' the the insertion point is the end
        # of the buffer:
        #
        else:
            pos = console.size()

        # Insert the output into the buffer. If the flag is set to show maximum output
        # then we make the end of the buffer visible:
        #
        console.run_command('sublime_helper_insert_text', {'pos': pos, 'msg': output})
        if scroll_show_maximum_output:
            console.run_command('move_to', {'to': 'eof', 'extend': False})

        # Set read only back again if necessary:
        #
        if is_read_only:
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
