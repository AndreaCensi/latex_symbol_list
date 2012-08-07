from . import generate
from .misc_utils import wrap_script

def generate_chapter_contents(args): #@UnusedVariable
    generate(
        pattern='*.lyx', 
        entry2value=lambda x: '%s' % x,
        exclude=['chapter.lyx', 'chapter0.lyx', 'chapter_contents.lyx'])

def generate_chapter_contents_main():
    wrap_script(generate_chapter_contents)
