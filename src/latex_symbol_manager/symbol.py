import yaml


class NomenclatureEntry(yaml.YAMLObject):
    def __init__(self, label, text):
        self.label = label
        self.text = text

    def __repr__(self):
        return ('Nom(%r, %r)' % (self.label, self.text))


class Symbol(yaml.YAMLObject):
    yaml_tag = u'!Symbol'

    def __init__(self, symbol, tex, definition_order, tag=None, desc=None,
                 long=None, example=None, nargs=0, #@ReservedAssignment
                  where=None, nomenclature=None, other={}):
        self.symbol = symbol
        self.tex = tex
        self.definition_order = definition_order
        self.nargs = nargs
        self.desc = desc
        self.long = long
        self.example = example
        self.tag = tag
        self.where = where
        self.nomenclature = nomenclature
        self.other = other

    def __repr__(self):
        return ('Symbol(%r, %r, %r, %r, %r, %r, %r)' %
            (self.symbol, self.tex, self.tag, self.nargs, self.example,
             self.nomenclature, self.other))

    def tex_definition(self, wrapper=None):
        if wrapper is None:
            tex = self.tex
        else:
            tex = wrapper(self.tex)

        def single_def(cmd):

            if self.nargs:
                params = '{%s}[%s]{%s}' % (cmd, self.nargs, tex)
            else:
                params = '{%s}{%s}' % (cmd, tex)

            s = ('\\ifdefined%s%%\n  \\renewcommand%s%%\n\\else%%\n  '
                 '\\newcommand%s%%\n\\fi\n' % (cmd, params, params))
            return s

        if isinstance(self.symbol, list):
            s = "\n".join([single_def(t) for t in self.symbol])
        else:
            s = single_def(self.symbol)

        if self.desc:
            s += '%% %s' % self.desc

        return s
