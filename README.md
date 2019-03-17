# Introduction

The `ShellCommand` plugin allows arbitrary shell commands to be run and their output to be sent to buffers or panels.

It can:

* run pretty much any shell command, either typed into a prompt or configured in key bindings and commands;
* the output from a command is directable to either a new buffer or a panel;
* subsequent commands can cause other panels to re-run their commands, i.e., to 'refresh' themselves;
* the output of a shell command can be controlled by any syntax definition.

These features can be combined together to create apps or *modes*. To see a full example of how this can be done, see the [Git Mode](https://packagecontrol.io/packages/Git%20Mode) plugin, which provides an interface to Git, entirely implemented using key bindings, syntax definitions and calls to `ShellCommand`.

# Motivation

Whilst working on a number of Emacs-style extensions for Sublime it became clear that much of the functionality of extensions such as `dired` and `magit` required little more than the ability to move from one buffer to another, invoking commands based on context on the way.

For example, `dired` shows a list of files and directories, and then allows users to interact with those files by selecting items in the buffer and pressing some key combinations. This way files and directories can be opened, renamed, deleted, zipped up, compared, and so on.

Similarly, the incredibly useful `magit` firstly shows the status of a Git repo and then allows files to be staged, unstaged, committed and diffed, whilst branches can be switched between, rebased, merged, pushed, pulled and more.

So this extension is the factoring out of the core functionality on top of which tools like `dired` and `magit` can be built. A Sublime-style version of `magit` should be available shortly.

# Installation

The package is available on [Package Control](https://sublime.wbond.net/).

# Key bindings

The built-in bindings are based on similar functionality for Emacs (see [Execute External Command](http://www.emacswiki.org/emacs/ExecuteExternalCommand)):

* `alt+!` will show a prompt into which a shell command can be typed;
* `alt+|` will also show a prompt, but will use any selections or text under the cursor (or the current file if nothing is selected) as standard input to the shell command (i.e., `stdin`);
* `ctrl+alt+!` will do the same as `alt+!` but instead of sending the result to a new buffer, the result will be placed in the current document at the cursor position;
* `ctrl+alt+|` will do the same as `alt+|` but instead of sending the result to a new buffer, the result will overwrite the selected text in the current document (i.e., the text that was used as input to the command);
* `g` in a view that is showing the output of a shell command will cause the command to be run again.

In addition to this it's possible to customise the behaviour for many different scenarios.

# Shell Configuration Files

For detailed information about using your shell configuration options see [Using a Shell Configuration File](../../wiki/Using-a-Shell-Configuration-File).

# Commands

There is one command provided in the Command Pallette, which is `ShellCommand`. This provides a prompt into which a shell command can be entered. Any selections in the active view will be fed to the command as standard input. If there are no selections then the entire buffer will be passed through.

# Configuration Settings

NOTE: Some variable names have hyphens and some underscores. This is because I'm still uncertain about how much to align with the Emacs functionality that this module is based on.

## comint-scroll-show-maximum-output

If comint-scroll-show-maximum-output is `True`, then scrolling due to arrival of output tries to place the last line of text at the bottom line of the window, so as to show as much useful text as possible. (This mimics the scrolling behavior of many terminals.) The default is `False`.

## shell-file-name

`shell-file-name` provides the name of the shell to use when executing commands. If this value is not set then either the `SHELL` or `COMSPEC` environment variable is used, depending on whether Sublime Text is running on a Posix or Windows system. If none of these is set then the behaviour is defined by `subprocess.Popen()`.

## show_success_but_no_output_message

Indicates whether to show a message when the shell command returns no output, or the output is just whitespace. The default value is `False`, i.e., no window is created if the command doesn't return anything.

## success_but_no_output_message

This is the message to show in the window or panel if the `show_success_but_no_output_message` value is set to `True`. The default value copies the equivalent from Emacs, i.e., "Shell command succeeded with no output".

# Examples

Note that the following key bindings are for illustrative purposes only.

## Prompt for a command on `ctrl+enter`

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command"
  }
]
```

This is the most basic use of the plugin, and will result in a prompt being provided to the user, into which any string can be typed. On pressing `[ENTER]` the string will be processed as a shell command and the output will be rendered in a new view. The buffer in the view is read only.

## Change the prompt caption and the output window title

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "prompt": "Enter a command",
      "title": "My Command"
    }
  }
]
```

Using these arguments the caption next to the prompt can be changed, as well as the title of the output view.

## Capturing output in a panel

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "prompt": "Enter a command",
      "title": "My Command",
      "panel": true
    }
  }
]
```

Often the output of a command is only required for a short amount of time, in which case a panel might be more appropriate.

## Capturing output in the current buffer

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "prompt": "Enter a command",
      "title": "My Command",
      "target": "point"
    }
  }
]
```

Sometimes the output of a command should be inserted into the document being edited. Setting the `target` argument to `point` achieves this. If there is a region selected then this is overwritten.

