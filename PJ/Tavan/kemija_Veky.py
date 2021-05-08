from pj import *
from backend import referentne_atomske_mase
import collections


class T(TipoviTokena):
    OOTV, OZATV, UOTV, UZATV = '()[]'

    class N(Token):
        literal = 'n'
        def vrijednost(self, tablica): return tablica[self]

    class ATOM(Token):
        def masa(self, tablica): return tablica[self]

    class BROJ(Token):
        def vrijednost(self, tablica): return int(self.sadržaj)


def kemija(lex):
    možeN = False
    for znak in lex:
        if znak == 'n':
            if možeN: yield lex.token(T.N)
            else: raise lex.greška('n ne može doći ovdje')
        elif znak.isdecimal():
            lex.prirodni_broj(znak, nula=False)
            yield lex.token(T.BROJ)
        elif znak.isupper():
            if not lex.čitaj().islower(): lex.vrati()
            yield lex.token(T.ATOM)
        else:
            yield lex.literal(T)
        možeN = znak in '])'


### BKG
# formula -> skupina | skupina formula
# skupina -> ATOM | ATOM BROJ | zagrade | zagrade BROJ | zagrade N
# zagrade -> OOTV formula OZATV | UOTV formula UZATV


class spoj(Parser):
    def formula(self):
        l = [self.skupina()]
        while self >= {T.ATOM, T.OOTV, T.UOTV}: l.append(self.skupina())
        return Formula(l)

    def skupina(self):
        if self >> T.OOTV:
            što = self.formula()
            self.pročitaj(T.OZATV)
        elif self >> T.UOTV:
            što = self.formula()
            self.pročitaj(T.UZATV)
        else: što = self.pročitaj(T.ATOM)
        return Skupina(što, self >> {T.BROJ, T.N} or nenavedeno)

    lexer = kemija
    start = formula


### AST
# Formula: skupine:[Skupina]
# Skupina: čega:ATOM|Formula koliko:(BROJ|N)?


class Formula(AST('skupine')):
    def masa(self, tablica): return sum(s.ukupno(tablica) for s in self.skupine)

    def Mr(self, **mase):
        spojeno = collections.ChainMap(mase, referentne_atomske_mase)
        return self.masa(Memorija(spojeno))


class Skupina(AST('čega koliko')):
    def ukupno(self, tablica):
        m = self.čega.masa(tablica)
        if self.koliko: m *= self.koliko.vrijednost(tablica)
        return m


natrijev_trikarbonatokobaltat = spoj('Na3[Co(CO3)3]')
prikaz(natrijev_trikarbonatokobaltat)
for krivo in 'SnABcdefG', 'O Be', 'Es(n)':
    with očekivano(LeksičkaGreška): spoj.tokeniziraj(krivo)
    print()
spoj.tokeniziraj(']nB')
print(spoj('CH3(CH2)nCH3').Mr(n=2))
