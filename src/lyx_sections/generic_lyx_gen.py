from .misc_utils import wrap_script
from lyx_sections.generate_generic import generate_index
from lyx_sections.misc_utils import UserError
from optparse import OptionParser
from lyx_sections.generate_generic_templates import templates
 
def lyx_gen(args):

    parser = OptionParser()
    
    parser.add_option("-o", "--output", help="Output file")

    parser.add_option("-c", "--textclass", default='amsbook', help="LyX text class")

    parser.add_option("-p", "--pattern", help="File pattern",
                      default='*.lyx')
    
    parser.add_option("-P", "--preamble", help="Preamble section", default='')
    
    options, which = parser.parse_args(args[1:])
    
    if not options.output:
        msg = 'Please provide output argument with -o.'
        raise UserError(msg)
            
    if which:
        msg = 'Spurious arguments: %s' % which
        raise UserError(msg)


    template_main = templates[options.textclass]
    
    main = generate_index(
        pattern=options.pattern,
        template_main=template_main,
        entry2value=lambda x: '%s' % x,
        exclude=['chapter.lyx', 'chapter0.lyx', 'chapter_contents.lyx'],
        preamble=options.preamble)
    
    with open(options.output, 'wb') as f:
        f.write(main)

def lyx_gen_main():
    wrap_script(lyx_gen)
