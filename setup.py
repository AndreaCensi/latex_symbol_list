from setuptools import setup, find_packages

setup(name='LatexSymbolManager',
        author="Andrea Censi",
        author_email="andrea@cds.caltech.edu",
        version="0.5",
        package_dir={'':'src'},
        packages=find_packages('src'),
        entry_points={
         'console_scripts': [
           'lsm_test1 = latex_symbol_manager.parsing:main',
           'lsm_test2 = latex_symbol_manager.parsing_structure:main',
           'lsm_table = latex_symbol_manager.create_symbols_table:main',
           'lsm_symbols = latex_symbol_manager.compact_all:main',
           'lsm_extract = latex_symbol_manager.programs:lsm_extract_main',
           #'lsm_select = latex_symbol_manager.programs.select_subset:main',
           'lsm_nomenc = latex_symbol_manager.programs.nomenc:main',
           'lsm_collect = latex_symbol_manager.programs.collect.collect:main',

           # Depednencies
           'tex-deps = latex_deps.tex_deps:tex_deps_main',
           'tex-deps-all = latex_deps.tex_deps_all:tex_deps_all_main',
           'lyx-deps = latex_deps.lyx_deps:lyx_deps_main',
           'lyx-deps-all = latex_deps.lyx_deps_all:lyx_deps_all_main',

           # Summaries
           'lyx-gen-chapter = lyx_sections:generate_chapter_contents_main',
           'lyx-gen-part  = lyx_sections:generate_part_contents_main',
           'lyx-gen  = lyx_sections:lyx_gen_main',
           ]
        },
        install_requires=['LaTeXGen', 'pyyaml'],
        extras_require={},
)

