from pj import *


class AZ(enum.Enum):
    PLUS, MINUS, PUTA, OTVORENA, ZATVORENA = '+-*()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def prevedi(self): return Polinom.konstanta(self.vrijednost())
    class X(Token):
        def prevedi(self): return Polinom.x()
        def vrijednost(self): raise NotImplementedError('Nepoznata vrijednost')


def az_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AZ.BROJ)
        elif znak == 'x': yield lex.token(AZ.X)
        else: yield lex.token(operator(AZ, znak) or lex.greška())


### Beskontekstna gramatika:
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | faktor | MINUS član | član faktor *>vidi dolje!
# faktor -> BROJ | X | X BROJ | OTVORENA izraz ZATVORENA


class AZParser(Parser):
    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> AZ.PLUS: 
                član = self.član()
                trenutni = Zbroj(trenutni, član)
            elif self >> AZ.MINUS:
                član = self.član()
                trenutni = Razlika(trenutni, član)
            else: break
        return trenutni

    def član(self):
        if self >> AZ.MINUS: return Suprotan(self.član())
        trenutni = self.faktor()
        while True:
            if self >> AZ.PUTA: trenutni = Umnožak(trenutni, self.faktor())
            elif self >= {AZ.X, AZ.OTVORENA}:  # *ovdje AZ.BROJ je ružno: (x+2)3
                trenutni = Umnožak(trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AZ.BROJ: return self.zadnji
        elif self >> AZ.X:
            x = self.zadnji
            if self >> AZ.BROJ: return Xna(self.zadnji)
            else: return x
        elif self >> AZ.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AZ.ZATVORENA)
            return u_zagradi
        else: self.greška()

    start = izraz


class Zbroj(AST('lijevo desno')):
    def prevedi(self):
        l, d = self.lijevo.prevedi(), self.desno.prevedi()
        return l + d

class Razlika(AST('lijevo desno')):
    def prevedi(self):
        l, d = self.lijevo.prevedi(), self.desno.prevedi()
        return l - d
    
class Umnožak(AST('lijevo desno')):
    def prevedi(self):
        l, d = self.lijevo.prevedi(), self.desno.prevedi()
        return l * d

class Suprotan(AST('od')):
    def prevedi(self):
        return -self.od.prevedi()
    
class Xna(AST('eksponent')):
    def prevedi(self):
        return Polinom.x(self.eksponent.vrijednost())


class Polinom(collections.Counter):
    @classmethod
    def konstanta(klasa, broj): return klasa({0: broj})

    @classmethod
    def x(klasa, eksponent=1): return klasa({eksponent: 1})

    def __add__(p, q):
        r = Polinom(p)
        for eksponent, koeficijent in q.items(): r[eksponent] += koeficijent
        return r

    def __mul__(p, q):
        r = Polinom()
        for e1, k1 in p.items():
            for e2, k2 in q.items(): r[e1 + e2] += k1 * k2
        return r

    def __neg__(p): return Polinom.konstanta(-1) * p

    def __sub__(p, q): return p + -q

    def monomi(p):
        for e, k in sorted(p.items(), reverse=True):
            if not k: continue
            č = format(k, '+')
            if e:
                if abs(k) == 1: č = č[0]
                č += 'x'
                if e > 1: č += str(e)
            yield č

    def __str__(p): return ''.join(p.monomi()).lstrip('+') or '0'


def izračunaj(zadatak):
    print(zadatak, '=', AZParser.parsiraj(az_lex(zadatak)).prevedi())

if __name__ == '__main__':
    izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
    izračunaj('x-2+5x-(7x-5)')
    izračunaj('(((x-2)x+4)x-8)x+7')
    izračunaj('x2-2x+3')
    izračunaj('(x+1)' * 7)
    izračunaj('(x-2+5x-(7x-5))-(x-2+5x-(7x-5))')
