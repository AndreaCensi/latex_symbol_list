import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

from zuper_commons.fs import read_ustring_from_utf8_file
from zuper_commons.text import remove_hash_comments

from . import logger

command_pattern = r"(\\[a-zA-Z]+)"  # XXX: need to exclude '_'
command_regex = re.compile(command_pattern)

label_pattern = r"\\label{([^}]*)}"
label_regex = re.compile(label_pattern)


@dataclass
class Usage:
    filename: str
    line: int
    last_label: Optional[str]


def find_all_commands(filename: str) -> Dict[str, List[Usage]]:
    """ Finds all TeX commands used in the file. """
    commands: Dict[str, List[Usage]] = defaultdict(list)
    found = set()
    last_label = None
    data = read_ustring_from_utf8_file(filename)
    logger.info(f'Processing {filename}')
    remove = [
        ('\\begin{forslides}', '\\end{forslides}'),
        ('\\begin{comment}', '\\end{comment}'),
    ]
    data = remove_hash_comments(data, remove_empty_lines=False, comment_char='%')
    while True:
        changes = 0
        for start, stop in remove:

            if start in data:
                i = data.index(start)
                after = data[i:]
                n = after.index(stop)

                data = data[:i] + data[i + n + len(stop):]
                changes += 1
                break

        if changes == 0:
            break
    lines = data.split('\n')
    for a, line in enumerate(lines):
        # if "%" in line:
        #     i = line.index("%")
        #     line = line[:i]

        for y in label_regex.findall(line):
            last_label = y
            assert '}' not in last_label, last_label
            assert '{' not in last_label, last_label

        for x in command_regex.findall(line):
            if x not in found:
                commands[x].append(Usage(filename, a, last_label))
            if last_label is not None:
                found.add(x)
    return dict(commands)


def find_all_commands_in_string(s: str) -> List[str]:
    return list(command_regex.findall(s))
