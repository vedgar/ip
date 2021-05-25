"""Jednostavni kalkulator s (približnim) kompleksnim brojevima po IEEE-754.

Ulaz je nula ili više naredbi pridruživanja izraz -> ime,
    nakon kojih slijedi izraz čija vrijednost se računa i vraća.
    Svaki izraz može koristiti sva prethodno definirana imena.

Prikazano je čitanje decimalnih brojeva, aliasi, postfiksni operatori, ...
Također imamo kompajliranje u jednostavni TAC (two/three-address code)."""


from vepar import *


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, NA, OTV, ZATV, KONJ = '+-*/^()~'
    STRELICA = '->'
    class BROJ(Token):
        def vrijednost(self, _): return complex(self.sadržaj)
        def tac(self, reg):
            yield [r:=next(reg), '=', float(self.sadržaj)]
            return r
    class I(Token):
        literal = 'i'
        def vrijednost(self, _): return 1j
        def tac(self, reg):
            yield [r:=next(reg), '=', self.literal]
            return r
    class IME(Token):
        def vrijednost(self, okolina): return okolina[self]
        def tac(self, reg):
            yield [r:=next(reg), '=', self.sadržaj]
            return r

def ac(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '-': yield lex.token(T.STRELICA if lex >= '>' else T.MINUS)
        elif znak == '*': yield lex.token(T.NA if lex >= '*' else T.PUTA)
        elif znak.isdecimal():
            lex * str.isdecimal
            if lex >= '.': lex * str.isdecimal
            if lex >= 'e':
                lex >= '-'
                lex + str.isdecimal
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * str.isalnum
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

    def start(p):
        okolina = []
        izraz = p.izraz()
        while p >= T.STRELICA:
            okolina.append((p >> T.IME, izraz))
            izraz = p.izraz()
        return Program(okolina, izraz)

    def izraz(p):
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Binarna(op, t, p.član())
        return t

    def član(p):
        t = p.faktor()
        while op := p >= {T.PUTA, T.KROZ}: t = Binarna(op, t, p.faktor())
        return t

    def faktor(p):
        if op := p >= T.MINUS: return Unarna(op, p.faktor())
        baza = p.baza()
        if op := p >= T.NA: return Binarna(op, baza, p.faktor())
        else: return baza

    def baza(p):
        if p >= T.OTV:
            trenutni = p.izraz()
            p >> T.ZATV
        else: trenutni = p >> {T.BROJ, T.IME, T.I}
        while op := p >= T.KONJ: trenutni = Unarna(op, trenutni)
        return trenutni


### Apstraktna sintaksna stabla
# Program: okolina:[(izraz,IME)] završni:izraz
# izraz: BROJ: Token
#        I: Token
#        IME: Token
#        Binarna: op:PLUS|MINUS|PUTA|KROZ|NA lijevo:izraz desno:izraz
#        Unarna: op:MINUS|KONJ ispod:izraz


class Program(AST):
    okolina: '(izraz,IME)*'
    završni: 'izraz'

    def izvrši(program):
        env = Memorija()
        for ime, izraz in program.okolina: env[ime] = izraz.vrijednost(env)
        return program.završni.vrijednost(env)

    def kompajliraj(program):
        reg = Registri()
        for ime, izraz in program.okolina:
            r = yield from izraz.tac(reg)
            yield [ime.sadržaj, '=', r]
        r = yield from program.završni.tac(reg)
        yield ['OUT', r]

class Binarna(AST):
    op: 'T'
    lijevo: 'izraz'
    desno: 'izraz'

    def vrijednost(self, env):
        o = self.op
        x, y = self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ^ T.PLUS: return x + y
            elif o ^ T.MINUS: return x - y
            elif o ^ T.PUTA: return x * y
            elif o ^ T.KROZ: return x / y
            elif o ^ T.NA: return x ** y
            else: assert False, f'nepokriveni slučaj binarnog operatora {o}'
        except ArithmeticError as ex: raise o.iznimka(ex)

    def tac(self, reg):
        r1 = yield from self.lijevo.tac(reg)
        r2 = yield from self.desno.tac(reg)
        yield [r:=next(reg), '=', r1, self.op.tip.value, r2]
        return r

class Unarna(AST):
    op: 'T'
    ispod: 'izraz'

    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ^ T.MINUS: return -z
        elif o ^ T.KONJ: return z.conjugate()
        else: assert False, f'nepokriveni slučaj unarnog operatora {o}'

    def tac(self, reg):
        r1 = yield from self.ispod.tac(reg)
        yield [r:=next(reg), '=', self.op.tip.value, r1]
        return r

def izračunaj(string): 
    print('-' * 60)
    prikaz(program := P(string))
    for instrukcija in program.kompajliraj(): print('\t\t', '|', *instrukcija)
    print(string.rstrip(), '=', program.izvrši())

izračunaj('2+2*3')
izračunaj('(1+6*i)/(3*i-4)~^2~')
izračunaj('i^i')
izračunaj('''
    i+1 -> t
    t/2^2^-1 -> a
    a^2^2^2^2^0 -> b
    b
''')
izračunaj(f'''
    8 -> d
    10^d -> n
    (1+1/n)^n -> e
    355/113 -> pi
    e^(i*pi) + 1 -> skoro0
    skoro0
''')
izračunaj('6.02214076e23->NA 1.6605e-27->u 1/(NA*u)')
with LeksičkaGreška: izračunaj('2e+3')
with GreškaIzvođenja: izračunaj('2+2/0')
with GreškaIzvođenja: izračunaj('0**i')

# DZ: Dodajte implicitno množenje, barem s i; tako da radi npr. 2+3i
# DZ: Stritkno držanje IEEE-754 zahtijeva i ispravno tretiranje dijeljenja nulom
# (a ako želite biti sasvim compliant, i potenciranja poput 0^-1): učinite to!
