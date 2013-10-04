# Introduction

The `ShellCommand` plugin allows OS shell commands to be run and their output to be sent to buffers or panels.

It can:
* run pretty much any shell command, either typed into a prompt or configured in key bindings and commands;
* the output from a command is directable to either a new buffer or a panel;
* subsequent commands can cause other panels to re-run their commands, i.e., to 'refresh' themselves;
* the output of a shell command can be controlled by any syntax definition.

# Motivation

Whilst working on a number of Emacs-style extensions for Sublime it became clear that much of the functionality of extensions such as `dired` and `magit` required little more than the ability to move from one buffer to another, invoking commands based on context on the way.

For example, `dired` shows a list of files and directories, and then allows users to interact with those files by selecting items in the buffer and pressing some key combinations. This way files and directories can be opened, renamed, deleted, zipped up, compared, and so on.

Similarly, the incredibly useful `magit` firstly shows the status of a Git repo and then allows files to be staged, unstaged, committed and diffed, whilst branches can be switched between, rebased, merged, pushed, pulled and more.

So this extension is the factoring out of the core functionality on top of which tools like `dired` and `magit` can be built. A Sublime-style version of `magit` should be availble shortly.

# Installation

The package is available on [Package Control](https://sublime.wbond.net/).

# Key bindings

The built-in bindings are based on similar functionality for Emacs:

* `alt+!` will show a prompt into which a shell command can be typed;
* `alt+|` will use any selections or text under the cursor as input for a shell command;
* `g` in a view that is showing the output of a shell command will cause the command to be run again.

In addition to this it's possible to customise the behaviour for many different scenarios.

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

This is the most basic use of the plugin, and will result in a prompt being provided to the user, into which any string can be typed. On pressing `[ENTER]` the string will be processed as a command and the output will be rendered in a new view. The buffer in the view is read only.

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

## Use cursor selection for input

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "ls -al",
      "region": true
    }
  }
]
```

If the `region` option is set then any active selections are appended to the command. If there are no active selections then the word under the cursor is used. In this example if there were no selections, and no word under the cursor then the `ls -al` command would be run as is, most likely giving the contents of the project directory. But if a directory name were under the cursor, or was selected, then its contents would be listed.

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

## Applying a syntax definition to the output

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git diff",
      "region": true,
      "syntax": "Diff",
      "title": "Diff"
    },
  }
]
```

This will run `git diff` against whatever file is selected, and then use the `Diff` syntax file (`Packages/Diff/Diff.tmLanguage`) to format the output.

## Restricting key bindings to a shell command view

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "shell_command",
    "args": {
      "command": "git diff",
      "region": true,
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
      "region": true,
      "refresh": true
    }
  },
]
```

# Changelog

2013-10-04 (v0.1.0)

* Initial release.
