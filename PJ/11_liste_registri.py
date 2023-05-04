"""Virtualna mašina za rad s listama; kolokvij 31. siječnja 2011. (Puljić).

  9 registara (L1 do L9) koji drže liste cijelih brojeva (počinju od prazne),
  2 naredbe (ubacivanje i izbacivanje elementa po indeksu),
  3 upita (duljina i praznost liste, dohvaćanje elementa po indeksu)."""


from vepar import *


class T(TipoviTokena):
    LISTA, UBACI, IZBACI = 'lista', 'ubaci', 'izbaci'
    KOLIKO, PRAZNA, DOHVATI = 'koliko', 'prazna', 'dohvati'
    class ID(Token): pass
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class MINUSBROJ(BROJ): """Negativni broj."""

@lexer
def listlexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == 'L':
            if (nakonL := next(lex)).isdecimal():
                n = lex.prirodni_broj(nakonL)
                tok = lex.token(T.ID)
                if 1 <= n <= 9: yield tok
                else: raise tok.krivi_sadržaj('očekivan broj liste između 1 i 9')
            else:
                lex * str.isalpha
                yield lex.literal(T, case=False)
        elif znak.isalpha():
            lex * str.isalpha
            yield lex.literal(T, case=False)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '-':
            lex.prirodni_broj('', nula=False)
            yield lex.token(T.MINUSBROJ)
        else: raise lex.greška()


### Beskontekstna gramatika (jezik je regularan!)
# start -> '' | start naredba
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
    def start(self) -> 'Program':
        naredbe = []
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self) -> 'Ubaci|Deklaracija|Provjera|Izbaci|Dohvati|Duljina':
        if self >= T.LISTA: return Deklaracija(self >> T.ID)
        elif self >= T.PRAZNA: return Provjera(self >> T.ID)
        elif self >= T.KOLIKO: return Duljina(self >> T.ID)
        elif self >= T.DOHVATI: return Dohvati(self >> T.ID, self >> T.BROJ)
        elif self >= T.IZBACI: return Izbaci(self >> T.ID, self >> T.BROJ)
        elif self >= T.UBACI: return Ubaci(self >> T.ID, 
            self >> {T.BROJ,T.MINUSBROJ}, self >> T.BROJ)
        else: raise self.greška()


class Program(AST):
    """Program u jeziku listâ."""
    naredbe: 'naredba*'
    def izvrši(self):
        rt.mem = Memorija(redefinicija=False)
        for nar in self.naredbe: print(nar, ' --> ', nar.izvrši())

class Deklaracija(AST):
    """Deklaracija liste."""
    lista: 'ID'
    def izvrši(self): rt.mem[self.lista] = []

class Provjera(AST):
    """Je li lista prazna?"""
    lista: 'ID'
    def izvrši(self): return not rt.mem[self.lista]

class Duljina(AST):
    """Broj elemenata u listi."""
    lista: 'ID'
    def izvrši(self): return len(rt.mem[self.lista])

class Dohvati(AST):
    """Element zadanog indeksa (brojeći od 0). Prevelik indeks javlja grešku."""
    lista: 'ID'
    indeks: 'BROJ'
    def izvrši(self):
        l, i = rt.mem[self.lista], self.indeks.vrijednost()
        if i < len(l): return l[i]
        else: raise self.iznimka('Prevelik indeks')
        
class Izbaci(AST):
    """Izbacuje element zadanog indeksa iz liste ili javlja grešku izvođenja."""
    lista: 'ID'
    indeks: 'BROJ'
    def izvrši(self):
        l, i = rt.mem[self.lista], self.indeks.vrijednost()
        if i < len(l): del l[i]
        else: raise self.iznimka('Prevelik indeks')

class Ubaci(AST):
    """Ubacuje vrijednost u listu na zadanom indeksu, ili javlja grešku."""
    lista: 'ID'
    element: 'BROJ|MINUSBROJ'
    indeks: 'BROJ'
    def izvrši(self):
        l, i = rt.mem[self.lista], self.indeks.vrijednost()
        if i <= len(l): l.insert(i, self.element.vrijednost())
        else: raise self.iznimka('Prevelik indeks')


listlexer('lista L1 prazna ubaci-2345izbaci L9 dohvati 3 koliko')
P('''
    lista L1  lista L3  ubaci L3 45 0  dohvati L3 0
    koliko L1  koliko L3  prazna L1  prazna L3
    Lista L5  ubaci L5 6 0  ubaci L5 -7 1  ubaci L5 8 1  ubaci L5 9 0
    koliko L5  dohvati L5 0  dohvati L5 1  dohvati L5 2  dohvati L5 3
    izbaci L5 1  koliko L5 dohvati L5 0 dohvati L5 1 dohvati L5 2
''').izvrši()
for ime, lista in rt.mem: print(ime, '=', lista)
with LeksičkaGreška: listlexer('L0')
with SintaksnaGreška: P('ubaci L5 6 -2')
with SemantičkaGreška: P('ubaci L7 5 0').izvrši()
with LeksičkaGreška: listlexer('ubaci L3 5 -0')
with GreškaIzvođenja: P('lista L1 ubaci L1 7 3').izvrši()
