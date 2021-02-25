from collections import namedtuple

NO_SUMMARY = 'nosummary'

NO_INLINE = 'no-inline'
NOMENC = 'nomenc'
NOMENC_EXCLUDE = 'nomenc-exclude'
TODO = "todo"
SEE_ALSO = 'def'
SORT = 'def'
NOT_FINAL = 'notfinal'
DEPRECATED = 'deprecated'
EXAMPLE = 'example'
KNOWN_TAGS_SYMBOLS = [
    SEE_ALSO,
    NOMENC,
    NOMENC_EXCLUDE,
    NO_SUMMARY,
    SORT,
    EXAMPLE, DEPRECATED, NOT_FINAL,
    TODO,
    NO_INLINE,
]
KNOWN_TAGS_SECTIONS = [NOMENC_EXCLUDE, NOT_FINAL, DEPRECATED]

# These are the possible results of parsing a tex file
NewCommand = namedtuple("NewCommand", "command nargs body comment where")
SpecialComment = namedtuple("SpecialComment", "tag lines where")
OtherLine = namedtuple("OtherLine", "line where")

SymbolSection = namedtuple(
    "SymbolSection",
    "name description symbols parent subs where definition_order attrs",
)


class Where:
    def __init__(self, filename, lineno, text=None):
        self.filename = filename
        self.lineno = lineno
        if text and text[-1] == "\n":
            text = text[:-1]
        self.text = text

    def __str__(self):
        return "%s: line %4d: %s" % (self.filename, self.lineno, self.text)

    def __repr__(self):
        return "Where(%s,%s)" % (self.filename, self.lineno)


class ParsingError(Exception):
    def __init__(self, error, where):
        self.error = error
        self.where = where

    def __str__(self):
        return "%s\n%s" % (self.error, self.where)
