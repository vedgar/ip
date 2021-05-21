"""Aritmetika u skupu racionalnih brojeva, s detekcijom grešaka.
Po uzoru na https://web.math.pmf.unizg.hr/~veky/B/IP.k2p.17-09-08.pdf."""


from vepar import *
import fractions  # kao backend


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV, NOVIRED = '+-*/=()\n'
    class BROJ(Token):
        def izračunaj(self, mem, v): return fractions.Fraction(self.sadržaj)
    class IME(Token):
        def izračunaj(self, mem, v):
            if self in mem: return mem[self]
            else: raise self.nedeklaracija(f'pri pridruživanju {v}')

def aq(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif identifikator(znak):
            lex.zvijezda(identifikator)
            yield lex.token(T.IME)
        elif znak.isspace() and znak != '\n': lex.zanemari()
        else: yield lex.literal(T)


### BKG
# program -> '' | naredba | naredba program
# naredba -> IME JEDNAKO izraz NOVIRED
# izraz -> član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> MINUS faktor | BROJ | IME | OTV izraz ZATV

### AST
# Program: pridruživanja:[(IME,izraz)]
# izraz: BROJ: Token
#        IME: Token
#        Op: op:PLUS|MINUS|PUTA|KROZ lijevo:izraz? desno:izraz


class P(Parser):
    lexer = aq

    def start(self):
        pridruživanja = []
        while ime := self >= T.IME:
            self >> T.JEDNAKO
            pridruživanja.append((ime, self.izraz()))
            self >> T.NOVIRED
        return Program(pridruživanja)

    def izraz(self):
        t = self.član()
        while op := self >= {T.PLUS, T.MINUS}: t = Op(op, t, self.član())
        return t

    def član(self):
        t = self.faktor()
        while op := self >= {T.PUTA, T.KROZ}: t = Op(op, t, self.faktor())
        return t

    def faktor(self):
        if op := self >= T.MINUS: return Op(op, nenavedeno, self.faktor())
        if elementarni := self >= {T.IME, T.BROJ}: return elementarni
        elif self >> T.OTV:
            u_zagradi = self.izraz()
            self >> T.ZATV
            return u_zagradi


class Program(AST):
    pridruživanja: '(IME,izraz)*'
    def izvrši(self):
        memorija = Memorija()
        for ime, vrijednost in self.pridruživanja:
            memorija[ime] = vrijednost.izračunaj(memorija, ime)
        return memorija


class Op(AST):
    op: 'T'
    lijevo: 'izraz?'
    desno: 'izraz'
    def izračunaj(self, memorija, v):
        if self.lijevo is nenavedeno: l = 0  # unarni minus: -x = 0-x
        else: l = self.lijevo.izračunaj(memorija, v)
        o, d = self.op, self.desno.izračunaj(memorija, v)
        if o ^ T.PLUS: return l + d
        elif o ^ T.MINUS: return l - d
        elif o ^ T.PUTA: return l * d
        elif d: return l / d
        else: raise o.iznimka(f'dijeljenje nulom pri pridruživanju {v}')


# Moramo staviti backslash na početak jer inače program počinje novim redom.
ast = P('''\
    a = 3 / 7
    b = a + 3
    c = b - b
    b = a * -a
    d = a / (c + 1)
    e = -3 / 3
''')
prikaz(ast)
for ime, vrijednost in ast.izvrši(): print(ime.sadržaj, vrijednost, sep='=')
