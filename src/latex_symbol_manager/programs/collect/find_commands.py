import re


def find_all_commands(filename):
    """ Finds all TeX commands used in the file. """
    command_pattern = r'(\\\w+)'
    regex = re.compile(command_pattern)
    commands = set()
    for line in open(filename):
        for x in regex.findall(line):
            commands.add(x)
    return commands
