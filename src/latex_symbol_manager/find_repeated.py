import re
import sys
from collections import defaultdict
from typing import Dict, Set


def main():
    data = sys.stdin.read()
    MAX_LEN = 30
    MIN_LEN = 10

    found = defaultdict(lambda: 0)

    def process(i: int):
        for l in range(MIN_LEN, MAX_LEN):
            s = data[i : i + l]
            s = s.replace(" ", "")
            s = s.replace("\n", "")
            if (
                s.startswith("\\begin")
                or s.startswith("\\end")
                or s.startswith("\\\\")
                or s.startswith("\\input")
                or s.startswith("\\\\")
            ):
                continue

            balanced = (s.count("{") == s.count("}")) and (s.count("(") == s.count(")")) and (s.count("[") == s.count("]"))
            if not balanced:
                continue
            if len(s) >= MIN_LEN:
                found[s] += 1

    for m in re.finditer("\\\\", data):
        process(m.start())

    len_found: Dict[int, Set[str]] = defaultdict(set)
    for k, v in found.items():
        len_found[v].add(k)

    MIN_REP = 15

    found_frequent: Set[str] = set()
    for k, v in len_found.items():
        if k > MIN_REP:
            found_frequent.update(v)

    def bigger_found(s):
        return any(_.startswith(s) and _ != s for _ in found_frequent)

    toshow = []
    for k, v in len_found.items():
        for w in v:
            if w in found_frequent and not bigger_found(w):
                toshow.append((k, w))

    toshow = sorted(toshow, reverse=True)
    for k, v in toshow:
        print(f"{k:4d} {v}")

    # print(dict(sorted(len_found.items())))


if __name__ == "__main__":
    main()
