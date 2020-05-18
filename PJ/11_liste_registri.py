"""Virtualna mašina za rad s listama; kolokvij 31. siječnja 2011. (Puljić).

  9 registara (L1 do L9) koji drže liste cijelih brojeva (počinju od prazne),
  2 naredbe (ubacivanje i izbacivanje elementa po indeksu),
  3 upita (duljina i praznost liste, dohvaćanje elementa po indeksu)."""


from pj import *


class T(TipoviTokena):
    LISTA, UBACI, IZBACI = 'lista', 'ubaci', 'izbaci'
    KOLIKO, PRAZNA, DOHVATI = 'koliko', 'prazna', 'dohvati'
    class ID(Token): pass
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class MINUSBROJ(BROJ): """Negativni broj."""


def list_lexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == 'L':
            nakonL = lex.čitaj()
            if nakonL.isdecimal():
                n = lex.prirodni_broj(nakonL)
                tok = lex.token(T.ID)
                if 1 <= n <= 9: yield tok
                else: raise tok.krivi_sadržaj('očekivan broj liste između 1 i 9')
            else:
                lex.zvijezda(str.isalpha)
                yield lex.literal(T, case=False)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.literal(T, case=False)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '-':
            lex.prirodni_broj(nula=False)
            yield lex.token(T.MINUSBROJ)
        else: raise lex.greška()


### Beskontekstna gramatika (jezik je regularan!)
# start -> naredba start | ''
# naredba -> deklaracija | provjera | ubaci | izbaci | dohvati | duljina
# deklaracija -> LISTA ID
# provjera -> PRAZNA ID
# ubaci -> UBACI ID BROJ BROJ | UBACI ID MINUSBROJ BROJ
# izbaci -> IZBACI ID BROJ
# dohvati -> DOHVATI ID BROJ
# duljina -> KOLIKO ID

### Apstraktna sintaksna stabla
# Program: naredbe:[naredba]
# naredba: Deklaracija: lista:ID
#          Provjera: lista:ID
#          Ubaci: lista:ID vrijednost:BROJ|MINUSBROJ indeks:BROJ
#          Izbaci: lista:ID indeks:BROJ
#          Dohvati: lista:ID indeks:BROJ
#          Duljina: lista:ID

class P(Parser):
    lexer = list_lexer

    def start(self):
        naredbe = []
        while not self >> KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        p = self.pročitaj
        if self>>T.UBACI: return Ubaci(p(T.ID),p(T.BROJ,T.MINUSBROJ),p(T.BROJ))
        elif self >> T.LISTA: return Deklaracija(p(T.ID))
        elif self >> T.PRAZNA: return Provjera(p(T.ID))
        elif self >> T.IZBACI: return Izbaci(p(T.ID), p(T.BROJ))
        elif self >> T.DOHVATI: return Dohvati(p(T.ID), p(T.BROJ))
        elif self >> T.KOLIKO: return Duljina(p(T.ID))
        else: self.greška()


class Program(AST('naredbe')):
    """Program u jeziku listâ."""
    def izvrši(self):
        mem = Memorija(redefinicija=False)
        for nar in self.naredbe: print(nar, nar.izvrši(mem), sep=' --> ')

class Deklaracija(AST('lista')):
    """Deklaracija liste."""
    def izvrši(self, memorija): memorija[self.lista] = []

class Provjera(AST('lista')):
    """Je li lista prazna?"""
    def izvrši(self, memorija): return not memorija[self.lista]

class Duljina(AST('lista')):
    """Broj elemenata u listi."""
    def izvrši(self, memorija): return len(memorija[self.lista])

class Dohvati(AST('lista indeks')):
    """Element zadanog indeksa (brojeći od 0). Prevelik indeks javlja grešku."""
    def izvrši(self, memorija):
        l, i = memorija[self.lista], self.indeks.vrijednost()
        if i < len(l): return l[i]
        else: raise self.indeks.iznimka('Prevelik indeks')
        
class Izbaci(AST('lista indeks')):
    """Izbacuje element zadanog indeksa iz liste ili javlja grešku izvođenja."""
    def izvrši(self, memorija):
        l, i = memorija[self.lista], self.indeks.vrijednost()
        if i < len(l): del l[i]
        else: raise self.indeks.iznimka('Prevelik indeks')

class Ubaci(AST('lista element indeks')):
    """Ubacuje vrijednost u listu na zadanom indeksu, ili javlja grešku."""
    def izvrši(self, memorija):
        l, i = memorija[self.lista], self.indeks.vrijednost()
        if i <= len(l): l.insert(i, self.element.vrijednost())
        else: raise self.indeks.iznimka('Prevelik indeks')


P.tokeniziraj('lista L1 prazna ubaci-2345izbaci L9 dohvati 3 koliko')
source = '''lista L1  lista L3
    ubaci L3 45 0  dohvati L3 0
    koliko L1  koliko L3
    prazna L1  prazna L3
    Lista L5  ubaci L5 6 0  ubaci L5 -7 1  ubaci L5 8 1  ubaci L5 9 0
    dohvati L5 0  dohvati L5 1  dohvati L5 2  dohvati L5 3  koliko L5
    izbaci L5 1  dohvati L5 0 dohvati L5 1 dohvati L5 2  koliko L5'''
P(source).izvrši()
with očekivano(LeksičkaGreška): P.tokeniziraj('L0')
with očekivano(SintaksnaGreška): P('ubaci L5 6 -2')
with očekivano(SemantičkaGreška): P('ubaci L7 5 0').izvrši()
with očekivano(LeksičkaGreška): P.tokeniziraj('ubaci L3 5 -0')
