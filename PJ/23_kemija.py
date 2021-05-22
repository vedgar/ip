"""Kemijske formule: zadatak s kolokvija 2018.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2p.18-09-07.pdf"""


from vepar import *
from backend import referentne_atomske_mase


class T(TipoviTokena):
    OOTV, OZATV, UOTV, UZATV = '()[]'

    class N(Token):
        literal = 'n'
        def vrijednost(t, tablica): return tablica[t]

    class ATOM(Token):
        def masa(t, tablica): return tablica[t]

    class BROJ(Token):
        def vrijednost(t, _): return int(t.sadržaj)


def kemija(lex):
    može_n = False
    for znak in lex:
        if znak == 'n':
            if može_n: yield lex.token(T.N)
            else: raise lex.greška('n ne može doći ovdje')
        elif znak.isdecimal():
            lex.prirodni_broj(znak, nula=False)
            yield lex.token(T.BROJ)
        elif znak.isupper():
            lex >= str.islower
            yield lex.token(T.ATOM)
        else: yield lex.literal(T)
        može_n = znak in {']', ')'}


### BKG
# formula -> skupina | skupina formula
# skupina -> ATOM | ATOM BROJ | zagrade | zagrade BROJ | zagrade N
# zagrade -> OOTV formula OZATV | UOTV formula UZATV


class spoj(Parser):
    def formula(p):
        l = [p.skupina()]
        while p > {T.ATOM, T.OOTV, T.UOTV}: l.append(p.skupina())
        return Formula(l)

    def skupina(p):
        if p >= T.OOTV:
            što = p.formula()
            p >> T.OZATV
        elif p >= T.UOTV:
            što = p.formula()
            p >> T.UZATV
        else: što = p >> T.ATOM
        return Skupina(što, p >= {T.BROJ, T.N})

    lexer = kemija
    start = formula


### AST
# Formula: skupine:[Skupina]
# Skupina: čega:ATOM|Formula koliko:(BROJ|N)?


class Formula(AST):
    skupine: 'Skupina*'

    def masa(spoj, tablica):
        return sum(skupina.ukupno(tablica) for skupina in spoj.skupine)

    def Mr(spoj, **mase):
        return spoj.masa(Memorija(referentne_atomske_mase | mase))


class Skupina(AST):
    čega: 'ATOM|Formula'
    koliko: '(BROJ|N)?'

    def ukupno(skupina, tablica):
        m = skupina.čega.masa(tablica)
        if skupina.koliko: m *= skupina.koliko.vrijednost(tablica)
        return m


natrijev_trikarbonatokobaltat = spoj('Na3[Co(CO3)3]')
prikaz(natrijev_trikarbonatokobaltat)
for krivo in 'SnABcdefG', 'O Be', 'Es(n)':
    with LeksičkaGreška: spoj.tokeniziraj(krivo)
    print()
spoj.tokeniziraj(']nB')
print('Molarna masa butana je', spoj('CH3(CH2)nCH3').Mr(n=2))
