# Introduction

The `ShellCommand` plugin allows OS shell commands to be run and their output to be sent to buffers or panels.

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
