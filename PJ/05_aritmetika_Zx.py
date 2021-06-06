"""Računanje polinomima u jednoj varijabli s cjelobrojnim koeficijentima.

Aritmetika cijelih brojeva je specijalni slučaj, kad se x ne pojavljuje.
Dozvoljeno je ispuštanje zvjezdice za množenje u slučajevima poput
  23x, xxxx, 2(3+1), (x+1)x, (x)(7) -- ali ne x3: to znači potenciranje!
  Također, zabranjeni su izrazi poput (x+2)3, te (već leksički) 2 3.

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
# izraz -> član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član faktorxz
# faktor -> MINUS faktor | BROJ | faktorxz
# faktorxz -> X | X BROJ | OTVORENA izraz ZATVORENA

class P(Parser):
    def izraz(p) -> 'Zbroj|član':
        t = p.član()
        while ...:
            if p >= T.PLUS: t = Zbroj(t, p.član())
            elif p >= T.MINUS: t = Zbroj(t, Suprotan(p.član()))
            else: return t

    def član(p) -> 'Umnožak|faktor':
        trenutni = p.faktor()
        while p >= T.PUTA or p > {T.X, T.OTVORENA}:
            trenutni = Umnožak(trenutni, p.faktor())
        return trenutni

    def faktor(p) -> 'Suprotan|BROJ|Xna|X|izraz':
        if p >= T.MINUS: return Suprotan(p.faktor())
        elif broj := p >= T.BROJ: return broj
        elif x := p >= T.X:
            if eksponent := p >= T.BROJ: return Xna(eksponent)
            else: return x
        elif p >> T.OTVORENA:
            u_zagradi = p.izraz()
            p >> T.ZATVORENA
            return u_zagradi


### Apstraktna sintaksna stabla:
# izraz: BROJ: Token
#        X: Token
#        Zbroj: lijevo:izraz desno:izraz
#        Umnožak: lijevo:izraz desno:izraz
#        Suprotan: od:izraz
#        Xna: eksponent:BROJ

class Zbroj(AST):
    lijevo: 'izraz'
    desno: 'izraz'
    def prevedi(zbroj): return zbroj.lijevo.prevedi() + zbroj.desno.prevedi()
    
class Umnožak(AST):
    lijevo: 'izraz'
    desno: 'izraz'
    def prevedi(umnožak):
        return umnožak.lijevo.prevedi() * umnožak.desno.prevedi()

class Suprotan(AST):
    od: 'izraz'
    def prevedi(self): return -self.od.prevedi()
    
class Xna(AST):
    eksponent: 'BROJ'
    def prevedi(self): return Polinom.x(self.eksponent.vrijednost())


def izračunaj(zadatak): print(zadatak, '=', P(zadatak).prevedi())

izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
izračunaj('x-2+5x-(7x-5)')
izračunaj('(((x-2)x+4)x-8)x+7')
izračunaj('xx-2x+3')
izračunaj('(x+1)' * 7)
izračunaj('-'.join(['(x2-2x3-(7x+5))'] * 2))
izračunaj('x0+x0')
with SintaksnaGreška: izračunaj('(x)x+(x)3')
with LeksičkaGreška: izračunaj('x x')
