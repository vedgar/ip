from pj import *


class AZ(enum.Enum):
    BROJ = 1
    PLUS = '+'
    MINUS = '-'
    PUTA = '*'
    OTVORENA = '('
    ZATVORENA = ')'
    X = 'x'


def az_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AZ.BROJ)
        else: yield lex.token(operator(AZ, znak) or lex.greška())


### Beskontekstna gramatika:
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | faktor | MINUS član | član faktor *vidi dolje!
# faktor -> BROJ | X | X BROJ | OTVORENA izraz ZATVORENA


Binarni = AST('lijevo desno')
class Zbroj(Binarni): """Zbroj dva polinoma."""
class Razlika(Binarni): """Razlika dva polinoma."""
class Umnožak(Binarni): """Umnožak dva polinoma."""
class Suprotan(AST('od')): """Suprotan polinom zadanom."""
class Xna(AST('eksponent')): """Monom x^eksponent."""


class AZParser(Parser):
    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> AZ.PLUS: trenutni = Zbroj(trenutni, self.član())
            elif self >> AZ.MINUS: trenutni = Razlika(trenutni, self.član())
            else: return trenutni

    def član(self):
        if self >> AZ.MINUS: return Suprotan(self.član())
        trenutni = self.faktor()
        while True:
            if self >> AZ.PUTA: trenutni = Umnožak(trenutni, self.faktor())
            elif self >> {AZ.X, AZ.OTVORENA}:  # *ovdje AZ.BROJ je ružno: (x+2)3
                self.vrati()
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

def prevedi(p):
    if p ** AZ.BROJ: return Polinom.konstanta(int(p.sadržaj))
    elif p ** AZ.X: return Polinom.x()
    elif p ** Binarni:
        l, d = prevedi(p.lijevo), prevedi(p.desno)
        if p ** Zbroj: return l + d
        elif p ** Razlika: return l - d
        elif p ** Umnožak: return l * d
    elif p ** Suprotan: return -prevedi(p.od)
    elif p ** Xna: return Polinom.x(int(p.eksponent.sadržaj))


def izračunaj(zadatak):
    print(zadatak, '=', prevedi(AZParser.parsiraj(az_lex(zadatak))))

if __name__ == '__main__':
    izračunaj('(5+2*8-3)(3-1)-(-4+2*19)')
    izračunaj('x-2+5x-(7x-5)')
    izračunaj('(((x-2)x+4)x-8)x+7')
    izračunaj('x2-2x+3')
    izračunaj('(x+1)' * 7)
    izračunaj('(x-2+5x-(7x-5))-(x-2+5x-(7x-5))')
