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
        def vrijednost(self): return complex(self.sadržaj)
        def tac(self):
            yield [r:=next(rt.reg), '=', float(self.sadržaj)]
            return r
    class I(Token):
        literal = 'i'
        def vrijednost(self): return 1j
        def tac(self):
            yield [r:=next(rt.reg), '=', self.literal]
            return r
    class IME(Token):
        def vrijednost(self): return rt.okolina[self]
        def tac(self):
            yield [r:=next(rt.reg), '=', self.sadržaj]
            return r

@lexer
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
            yield lex.literal_ili(T.IME)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# start -> izraz | izraz STRELICA IME start
# izraz -> član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> baza | baza NA faktor | MINUS faktor 
# baza -> BROJ | IME | I | OTV izraz ZATV | baza KONJ


class P(Parser):
    def start(p) -> 'Program':
        definicije = []
        izraz = p.izraz()
        while p >= T.STRELICA:
            definicije.append((p >> T.IME, izraz))
            izraz = p.izraz()
        return Program(definicije, izraz)

    def izraz(p) -> 'član|Binarna':
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Binarna(op, t, p.član())
        return t

    def član(p) -> 'faktor|Binarna':
        t = p.faktor()
        while op := p >= {T.PUTA, T.KROZ}: t = Binarna(op, t, p.faktor())
        return t

    def faktor(p) -> 'Unarna|baza|Binarna':
        if op := p >= T.MINUS: return Unarna(op, p.faktor())
        baza = p.baza()
        if op := p >= T.NA: return Binarna(op, baza, p.faktor())
        else: return baza

    def baza(p) -> 'izraz|BROJ|IME|I|Unarna':
        if p >= T.OTV:
            trenutni = p.izraz()
            p >> T.ZATV
        else: trenutni = p >> {T.BROJ, T.IME, T.I}
        while op := p >= T.KONJ: trenutni = Unarna(op, trenutni)
        return trenutni


### Apstraktna sintaksna stabla
# Program: definicije:[(IME,izraz)] završni:izraz
# izraz: BROJ: Token
#        I: Token
#        IME: Token
#        Binarna: op:PLUS|MINUS|PUTA|KROZ|NA lijevo:izraz desno:izraz
#        Unarna: op:MINUS|KONJ ispod:izraz


class Program(AST):
    definicije: list[tuple[T.IME,P.izraz]]
    završni: P.izraz

    def izvrši(program):
        rt.okolina = Memorija()
        for ime, izraz in program.definicije:
            rt.okolina[ime] = izraz.vrijednost()
        return program.završni.vrijednost()

    def kompajliraj(program):
        rt.reg = Registri()
        for ime, izraz in program.definicije:
            r = yield from izraz.tac()
            yield [ime.sadržaj, '=', r]
        r = yield from program.završni.tac()
        yield ['OUT', r]

class Binarna(AST):
    op: T
    lijevo: P.izraz
    desno: P.izraz

    def vrijednost(self):
        lijevo, desno = self.lijevo.vrijednost(), self.desno.vrijednost()
        try:
            match self.op.tip:
                case T.PLUS: return lijevo + desno
                case T.MINUS: return lijevo - desno
                case T.PUTA: return lijevo * desno
                case T.KROZ: return lijevo / desno
                case T.NA: return lijevo ** desno
                case _: assert False, f'nepokriveni binarni operator {self.op}'
        except ArithmeticError as ex: raise self.iznimka(ex)

    def tac(self):
        rlijevo = yield from self.lijevo.tac()
        rdesno = yield from self.desno.tac()
        yield [rrezultat:=next(rt.reg), '=', rlijevo, self.op.tip.value, rdesno]
        return rrezultat

class Unarna(AST):
    op: T
    ispod: P.izraz

    def vrijednost(self):
        ispod = self.ispod.vrijednost()
        match self.op.tip:
            case T.MINUS: return -ispod
            case T.KONJ: return ispod.conjugate()
            case _: assert False, f'nepokriveni unarni operator {self.op}'

    def tac(self):
        rispod = yield from self.ispod.tac()
        yield [rrezultat:=next(rt.reg), '=', self.op.tip.value, rispod]
        return rrezultat

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

# DZ: Dodajte implicitno množenje (barem s i, tako da radi npr. 2+3i)
# DZ: Stritkno držanje IEEE-754 zahtijeva i ispravno tretiranje dijeljenja nulom
# (a ako želite biti sasvim compliant, i potenciranja poput 0^-1): učinite to!
