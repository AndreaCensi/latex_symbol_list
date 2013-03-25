import re

# XXX: need to exclude '_'
command_pattern = r'(\\\w+)'
command_regex = re.compile(command_pattern)

def find_all_commands(filename):
    """ Finds all TeX commands used in the file. """
    commands = set()
    for line in open(filename):
        for x in command_regex.findall(line):
            commands.add(x)
    return commands


def find_all_commands_in_string(s):
    return command_regex.findall(s)
