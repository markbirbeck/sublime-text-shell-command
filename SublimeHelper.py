# Helper functions and classes to wrap common Sublime Text idioms:
#
import functools
import os

import sublime
import sublime_plugin


def main_thread(callback, *args, **kwargs):

    sublime.set_timeout_async(functools.partial(callback, *args, **kwargs), 0)


def error_message(*args, **kwargs):

    main_thread(sublime.error_message, *args, **kwargs)


class TextCommand(sublime_plugin.TextCommand):

    def get_region(self, view=None):
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

        if view is not None:

            # If there is a file in the active view then use it to work out
            # a working directory:
            #
            file_name = view.file_name()
            if file_name is not None:
                dirname, _ = os.path.split(os.path.abspath(file_name))
                return dirname

            window = view.window()
            if window is not None:

                # If there is a project file in the window then use it to work
                # out a working directory:
                #
                file_name = window.project_file_name()
                if file_name is not None:
                    dirname, _ = os.path.split(os.path.abspath(file_name))
                    return dirname

                # Alternatively, see if there are any open folders, and if so, use the
                # path of the first one:
                #
                folders = window.folders()
                if folders is not None:
                    return folders[0]

        return ''


# The command that is executed to insert text into a view:
#
class SublimeHelperInsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, pos, msg):

        self.view.insert(edit, pos, msg)


# The command that is executed to erase text into a view:
#
class SublimeHelperEraseTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, a, b):

        self.view.erase(edit, sublime.Region(a, b))
