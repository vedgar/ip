"""Jednostavni kalkulator s (približnim) kompleksnim brojevima po IEEE-754.

Ulaz je nula ili više naredbi pridruživanja izraz -> ime,
    nakon kojih slijedi izraz čija vrijednost se računa i vraća.
    Svaki izraz može koristiti sva prethodno definirana imena.

Prikazano je čitanje decimalnih brojeva, aliasi, postfiksni operatori, ...
"""


from vepar import *
from math import pi


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, NA, OTV, ZATV, KONJ = '+-*/^()~'
    STRELICA = '->'
    class BROJ(Token):
        def vrijednost(self, _): return complex(self.sadržaj)
    class I(Token):
        literal = 'i'
        def vrijednost(self, _): return 1j
    class IME(Token):
        def vrijednost(self, okolina): return okolina[self]


def ac(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '-': yield lex.token(T.STRELICA if lex >> '>' else T.MINUS)
        elif znak == '*': yield lex.token(T.NA if lex >> '*' else T.PUTA)
        elif znak.isdecimal():
            lex.zvijezda(str.isdecimal)
            if lex >> '.': lex.zvijezda(str.isdecimal)
            if lex >> 'e': lex >> '-', lex.plus(str.isdecimal)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.literal(T.IME)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# start -> izraz STRELICA IME start | izraz
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor 
# baza -> BROJ | IME | I | OTV izraz ZATV | baza KONJ


class P(Parser):
    lexer = ac

    def start(self):
        okolina = []
        izraz = self.izraz()
        while self >= T.STRELICA:
            okolina.append((self >> T.IME, izraz))
            izraz = self.izraz()
        return Program(okolina, izraz)

    def izraz(self):
        t = self.član()
        while op := self >= {T.PLUS, T.MINUS}: t = Binarna(op, t, self.član())
        return t

    def član(self):
        t = self.faktor()
        while op := self >= {T.PUTA, T.KROZ}: t = Binarna(op, t, self.faktor())
        return t

    def faktor(self):
        if op := self >= T.MINUS: return Unarna(op, self.faktor())
        baza = self.baza()
        if op := self >= T.NA: return Binarna(op, baza, self.faktor())
        else: return baza

    def baza(self):
        if self >= T.OTV:
            trenutni = self.izraz()
            self >> T.ZATV
        else: trenutni = self >> {T.BROJ, T.IME, T.I}
        while op := self >= T.KONJ: trenutni = Unarna(op, trenutni)
        return trenutni


### Apstraktna sintaksna stabla
# Program: okolina:[(izraz,IME)] izraz:izraz
# izraz: BROJ: Token
#        I: Token
#        IME: Token
#        Binarna: op:PLUS|MINUS|PUTA|KROZ|NA lijevo:izraz desno:izraz
#        Unarna: op:MINUS|KONJ ispod:izraz


class Program(AST('okolina završni')):
    def izvrši(self):
        env = Memorija()
        for ime, izraz in self.okolina: env[ime] = izraz.vrijednost(env)
        return self.završni.vrijednost(env)

class Binarna(AST('op lijevo desno')):
    def vrijednost(self, env):
        o,x,y = self.op, self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ^ T.PLUS: return x + y
            elif o ^ T.MINUS: return x - y
            elif o ^ T.PUTA: return x * y
            elif o ^ T.KROZ: return x / y
            elif o ^ T.NA: return x ** y
            else: assert False, 'nepokriveni slučaj binarnog operatora' + str(o)
        except ArithmeticError as ex: raise o.iznimka(ex)

class Unarna(AST('op ispod')):
    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ^ T.MINUS: return -z
        elif o ^ T.KONJ: return z.conjugate()
        else: assert False, 'nepokriveni slučaj unarnog operatora ' + str(o)


def izračunaj(string): 
    print('-' * 60)
    stablo = P(string)
    prikaz(stablo)
    print(string.rstrip(), end=' = ')
    print(stablo.izvrši())

izračunaj('2+2*3')
izračunaj('(1+6*i)/(3*i-4)~^2~')
izračunaj('i^i')
izračunaj('''\
    i+1 -> t
    t/2^2^-1 -> a
    a^2^2^2^2^0 -> b
    b
''')
izračunaj('''\
    8 -> d
    10^d -> n
    (1+1/n)^n -> e
    {} -> pi
    e^(i*pi) + 1 -> skoro0
    skoro0
'''.format(pi))
izračunaj('6.02214076e23->NA 1.6605e-27->u 1/(NA*u)')
with očekivano(LeksičkaGreška): izračunaj('2e+3')
with očekivano(GreškaIzvođenja): izračunaj('2+2/0')
with očekivano(GreškaIzvođenja): izračunaj('0**i')

# DZ: Dodajte implicitno množenje, barem s i; tako da radi npr. 2+3i
# DZ: Stritkno držanje IEEE-754 zahtijeva i ispravno tretiranje dijeljenja nulom
# (a ako želite biti sasvim compliant, i potenciranja poput 0^-1): učinite to!
