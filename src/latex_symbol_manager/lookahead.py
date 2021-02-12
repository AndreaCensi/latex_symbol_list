class Lookahead:
    def __init__(self, iterator):
        self.iter = iterator
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):  # @ReservedAssignment
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return next(self.iter)

    def lookahead(self, n):
        """Return an item n entries ahead in the iteration."""
        while n >= len(self.buffer):
            try:
                self.buffer.append(next(self.iter))
            except StopIteration:
                return None
        return self.buffer[n]
