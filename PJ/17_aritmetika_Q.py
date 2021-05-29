"""Aritmetika u skupu racionalnih brojeva, s detekcijom grešaka.
Po uzoru na https://web.math.pmf.unizg.hr/~veky/B/IP.k2p.17-09-08.pdf."""


from vepar import *


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV, NOVIRED = '+-*/=()\n'
    class BROJ(Token):
        def izračunaj(t, mem, v): return fractions.Fraction(t.sadržaj)
    class IME(Token):
        def izračunaj(t, mem, v):
            if t in mem: return mem[t]
            else: raise t.nedeklaracija(f'pri pridruživanju {v}')

def aq(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalnum():
            lex * {str.isalnum, '_'}
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

    def start(p) -> 'Program':
        pridruživanja = []
        while ime := p >= T.IME:
            p >> T.JEDNAKO
            pridruživanja.append((ime, p.izraz()))
            p >> T.NOVIRED
        return Program(pridruživanja)

    def izraz(p) -> 'član|Op':
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Op(op, t, p.član())
        return t

    def član(p) -> 'faktor|Op':
        t = p.faktor()
        while op := p >= {T.PUTA, T.KROZ}: t = Op(op, t, p.faktor())
        return t

    def faktor(p) -> 'Op|IME|BROJ|izraz':
        if op := p >= T.MINUS: return Op(op, nenavedeno, p.faktor())
        if elementarni := p >= {T.IME, T.BROJ}: return elementarni
        elif p >> T.OTV:
            u_zagradi = p.izraz()
            p >> T.ZATV
            return u_zagradi


class Program(AST):
    pridruživanja: '(IME,izraz)*'
    def izvrši(program):
        memorija = Memorija()
        for ime, vrijednost in program.pridruživanja:
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
