from pj import *
import fractions  # kao backend


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV, NOVIRED = '+-*/=()\n'
    class BROJ(Token):
        def izračunaj(self, mem, v): return fractions.Fraction(self.sadržaj)
    class IME(Token):
        def izračunaj(self, mem, v):
            if self in mem: return mem[self]
            else: raise self.nedeklaracija('pri pridruživanju {}'.format(v))

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
        while ime := self >> T.IME:
            self.pročitaj(T.JEDNAKO)
            što = self.izraz()
            self.pročitaj(T.NOVIRED)
            pridruživanja.append((ime, što))
        return Program(pridruživanja)

    def naredba(self):
        ime = self.pročitaj(T.IME)
        self.pročitaj(T.JEDNAKO)
        pridruženo = self.izraz()
        self.pročitaj(T.NOVIRED)
        return ime, pridruženo

    def izraz(self):
        t = self.član()
        while op := self >> {T.PLUS, T.MINUS}: t = Op(op, t, self.član())
        return t

    def član(self):
        t = self.faktor()
        while op := self >> {T.PUTA, T.KROZ}: t = Op(op, t, self.faktor())
        return t

    def faktor(self):
        if op := self >> T.MINUS: return Op(op, nenavedeno, self.faktor())
        if elementarni := self >> {T.IME, T.BROJ}: return elementarni
        self.pročitaj(T.OTV)
        u_zagradi = self.izraz()
        self.pročitaj(T.ZATV)
        return u_zagradi


class Program(AST('pridruživanja')):
    def izvrši(self):
        memorija = Memorija()
        for ime, vrijednost in self.pridruživanja:
            memorija[ime] = vrijednost.izračunaj(memorija, ime)
        return memorija


class Op(AST('op lijevo desno')):
    def izračunaj(self, memorija, v):
        if self.lijevo is nenavedeno: l = 0
        else: l = self.lijevo.izračunaj(memorija, v)
        o, d = self.op, self.desno.izračunaj(memorija, v)
        if o ^ T.PLUS: return l + d
        elif o ^ T.MINUS: return l - d
        elif o ^ T.PUTA: return l * d
        elif d: return l / d
        else: raise o.iznimka('dijeljenje nulom pri pridruživanju {}'.format(v))


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
