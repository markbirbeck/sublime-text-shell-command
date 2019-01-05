# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.17.0] - 2019-01-05
### Added
- Make the output of long-running tasks smoother. Closes #68. (@markbirbeck)
- Add support for history of commands. Closes #27. (@kaste)
- Support new syntax definition styles when using syntax option. Closes #74. (@gwenzek)

## [0.16.0] - 2016-02-26
### Added
- Allow the output of a command to overwrite the region used as input. Closes #9.

### Fixed
- Fixed problem where output buffers were always being set to read only. This is only relevant when writing to the buffer being edited. Fixes #51.

## [0.15.2] - 2016-02-05
### Fixed
Fixed problem where a failing configuration script would prevent any command from running. Fixes #50.

## [0.15.1] - 2015-03-11
### Fixed
- Fixed an additional scenario relating to issue #47, where generated views could have a CWD of `None`. Fixes #47.

## [0.15.0] - 2015-03-11

### Fixed
- Commands run from generated views no longer always have CWD of `None`. Fixes #47.
- `root_dir` is now working again. (@Stentor) Fixes #45.

## [0.14.0] - 2015-02-13
### Added
- Added option to allow the shell used to be overridden. Closes issue #32.

## [0.13.1] - 2015-02-13
### Added
- Added option to allow the end of a view to always be visible. Closes issue #39.

## [0.13.0] - 2015-02-12
### Changed
- The module has been renamed to `ShellCommand` in the package manager so this release simply applies the name change to documents, prompts, and file paths.

## [0.12.2] - 2015-02-12
### Added
- Add blank line before list in README. (@kleinfreund) Fixes issue #41.
- Provide method for running shell commands directly. (@markbirbeck) Fixes issue #42.
- Add reference to [Git Mode](https://github.com/markbirbeck/sublime-text-gitmode/) as an example of using `ShellCommand` to create modes. (@markbirbeck)

## [0.12.1] - 2015-01-01
### Added
- Add substitution variables that mirror those used in the ST build system. See [Build System Variables](http://docs.sublimetext.info/en/latest/reference/build_systems.html#build-system-variables) for the full list and description. Fixes issue #35.

## [0.12.0] - 2015-01-01
### Added
- Commands can now get parameters from users. Thanks to @aflc for providing the code for this functionality. Fixes issue #36.

## [0.11.1] - 2014-06-26
### Fixed
- The working directory is set to be the directory of the current file, but if the 'root' (deduced from the current file) is required, the option `root_dir` can be set to `True`. (@markbirbeck) Fixes issue #25.

## [0.11.0] - 2014-06-26
### Added
- Working directory selection is now much smarter, based on using the current file's path to find out which folder or project the file belongs to. (@bergtholdt) Fixes issue #17.
- The working directory is set to be the 'root' deduced from the current file, but if the directory of the current file is required, the option `root_dir` can be set to `False`. (@markbirbeck) Fixes issue #24.

### Changed
- `CR/LF` sequences are now mapped to `LF` which improves display on Windows. (@markbirbeck) Fixes issue #21.

### Fixed
- Commands were failing on Windows due to an unnecessary check that `stdout` was ready. (@markbirbeck) Fixes issue #13. Thanks to @bergtholdt who drew attention to the problem and proposed a slightly different solution.
- Menu entries that were supposed to provide access to settings and key bindings were opening the wrong files. (@markbirbeck) Fixes issue #22.
- A link to a wiki page from the README was incorrect. (@mrjoelkemp) Fixes issue #19 and #20. Thanks also to @reqshark who spotted the same problem and also provided a solution.

## [0.10.0] - 2014-03-20
### Fixed
- Passing a buffer with UTF-8 characters in as the stdin for a command caused the command to fail. (@markbirbeck) Fixes issue #16.

## [0.9.0] - 2014-03-15
### Fixed
- Commands were failing if run in a window with no open folders or files. (@mrvoss) Fixes issue #14.

## [0.8.0] - 2014-03-14
### Added
- Any text selected in the current buffer, or the entire buffer, can now be fed to a command as standard input, rather than as an argument. (@pcantrell) Fixes issue #5.

## [0.7.0] - 2014-03-11
### Added
- A shell configuration script can now be executed before commands. The script is either set in `$ENV` (as per `bash` conventions) or using the `shell_configuration_file` configuration setting. (@mikeerickson) Fixes issue #8.

## [0.6.0] - 2014-03-10
### Added
- The working directory is no longer derived primarily from the currently selected file. Instead any directory that has been saved in the view settings, or the project directory or the first open folder, is used. (@mikeerickson) Fixes issue #6.

## [0.5.0] - 2014-03-07
### Fixed
- If there is no output from a command then no panel or window is created. This used to work, until async commands were implemented, but now it really _does_ work. (@aldanor) Fixes issue #11.

## [0.4.0] - 2013-11-26
### Added
- Long-running commands will now update the buffer as and when data is available. For example, Grunt could be made to watch a project and update the buffer by running the command `grunt --no-color`. However, note that there is currently no way to terminate the process (see issue #10). Fixes issue #4.
- To change the default behaviour for long running commands, use the 'wait for completion' flag.

## [0.3.0] - 2013-10-07
### Added
- Add `shell_command_on_region` to align with Emacs version.

### Fixed
- Commands now *really are* run asynchronously. (@SirLenz0rlot)
  Fixes issue #2.

## [0.2.0] - 2013-10-07
### Added
- Some crucial text commands were not included (@bizoo).
  Fixes issue #1.

### Fixed
- The region under the cursor was not being used as a parameter.

## [0.1.0] - 2013-10-04
### Added
- Initial release.

[Unreleased]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.17.0...HEAD
[0.17.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.15.2...v0.16.0
[0.15.2]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.15.1...v0.15.2
[0.15.1]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.15.0...v0.15.1
[0.15.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.13.1...v0.14.0
[0.13.1]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.12.2...v0.13.0
[0.12.2]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.11.1...v0.12.0
[0.11.1]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/markbirbeck/sublime-text-shell-command/compare/...v0.1.0