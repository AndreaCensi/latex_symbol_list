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
           ]
        },
        install_requires=[],
        extras_require={},
)

