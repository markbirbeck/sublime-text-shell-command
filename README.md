# Introduction

The `OsCommand` plugin allows OS shell commands to be run and their output to be sent to buffers or panels.

# Examples

Note that the following key bindings are for illustrative purposes only.

## Prompt for a command on `ctrl+enter`

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "os_command"
  }
]
```

This is the most basic use of the plugin, and will result in a prompt being provided to the user, into which any string can be typed. On pressing `[ENTER]` the string will be processed as a command and the output will be rendered in a new view. The buffer in the view is read only.

## Change the prompt caption and the output window title

```json
[
  {
    "keys": ["ctrl+enter"],
    "command": "os_command",
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
    "command": "os_command",
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
    "command": "os_command",
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
    "command": "os_command",
    "args": {
      "command": "ls -al",
      "selections": true
    }
  }
]
```

If the `selections` option is set then any active selections are appended to the command. If there are no active selections then the word under the cursor is used. In this example if there were no selections, and no word under the cursor then the `ls -al` command would be run as is, most likely giving the contents of the project directory. But if a directory name were under the cursor, or was selected, then its contents would be listed.
