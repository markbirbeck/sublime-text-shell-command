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

def find_defined_value(item, view):
    window = view.window()

    if item == 'project_folders':
        return ' '.join(window.folders() or [])
    elif item == 'project_name':
        project_path = window.project_file_name()
        if not project_path:
            return ''
        return os.path.basename(project_path).replace('.sublime-project', '')
