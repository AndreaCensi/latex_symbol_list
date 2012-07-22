from . import * 

def generate_chapter_contents(args):
    generate(
        pattern='*.lyx', 
        entry2value=lambda x:'%s' % x,
        exclude=['chapter.lyx', 'chapter0.lyx', 'chapter_contents.lyx'])

def generate_chapter_contents_main():
    wrap_script(generate_chapter_contents)
