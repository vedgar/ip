from pj import *
from backend import Polinom


class AZ(enum.Enum):
    PLUS = '+'
    MINUS = '-'
    PUTA = '*'
    OTVORENA = '('
    ZATVORENA = ')'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def prevedi(self): return Polinom.konstanta(self.vrijednost())
    class X(Token):
        def prevedi(self): return Polinom.x()


def az_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AZ.BROJ)
        elif znak == 'x': yield lex.token(AZ.X)
        else: yield lex.literal(AZ)


### Beskontekstna gramatika:
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | faktor | član faktor  *> osim: član BROJ!
# faktor -> MINUS faktor | BROJ | X | X BROJ | OTVORENA izraz ZATVORENA


class AZParser(Parser):
    def izraz(self):
        t = self.član()
        while True:
            if self >> AZ.PLUS: t = Zbroj(t, self.član())
            elif self >> AZ.MINUS: t = Zbroj(t, Suprotan(self.član()))
            else: return t

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> AZ.PUTA or self >= {AZ.X, AZ.OTVORENA}:
                trenutni = Umnožak(trenutni,self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AZ.MINUS: return Suprotan(self.faktor())
        elif self >= AZ.BROJ: return self.pročitaj(AZ.BROJ)
        elif self >= AZ.X:
            x = self.pročitaj(AZ.X)
            if self >= AZ.BROJ: return Xna(self.pročitaj(AZ.BROJ))
            else: return x
        elif self >= AZ.OTVORENA:
            self.pročitaj(AZ.OTVORENA)
            u_zagradi = self.izraz()
            self.pročitaj(AZ.ZATVORENA)
            return u_zagradi
        else: raise self.greška()

    start = izraz


class Zbroj(AST('lijevo desno')):
    def prevedi(self):
        l, d = self.lijevo.prevedi(), self.desno.prevedi()
        return l + d
    
class Umnožak(AST('lijevo desno')):
    def prevedi(self):
        l, d = self.lijevo.prevedi(), self.desno.prevedi()
        return l * d

class Suprotan(AST('od')):
    def prevedi(self): return -self.od.prevedi()
    
class Xna(AST('eksponent')):
    def prevedi(self): return Polinom.x(self.eksponent.vrijednost())


def izračunaj(zadatak):
    print(zadatak, '=', AZParser.parsiraj(az_lex(zadatak)).prevedi())

if __name__ == '__main__':
    izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
    izračunaj('x-2+5x-(7x-5)')
    izračunaj('(((x-2)x+4)x-8)x+7')
    izračunaj('xx-2x+3')
    izračunaj('(x+1)' * 7)
    izračunaj('-'.join(['(x2-2x3-(7x+5))'] * 2))
    with očekivano(SintaksnaGreška): izračunaj('(x)x+(x)3')
    with očekivano(LeksičkaGreška): izračunaj('x x')
