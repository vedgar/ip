"""Računanje molarne mase kemijskog spoja: po uzoru na kolokvij 7. rujna 2018.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2p.18-09-07.pdf"""


from vepar import *
from backend import referentne_atomske_mase


class T(TipoviTokena):
    OOTV, OZATV, UOTV, UZATV = '()[]'

    class N(Token):
        literal = 'n'
        def vrijednost(t): 
            try: return rt.n
            except AttributeError: raise t.nedeklaracija('n nije naveden')

    class ATOM(Token):
        def masa(t): return rt.tablica[t]

    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)

@lexer
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
# formula -> skupina | formula skupina
# skupina -> ATOM | ATOM BROJ | zagrade | zagrade BROJ | zagrade N
# zagrade -> OOTV formula OZATV | UOTV formula UZATV

class spoj(Parser):
    def formula(p) -> 'Formula':
        l = [p.skupina()]
        while p > {T.ATOM, T.OOTV, T.UOTV}: l.append(p.skupina())
        return Formula(l)

    def skupina(p) -> 'Skupina':
        if p >= T.OOTV:
            što = p.formula()
            p >> T.OZATV
        elif p >= T.UOTV:
            što = p.formula()
            p >> T.UZATV
        else: što = p >> T.ATOM
        return Skupina(što, p >= {T.BROJ, T.N})


### AST
# Formula: skupine:[Skupina]
# Skupina: čega:ATOM|Formula koliko:(BROJ|N)?

class Formula(AST):
    skupine: 'Skupina*'

    def masa(spoj):
        return sum(skupina.ukupno() for skupina in spoj.skupine)

    def Mr(spoj, **mase):
        del rt.n
        if 'n' in mase: rt.n = mase.pop('n')
        rt.tablica = Memorija(referentne_atomske_mase | mase)
        return spoj.masa()

class Skupina(AST):
    čega: 'ATOM|Formula'
    koliko: '(BROJ|N)?'

    def ukupno(skupina):
        m = skupina.čega.masa()
        if skupina.koliko: m *= skupina.koliko.vrijednost()
        return m


natrijev_trikarbonatokobaltat = spoj('Na3[Co(CO3)3]')
prikaz(natrijev_trikarbonatokobaltat)
print(natrijev_trikarbonatokobaltat.Mr())
for krivo in 'SnABcdefG', 'O Be', 'Es(n)':
    with LeksičkaGreška: kemija(krivo)
    print()
kemija(']nB')
print('Molarna masa butana je', spoj('CH3(CH2)nCH3').Mr(n=2))
