"""Računanje polinomima u jednoj varijabli s cjelobrojnim koeficijentima.

Aritmetika cijelih brojeva je specijalni slučaj, kad se x ne pojavljuje.
Dozvoljeno je ispuštanje zvjezdice za množenje u slučajevima poput
  23x, xxxx, 2(3+1), (x+1)x, (x)(7) -- ali ne x3: to znači potenciranje!
Pokazuje se kako programirati jednostavne izuzetke od pravila BKG:
  konkretno, zabranjeni su izrazi poput (x+2)3, te (već leksički) 2 3.

Semantički analizator je napravljen u obliku prevoditelja (kompajlera) u
  klasu Polinom, čiji objekti podržavaju operacije prstena i lijep ispis."""


from vepar import *
from backend import Polinom


class T(TipoviTokena):
    PLUS, MINUS, PUTA, OTVORENA, ZATVORENA = '+-*()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def prevedi(self): return Polinom.konstanta(self.vrijednost())
    class X(Token):
        literal = 'x'
        def prevedi(self): return Polinom.x()


def az(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | faktor | član faktorxz
# faktorxz -> X | X BROJ | OTVORENA izraz ZATVORENA
# faktor -> MINUS faktor | BROJ | faktorxz

### Apstraktna sintaksna stabla:
# izraz: BROJ: Token
#        X: Token
#        Zbroj: lijevo:izraz desno:izraz
#        Umnožak: lijevo:izraz desno:izraz
#        Suprotan: od:izraz
#        Xna: eksponent:BROJ


class P(Parser):
    def izraz(self):
        t = self.član()
        while True:
            if self >= T.PLUS: t = Zbroj(t, self.član())
            elif self >= T.MINUS: t = Zbroj(t, Suprotan(self.član()))
            else: return t

    def član(self):
        trenutni = self.faktor()
        while self >= T.PUTA or self > {T.X, T.OTVORENA}:
            trenutni = Umnožak(trenutni, self.faktor())
        return trenutni

    def faktor(self):
        if self >= T.MINUS: return Suprotan(self.faktor())
        elif broj := self >= T.BROJ: return broj
        elif x := self >= T.X:
            if eksponent := self >= T.BROJ: return Xna(eksponent)
            else: return x
        elif self >> T.OTVORENA:
            u_zagradi = self.izraz()
            self >> T.ZATVORENA
            return u_zagradi

    lexer = az
    start = izraz


class Zbroj(AST('lijevo desno')):
    def prevedi(self): return self.lijevo.prevedi() + self.desno.prevedi()
    
class Umnožak(AST('lijevo desno')):
    def prevedi(self): return self.lijevo.prevedi() * self.desno.prevedi()

class Suprotan(AST('od')):
    def prevedi(self): return -self.od.prevedi()
    
class Xna(AST('eksponent')):
    def prevedi(self): return Polinom.x(self.eksponent.vrijednost())


def izračunaj(zadatak): print(zadatak, '=', P(zadatak).prevedi())

izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
izračunaj('x-2+5x-(7x-5)')
izračunaj('(((x-2)x+4)x-8)x+7')
izračunaj('xx-2x+3')
izračunaj('(x+1)' * 7)
izračunaj('-'.join(['(x2-2x3-(7x+5))'] * 2))
izračunaj('x0+x0')
with očekivano(SintaksnaGreška): izračunaj('(x)x+(x)3')
with očekivano(LeksičkaGreška): izračunaj('x x')
