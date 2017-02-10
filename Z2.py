from tip import Token, Tokenizer, Parser, enum
from RI import *

def specijalan(znak: str) -> bool:
    """Vraća je li znak specijalan."""
    assert len(znak) == 1
    ...

class RI(enum.Enum):
    """Tipovi tokena za regularne izraze."""
    ...

def RI_lex(ri: str):
    """Jednostavni lexer za regularne izraze."""
    ..., (yield Token(...))

# izraz -> ...  # Gramatiku napišite ovdje.

class RIParser(Parser):
    """Ad hoc LL(1) parser za regularne izraze."""
    def izraz(self) -> RegularanIzraz:
        ...
    ...

def RI_parse(ri: str) -> RegularanIzraz:
    """Funkcija koja parsira regularni izraz."""
    parser = RIParser(RI_lex(ri))
    rezultat = parser.izraz()
    parser.pročitaj(RI.KRAJ)
    return rezultat

if __name__ == '__main__':
    print(*RI_lex(' )a|'), sep=',')  # ZNAK' ',ZATV')',ZNAK'a',ILI'|',KRAJ''
    assert RI_parse('0|1(0|1)*') == nula | jedan * -(nula | jedan)
    print(RI_parse('/*|b|cde'))  # npr. (∅*|(b|(c(de))))
