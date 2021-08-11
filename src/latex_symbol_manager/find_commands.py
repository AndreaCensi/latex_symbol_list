import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

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
    for a, line in enumerate(open(filename)):
        if "%" in line:
            i = line.index("%")
            line = line[:i]

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
