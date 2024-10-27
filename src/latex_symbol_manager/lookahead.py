from collections.abc import Iterator

__all__ = [
    "Lookahead",
]


class Lookahead[X]:
    iter: Iterator[X]
    buffer: list[X]

    def __init__(self, iterator: Iterator[X]):
        self.iter = iterator
        self.buffer = []

    def __iter__(self) -> Iterator[X]:
        return self

    def __next__(self) -> X:  # @ReservedAssignment
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return next(self.iter)

    def lookahead(self, n: int) -> X | None:
        """Return an item n entries ahead in the iteration."""
        while n >= len(self.buffer):
            try:
                self.buffer.append(next(self.iter))
            except StopIteration:
                return None
        return self.buffer[n]
