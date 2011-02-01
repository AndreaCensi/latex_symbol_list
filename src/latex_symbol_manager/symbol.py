import yaml

class Symbol(yaml.YAMLObject):
    yaml_tag = u'!Symbol'
    
    def __init__(self, symbol, tex, tag=None, desc=None,
                 long=None, example=None, nargs=0, where=None):
        self.symbol = symbol
        self.tex = tex
        self.nargs = nargs
        self.desc = desc
        self.long = long
        self.example = example
        self.tag = tag
        self.where = where
    
    def __repr__(self):
        return ('Symbol(%r, %r, %r, %r, %r)' % 
            (self.symbol, self.tex, self.tag, self.nargs, self.example))
        
    def tex_definition(self):
        def single_def(cmd):
            if self.nargs:
                s = '\\newcommand{%s}[%s]{%s}' % (cmd, self.nargs, self.tex)
            else:    
                s = '\\newcommand{%s}{%s}' % (cmd, self.tex)
            return s

        if isinstance(self.symbol, list):
            s = "\n".join([ single_def(t) for t in self.symbol])
        else:
            s = single_def(self.symbol)
            
        if self.desc:
            s += '%% %s' % self.desc
            
        return s 
