# 2010 K2 Z1,Z2

from pj import *


class LJ(enum.Enum):
    LISTA, PRAZNA, UBACI = 'lista', 'prazna', 'ubaci'
    IZBACI, DOHVATI, KOLIKO = 'izbaci', 'dohvati', 'koliko'
    class ID(Token):
        def ref(self, mem): return pogledaj(mem, self)
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class MINUSBROJ(Token): """Negativni broj."""


def lj_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak == 'L':
            if '1' <= lex.čitaj() <= '9': yield lex.token(LJ.ID)
            else: lex.greška('očekivana znamenka između 1 i 9')
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.literal(LJ, case=False)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(LJ.BROJ)
        elif znak == '-':
            lex.plus(str.isdigit)
            yield lex.token(LJ.MINUSBROJ)
        else: raise lex.greška()


### Beskontekstna gramatika
# start -> naredba start | ε
# naredba -> deklaracija | provjera | ubaci | izbaci | dohvati | duljina
# deklaracija -> LISTA ID
# provjera -> PRAZNA ID
# ubaci -> UBACI ID ( BROJ | MINUSBROJ ) BROJ
# izbaci -> IZBACI ID BROJ
# dohvati -> DOHVATI ID BROJ
# duljina -> KOLIKO ID

### Apstraktna sintaksna stabla
# Program: naredbe
# Deklaracija: lista
# Provjera: lista
# Ubaci: lista vrijednost indeks
# Izbaci: lista indeks
# Dohvati: lista indeks
# Duljina: lista

class LJParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> LJ.LISTA: return Deklaracija(self.pročitaj(LJ.ID))
        elif self >> LJ.PRAZNA: return Provjera(self.pročitaj(LJ.ID))
        elif self >> LJ.UBACI: return Ubaci(self.pročitaj(LJ.ID),
            self.pročitaj(LJ.BROJ, LJ.MINUSBROJ), self.pročitaj(LJ.BROJ))
        elif self >> LJ.IZBACI:
            return Izbaci(self.pročitaj(LJ.ID), self.pročitaj(LJ.BROJ))
        elif self >> LJ.DOHVATI:
            return Dohvati(self.pročitaj(LJ.ID), self.pročitaj(LJ.BROJ))
        elif self >> LJ.KOLIKO: return Duljina(self.pročitaj(LJ.ID))
        else: self.greška()


class Program(AST('naredbe')):
    """Program u jeziku listâ."""
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe:
            izlaz = naredba.izvrši(memorija)
            if izlaz is not None: yield izlaz
    
class Deklaracija(AST('lista')):
    """Deklaracija liste."""
    def izvrši(self, memorija):
        l = self.lista.sadržaj
        if l in memorija: raise SemantičkaGreška('Redeklaracija: ' + l)
        memorija[l] = []

class Provjera(AST('lista')):
    """Je li lista prazna?"""
    def izvrši(self, memorija): return not self.lista.ref(memorija)

class Duljina(AST('lista')):
    """Broj elemenata u listi."""
    def izvrši(self, memorija): return len(self.lista.ref(memorija))

class Dohvati(AST('lista indeks')):
    """Element zadanog indeksa (brojeći od 0). Prevelik indeks javlja grešku."""
    def izvrši(self, memorija):
        l = self.lista.ref(memorija)
        i = self.indeks.vrijednost()
        if i < len(l): return l[i]
        else: raise self.indeks.problem('Prevelik indeks')
        
class Izbaci(AST('lista indeks')):
    """Izbacuje element zadanog indeksa iz liste ili javlja grešku izvođenja."""
    def izvrši(self, memorija):
        l = self.lista.ref(memorija)
        i = self.indeks.vrijednost()
        if i < len(l): del l[i]
        else: raise self.indeks.problem('Prevelik indeks')

class Ubaci(AST('lista element indeks')):
    """Ubacuje vrijednost u listu na zadanom indeksu, ili javlja grešku."""
    def izvrši(self, memorija):
        l = self.lista.ref(memorija)
        i = self.indeks.vrijednost()
        if i <= len(l): l.insert(i, self.element.vrijednost())
        else: raise self.indeks.problem('Prevelik indeks')


def rezultati(lj_program):
    print(*LJParser.parsiraj(lj_lex(lj_program)).izvrši())

if __name__ == '__main__':
    print(*lj_lex('lista L1 prazna ubaci -2345 izbaci L9 dohvati 3 koliko'))
    rezultati('''\
	lista L1  lista L3
	ubaci L3 45 0  dohvati L3 0
	koliko L1  koliko L3
	prazna L1  prazna L3
	lista L5  ubaci L5 6 0  ubaci L5 7 1  ubaci L5 8 1  ubaci L5 9 0
	dohvati L5 0  dohvati L5 1  dohvati L5 2  dohvati L5 3  koliko L5
	izbaci L5 1  dohvati L5 0 dohvati L5 1 dohvati L5 2  koliko L5
    ''')
