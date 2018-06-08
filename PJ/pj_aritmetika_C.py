from pj import *
import cmath


class AC(enum.Enum):
    PLUS, MINUS, PUTA, KROZ, OTV, ZATV, KONJ = '+-*/()~'
    NA, STRELICA = '**', '->'
    class BROJ(Token):
        def vrijednost(self, _): return complex(self.sadržaj)
    class I(Token):
        def vrijednost(self, _): return 1j
    class IME(Token):
        def vrijednost(self, okolina):
            try: return okolina[self.sadržaj]
            except KeyError: self.nedeklaracija()

def ac_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '-':
            yield lex.token(AC.STRELICA if lex.slijedi('>') else AC.MINUS)
        elif znak == '*': yield lex.token(AC.NA if lex.slijedi('*')else AC.PUTA)
        elif znak == '^': yield lex.token(AC.NA)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            if lex.slijedi('.'): lex.zvijezda(str.isdigit)
            if lex.slijedi('e'): lex.slijedi('-'), lex.plus(str.isdigit)
            yield lex.token(AC.BROJ)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.token(AC.I if lex.sadržaj == 'i' else AC.IME)
        else: yield lex.token(operator(AC, znak) or lex.greška())


### Beskontekstna gramatika
# start -> izraz STRELICA IME start | izraz
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor 
# baza -> BROJ | IME | I | OTV izraz ZATV | baza KONJ

class ACParser(Parser):
    def start(self):
        env = []
        while True:
            izraz = self.izraz()
            if self >> AC.STRELICA: 
                varijabla = self.pročitaj(AC.IME)
                par = varijabla, izraz
                env.append(par)
            elif self >> E.KRAJ: return Program(env, izraz)
            else: self.greška()

    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> {AC.PLUS, AC.MINUS}:
                trenutni = Binarna(
                    op = self.zadnji, 
                    lijevo = trenutni, 
                    desno = self.član()
                )
            else: return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> {AC.PUTA, AC.KROZ}:
                trenutni = Binarna(self.zadnji, trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AC.MINUS: return Unarna(self.zadnji, self.faktor())
        baza = self.baza()
        if self >> AC.NA: return Binarna(self.zadnji, baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> {AC.BROJ, AC.IME, AC.I}: trenutni = self.zadnji
        elif self >> AC.OTV:
            trenutni = self.izraz()
            self.pročitaj(AC.ZATV)
        else: self.greška()
        while self >> AC.KONJ: trenutni = Unarna(self.zadnji, trenutni)
        return trenutni


class Program(AST('okolina izraz')):
    def izvrši(self):
        env = {}
        for ime, izraz in self.okolina: env[ime.sadržaj] = izraz.vrijednost(env)
        return self.izraz.vrijednost(env)

class Binarna(AST('op lijevo desno')):
    def vrijednost(self, env):
        o,x,y = self.op, self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ** AC.PLUS: return x + y
            elif o ** AC.MINUS: return x - y
            elif o ** AC.PUTA: return x * y
            elif o ** AC.KROZ: return x / y
            elif o ** AC.NA: return x ** y
            else: assert not 'slučaj'
        except ArithmeticError as ex: o.problem(*ex.args)

class Unarna(AST('op ispod')):
    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ** AC.MINUS: return -z
        elif o ** AC.KONJ: return z.conjugate()


def izračunaj(string): return ACParser.parsiraj(ac_lex(string)).izvrši()

if __name__ == '__main__':
    from math import pi
    print(izračunaj('2+2*3'))
    print(izračunaj('(1+6*i)/(3*i-4)~^2~'))
    print(izračunaj('i^i'))
    print(izračunaj('''\
        i+1 -> t
        t/2^2^-1 -> a
        a^2^2^2^2^0 -> b
        b
    '''))
    print(abs(izračunaj('''\
        8 -> d
        10^d -> n
        (1+1/n)^n -> e
        {} -> pi
        e^(i*pi) + 1 -> skoro0
        skoro0
    '''.format(pi))))
    print(izračunaj('6.022045e23->NA 1.6605e-27->u NA*u-0.001'))
