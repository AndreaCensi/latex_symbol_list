from . import *

def generate_part_contents(args):
    generate(
        pattern='chap*', 
        entry2value=lambda x:'%s/chapter_contents.lyx' % x)


def generate_part_contents_main():
    wrap_script(generate_part_contents)
