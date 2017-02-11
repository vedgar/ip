from typing import Iterator
from tip import Token, Tokenizer, Parser, enum
from RI import *

class RI(enum.Enum):
    """Tipovi tokena za regularne izraze. Svaki specijalni znak ima token."""
    KRAJ, ZNAK, OTV, ZATV, ILI, PRAZAN, ZVIJEZDA = '$a()|/*'

def specijalan(znak: str) -> bool:
    """Vraća je li znak specijalan."""
    assert len(znak) == 1
    return znak in '()|/*'

def RI_lex(ri: str) -> Iterator[Token]:
    """Jednostavni lexer za regularne izraze."""
    lex = Tokenizer(ri)
    while True:
        znak = lex.čitaj()
        if znak is None:
            yield Token(RI.KRAJ, '')
            return
        elif specijalan(znak):
            yield Token(RI(znak), znak)
        else:
            yield Token(RI.ZNAK, znak)

# izraz -> član | član ILI izraz
# član -> faktor | faktor član
# faktor -> ZNAK | PRAZAN | OTV izraz ZATV | faktor ZVIJEZDA

class RIParser(Parser):
    """Ad hoc LL(1) parser za regularne izraze."""
    def izraz(self) -> RegularanIzraz:
        """Početni simbol."""
        prvi = self.član()
        sljedeći = self.granaj(RI.KRAJ, RI.ZATV, RI.ILI)
        if sljedeći == RI.ILI:
            self.pročitaj(RI.ILI)
            ostali = self.izraz()
            return Unija(prvi, ostali)
        return prvi

    def član(self):
        prvi = self.faktor()
        sljedeći = self.granaj(RI.KRAJ,RI.ZATV,RI.ILI,RI.OTV,RI.PRAZAN,RI.ZNAK)
        if sljedeći in {RI.OTV, RI.PRAZAN, RI.ZNAK}:
            ostali = self.član()
            return Konkatenacija(prvi, ostali)
        return prvi

    def faktor(self):
        prvi = self.granaj(RI.OTV, RI.PRAZAN, RI.ZNAK)
        if prvi == RI.OTV:
            self.pročitaj(RI.OTV)
            trenutni = self.izraz()
            self.pročitaj(RI.ZATV)
        elif prvi == RI.PRAZAN:
            self.pročitaj(RI.PRAZAN)
            trenutni = prazan
        else:
            token = self.pročitaj(RI.ZNAK)
            trenutni = Elementaran(token.sadržaj)
        while self.pogledaj().tip == RI.ZVIJEZDA:
            self.pročitaj(RI.ZVIJEZDA)
            trenutni = KleeneZvijezda(trenutni)
        return trenutni

def RI_parse(ri: str) -> RegularanIzraz:
    """Funkcija koja parsira regularni izraz."""
    parser = RIParser(RI_lex(ri))
    rezultat = parser.izraz()
    parser.pročitaj(RI.KRAJ)
    return rezultat

if __name__ == '__main__':
    print(*RI_lex(' )ab/|'), sep=',')
        # ZNAK' ',ZATV')',ZNAK'a',ZNAK'b',PRAZAN'/',ILI'|',KRAJ''
    assert RI_parse('0|1(0|1)*') == nula | jedan * -(nula | jedan)
    print(RI_parse('/*|b|cde'))  # (∅*|(b|(c(de))))
