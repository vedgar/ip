"""Računanje polinomima u jednoj varijabli s cjelobrojnim koeficijentima.

Aritmetika cijelih brojeva je specijalni slučaj, kad se x ne pojavljuje.
Dozvoljeno je ispuštanje zvjezdice za množenje u slučajevima poput
  23x, xxxx, 2(3+1), (x+1)x, (x)(7) -- ali x3 ili (x+2)3 znači potenciranje!

Semantički analizator je napravljen u obliku prevoditelja (kompajlera) u
  klasu Polinom, čiji objekti podržavaju operacije prstena i lijep ispis."""


from vepar import *
from backend import Polinom


class T(TipoviTokena):
    PLUS, MINUS, PUTA, OTVORENA, ZATVORENA = '+-*()'
    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)
        def prevedi(t): return Polinom.konstanta(t.vrijednost())
    class X(Token):
        literal = 'x'
        def prevedi(t): return Polinom.x()

@lexer
def az(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# izraz -> član | MINUS član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član faktorxz
# faktor -> BROJ | faktorxz
# faktorxz -> baza | baza BROJ
# baza -> X | OTVORENA izraz ZATVORENA

class P(Parser):
    def izraz(p) -> 'Zbroj|član|Suprotan':
        minus = p >= T.MINUS
        t = p.član()
        if minus: t = Suprotan(t)
        while ...:
            if p >= T.PLUS: t = Zbroj(t, p.član())
            elif p >= T.MINUS: t = Zbroj(t, Suprotan(p.član()))
            else: return t

    def član(p) -> 'Umnožak|faktor':
        trenutni = p.faktor()
        while p >= T.PUTA or p > {T.X, T.OTVORENA}:
            trenutni = Umnožak(trenutni, p.faktor())
        return trenutni

    def faktor(p) -> 'BROJ|izraz|X|Potencija':
        if broj := p >= T.BROJ: return broj
        elif p >= T.OTVORENA:
            baza = p.izraz()
            p >> T.ZATVORENA
        else: baza = p >> T.X
        if eksponent := p >= T.BROJ: return Potencija(baza, eksponent)
        else: return baza


### Apstraktna sintaksna stabla:
# izraz: BROJ: Token
#        X: Token
#        Zbroj: lijevo:izraz desno:izraz
#        Umnožak: lijevo:izraz desno:izraz
#        Suprotan: od:izraz
#        Potencija: baza:izraz eksponent:BROJ

class Zbroj(AST):
    lijevo: P.izraz
    desno: P.izraz
    def prevedi(zbroj): return zbroj.lijevo.prevedi() + zbroj.desno.prevedi()
    
class Umnožak(AST):
    lijevo: P.izraz
    desno: P.izraz
    def prevedi(umnožak):
        return umnožak.lijevo.prevedi() * umnožak.desno.prevedi()

class Suprotan(AST):
    od: P.izraz
    def prevedi(suprotan): return -suprotan.od.prevedi()

class Potencija(AST):
    baza: P.izraz
    eksponent: T.BROJ
    def prevedi(potencija):
        return potencija.baza.prevedi() ** potencija.eksponent.vrijednost()


def izračunaj(zadatak): print(zadatak, '=', P(zadatak).prevedi())

izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
izračunaj('x-2+5x-(7x-5)')
izračunaj('(((x-2)x+4)x-8)x+7')
izračunaj('xx-2x+3')
izračunaj('(x+1)7')
izračunaj('-'.join(['(x2-2x3-(7x+5))'] * 2))
izračunaj('x0+x0')
izračunaj('(x)x+(x)3')
with LeksičkaGreška: izračunaj('x x')
