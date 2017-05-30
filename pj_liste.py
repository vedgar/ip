# 2010 K2 Z1,Z2

from pj import *


class LJ(enum.Enum):
    LISTA = 'LISTA'
    PRAZNA = 'PRAZNA'
    UBACI = 'UBACI'
    IZBACI = 'IZBACI'
    DOHVATI = 'DOHVATI'
    KOLIKO = 'KOLIKO'
    L_ID = 'L1'
    BROJ = 234
    MINUSBROJ = -234

def lj_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == 'L':
            id = lex.čitaj()
            if id.isdigit() and id != '0': yield lex.token(LJ.L_ID)
            else: lex.greška('očekivana znamenka veća od nule')
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.token(ključna_riječ(LJ, lex.sadržaj, False) or E.GREŠKA)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(LJ.BROJ)
        elif znak == '-':
            if lex.čitaj().isdigit():
                lex.zvijezda(str.isdigit)
                yield lex.token(LJ.MINUSBROJ)
            else: lex.greška("očekivana znamenka nakon '-'")
        else: lex.greška()


### Beskontekstna gramatika
# start -> naredba start | ε
# naredba -> deklaracija | provjera | ubaci | izbaci | dohvati | duljina
# deklaracija -> LISTA L_ID
# provjera -> PRAZNA L_ID
# ubaci -> UBACI L_ID ( BROJ | MINUSBROJ ) BROJ
# izbaci -> IZBACI L_ID BROJ
# dohvati -> DOHVATI L_ID BROJ
# duljina -> KOLIKO L_ID

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
        if self >> LJ.LISTA: return Deklaracija(self.pročitaj(LJ.L_ID))
        elif self >> LJ.PRAZNA: return Provjera(self.pročitaj(LJ.L_ID))
        elif self >> LJ.UBACI: return Ubaci(self.pročitaj(LJ.L_ID),
            self.pročitaj(LJ.BROJ, LJ.MINUSBROJ), self.pročitaj(LJ.BROJ))
        elif self >> LJ.IZBACI:
            return Izbaci(self.pročitaj(LJ.L_ID), self.pročitaj(LJ.BROJ))
        elif self >> LJ.DOHVATI:
            return Dohvati(self.pročitaj(LJ.L_ID), self.pročitaj(LJ.BROJ))
        elif self >> LJ.KOLIKO: return Duljina(self.pročitaj(LJ.L_ID))    

    def broj(self):
        if self >> LJ.MINUS: return Suprotan(self.pročitaj(LJ.BROJ))
        else: return self.pročitaj(LJ.BROJ)

class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        izlazi = []
        for naredba in self.naredbe: izlazi.append(naredba.izvrši(memorija))
        return izlazi
    
class Deklaracija(AST('lista')):
    def izvrši(self, memorija):
        if self.lista.sadržaj in memorija:
            self.lista.problem('redeklaracija')
        memorija[self.lista.sadržaj] = []
    
class Provjera(AST('lista')):
    def izvrši(self, memorija):
        l = pogledaj(memorija, self.lista)
        return not l

class Duljina(AST('lista')):
    def izvrši(self, memorija):
        l = pogledaj(memorija, self.lista)
        return len(l)

class Dohvati(AST('lista indeks')):
    def izvrši(self, memorija):
        l = pogledaj(memorija, self.lista)
        i = int(self.indeks.sadržaj)
        if i < len(l): return l[i]
        self.indeks.problem('Prevelik indeks')
        
class Izbaci(AST('lista indeks')):
    def izvrši(self, memorija):
        l = pogledaj(memorija, self.lista)
        i = int(self.indeks.sadržaj)
        if i < len(l): del l[i]
        else: self.indeks.problem('Prevelik indeks')

class Ubaci(AST('lista vrijednost indeks')):
    def izvrši(self, memorija):
        l = pogledaj(memorija, self.lista)
        v = int(self.vrijednost.sadržaj)
        if self.vrijednost ** LJ.MINUSBROJ: v = -v
        i = int(self.indeks.sadržaj)
        if i <= len(l): l.insert(i, v)
        else: self.indeks.problem('Prevelik indeks')

def pogledaj(memorija, l_id):
    if l_id.sadržaj in memorija: return memorija[l_id.sadržaj]
    l_id.problem('Nedeklarirana lista')


if __name__ == '__main__':
    print(*lj_lex('lista L1 prazna ubaci -2345 izbaci L9 dohvati 3 koliko tr'))
    print(*LJParser.parsiraj(lj_lex('''\
	lista L1  lista L3
	ubaci L3 45 0  dohvati L3 0
	koliko L1  koliko L3
	prazna L1  prazna L3
	lista L5  ubaci L5 6 0  ubaci L5 7 1  ubaci L5 8 1  ubaci L5 9 0
	dohvati L5 0  dohvati L5 1  dohvati L5 2  dohvati L5 3  koliko L5
	izbaci L5 1  dohvati L5 0 dohvati L5 1 dohvati L5 2  koliko L5
    ''')).izvrši())