## Run a specific command

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git status"
    }
  }
]
```

To run a particular shell command use the `command` parameter.

## Prompt the user for parameters

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git checkout -b feature/${branch::Feature Branch} develop"
    }
  }
]
```

The `branch` variable has a prompt (the string 'Feature Branch'), so the user is asked to provide its value.

If a default value is provided (the second value after the variable name) then this will be placed into the prompt:
```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git checkout -b feature/${branch:new feature:Feature Branch} develop"
    }
  }
]
```

## Predefined variables


There are a number of predefined variables that you can pass to command (eg. current file name, project dir etc.).

|Variable|Value example|
|---|---|
|${file}|/var/www/index.html|
|${file_path}|/var/www|
|${file_name}|index.html|
|${file_extension}|.html|
|${file_base_name}|index|
|${packages}|/home/andrew/.config/sublime-text-3/Packages|
|${project}|/var/www/my-project.sublime-project|
|${project_path}|/var/www|
|${project_name}|my-project.sublime-project|
|${project_extension}|.sublime-project|
|${project_base_name}|my-project|
|${project_folders}|/var/www|

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "cat ${file}"
    }
  }
]
```

## Use cursor selection for input

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "ls -al",
      "region": "arg"
    }
  }
]
```

If the `region` option is set to 'arg' then any active selections are appended to the command as arguments. If there are no active selections then the word under the cursor is used. In this example if there were no selections, and no word under the cursor then the `ls -al` command would be run as is, most likely giving the contents of the project directory. But if a directory name were under the cursor, or was selected, then its contents would be listed.

```json
[
  {
    "caption": "Word Count",
    "command": "shell_command",
    "args": {
      "command": "wc -w",
      "region": "stdin"
    }
  }
]
```

If the `region` option is set to 'stdin' then any active selections are piped to the command as standard input (stdin). If there are no active selections then the entire buffer is used. In this example if there were no selections, and no word under the cursor then the `wc -w` command would count the number of words in the current buffer.

## Providing a common command prefix

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command_prefix": "git",
      "prompt": "Git Command"
    }
  }
]
```

Sometimes it's useful to provide a command prompt that relates to a specific shell command, and the user would then only need to provide the parameters. This example creates a prompt labelled 'Git Command', into which the user need only type the Git command itself, and any parameters. For example, to run `git status`, only `status` would need to be entered into the prompt.

## Feeding a string of text to a command

```json
[
  {
    "caption": "Word Count",
    "command": "shell_command",
    "args": {
      "stdin": "A contrived example. The output should be 8",
      "command": "wc -w"
    }
  }
]
```

To pass a string of text to a command use the `stdin` argument.

## Applying a syntax definition to the output

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git diff",
      "syntax": "Diff",
      "title": "Diff"
    },
  }
]
```

This will run `git diff` against whatever file is selected, and then use the `Diff` syntax file (`Packages/Diff/Diff.sublime-syntax`) to format the output.

The value of the `syntax` property can be a full path to a syntax file, a file name without a path, but with a file extension, or a syntax name without a file extension (as in the above example). If the value specified is not found when treated as a path then `ShellCommand` will append a suffix of `.sublime-syntax` and try again. If there is still no match, a suffix of `.tmLanguage` will be tried, before finally, an error is reported.

## Restricting key bindings to a shell command view

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git diff",
      "syntax": "Diff",
      "title": "Diff"
    },
    "context": [{ "key": "setting.ShellCommand" }]
  }
]
```

This is the same command as before -- running `git diff` on the file that the cursor is pointing at -- but this time the command will only work if the view is a `ShellCommand` window.

## Refreshing the current view

If a shell command is executed whilst in the context of the output of another shell command and the action would affect the first view, then a refresh can be sent after the command has run. This uses the `refresh` argument. For example, say a view contains a listing of the working directory created with the following shell command:

```json
[
  {
    "keys": ["ctrl+enter", "1"],
    "command": "shell_command",
    "args": {
      "command": "ls -al"
    }
  }
]
```

If we then have two further shell commands -- one that creates a new file, and one that deletes the file whose name is under the cursor -- we would want to ensure that the `ls` view updates after either of these commands is run. The settings for the two add and delete commands might look like this:

```json
[
  {
    "keys": ["ctrl+enter", "2"],
    "command": "shell_command",
    "args": {
      "command": "cp README.md tmp",
      "refresh": true
    }
  },
  {
    "keys": ["ctrl+enter", "3"],
    "command": "shell_command",
    "args": {
      "command": "rm",
      "arg_required": true,
      "region": "arg",
      "refresh": true
    }
  },
]
```

## Whether to wait for the command to complete

By default long-running commands will update the buffer as and when data is available. For some short commands this can look a little jerky and it might be best to wait for the command to complete before updating the buffer. This can be achieved with the 'wait for completion' flag:

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "wait_for_completion": true
    }
  }
]
```

# Changelog

Moved to [CHANGELOG](./CHANGELOG.md).
