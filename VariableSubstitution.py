def parse_command(command, view):
    ''' Inspired by Sublime's snippet syntax; "${...}" is a variable.
    But it's slightly different, ${<variable_name>[:[default value][:<Prompt message if not exist>]]}
    EX) git branch -m ${current_branch} ${new_branch::Enter branch name}
    '''
    import re

    parsed = re.split(r'\${(.*?)}', command)
    # if not variables, return command itself
    if len(parsed) == 1:
        return [], command
    template_parts = []
    asks = []
    for idx, item in enumerate(parsed, start=1):
        # variable
        auto_variable = 0
        if idx % 2 == 0:
            chs = item.split(':')
            variable_name = chs[0]
            if not variable_name:
                variable_name = '_' + str(auto_variable)
                auto_variable += 1
            v = find_defined_value(variable_name, view)
            if v:
                template_parts.append(v)
                continue

            # If the defined variable is not found then either use the default
            # value...
            #
            if len(chs) == 2:
                template_parts.append(chs[1])
                continue

            # ...or start prompting:
            #
            if len(chs) < 3:
                prompt_message = variable_name
                default_value = ''
            else:
                prompt_message = chs[2]
                default_value = chs[1]
            asks.append(dict(variable=variable_name, message=prompt_message, default=default_value))
            template_parts.append('{%s}' % variable_name)
        else:
            template_parts.append(item)
    return asks, ''.join(template_parts)

def file_name_split(file):
    import os

    if file is None:
        file = ''

    # The directory of the current file, e.g., C:\Files:
    #
    path = os.path.dirname(file)

    # The name portion of the current file, e.g., Chapter1.txt:
    #
    name = os.path.basename(file)

    # The extension portion of the current file, e.g., txt:
    #
    tmp, ext = os.path.splitext(file)

    # The name-only portion of the current file, e.g., Document:
    #
    base_name = os.path.basename(tmp)

    return file, path, name, ext, base_name

def find_defined_value(item, view):
    import os
    import sublime

    window = view.window()
    vars = {}

    # Build system variables:
    #
    # See http://docs.sublimetext.info/en/latest/reference/build_systems.html#build-system-variables
    #
    vars['file'], vars['file_path'], vars['file_name'], vars['file_extension'], vars['file_base_name'] = file_name_split(view.file_name())
    vars['packages'] = sublime.packages_path()
    vars['project'], vars['project_path'], vars['project_name'], vars['project_extension'], vars['project_base_name'] = file_name_split(window.project_file_name())

    # Others:
    #
    vars['project_folders'] = ' '.join(window.folders() or [])

    if item in vars:
        return vars[item]
