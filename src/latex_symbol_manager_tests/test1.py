s = r"""

\newcommand{\stain}[1]{
\scalebox{0.1}{
\begin{tikzpicture}[use Hobby shortcut,closed=true]
      \draw[fill=#1,thick](-2.5,-0.5).. (-3.5,0).. (-2.5,0.5).. (-3,1).. (-2,1.5).. (-2,3).. (-1,2.5).. (1,4.5).. (2.5,3).. (3,3.5).. (3.5,3).. (3,2).. (4.5,2).. (4.5,0).. (3,1).. (2.5,-0.5).. (3.5,-1.5).. (1.5,-1).. (0.5,-2).. (-2,-2.5).. (-1.5,-1).. (-2.5,-1.5).. (-2.5,-0.5);
\end{tikzpicture}}}

"""


def test1():
    from latex_symbol_manager import logger

    _ = logger
    pass
