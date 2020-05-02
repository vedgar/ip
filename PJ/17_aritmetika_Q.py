import fractions
from pj import *


class AQ(enum.Enum):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV, NOVIRED = '+-*/=()\n'

    class BROJ(Token):
        def izračunaj(self, memorija, čemu):
            return fractions.Fraction(self.sadržaj)

    class IME(Token):
        def izračunaj(self, memorija, v):
            try: return memorija[self]
            except KeyError: raise self.nedeklaracija('pridruženo {}'.format(v))


def aq_lex(program):
    lex = Tokenizer(program)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AQ.BROJ)
        elif identifikator(znak):
            lex.zvijezda(identifikator)
            yield lex.token(AQ.IME)
        elif znak == '\n': yield lex.token(AQ.NOVIRED)
        elif znak.isspace(): lex.zanemari()
        else: yield lex.literal(AQ)


# start = program -> '' | naredba | naredba program
# naredba -> IME JEDNAKO izraz NOVIRED
# izraz -> član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | OTV izraz ZATV


class AQParser(Parser):
    def start(self):
        naredbe = []
        while self >= AQ.IME: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        ime = self.pročitaj(AQ.IME)
        self.pročitaj(AQ.JEDNAKO)
        pridruženo = self.izraz()
        self.pročitaj(AQ.NOVIRED)
        return Pridruživanje(ime, pridruženo)

    def izraz(self):
        t = self.član()
        while self >> {AQ.PLUS, AQ.MINUS}: t = Op(self.zadnji, t, self.član())
        return t

    def član(self):
        t = self.faktor()
        while self >> {AQ.PUTA, AQ.KROZ}: t = Op(self.zadnji, t, self.faktor())
        return t

    def faktor(self):
        if self >> {AQ.IME, AQ.BROJ}: return self.zadnji
        self.pročitaj(AQ.OTV)
        u_zagradi = self.izraz()
        self.pročitaj(AQ.ZATV)
        return u_zagradi


class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe: naredba.izvrši(memorija)
        return memorija


class Pridruživanje(AST('ime vrijednost')):
    def izvrši(self, memorija):
        memorija[self.ime] = self.vrijednost.izračunaj(memorija, self.ime)


class Op(AST('operator lijevo desno')):
    def izračunaj(self, memorija, pridruženo):
        l = self.lijevo.izračunaj(memorija, pridruženo)
        d = self.desno.izračunaj(memorija, pridruženo)
        o = self.operator
        if o ^ AQ.PLUS: return l + d
        elif o ^ AQ.MINUS: return l - d
        elif o ^ AQ.PUTA: return l * d
        elif d: return l / d
        raise o.iznimka('dijeljenje nulom (pridruženo {})'.format(pridruženo))


if __name__ == '__main__':
    program = '''\
        a = 3 / 7
        b = a + 3
        c = b - b
        b = a * a
        d = a / (c + 1)
        e = 3 / 3
    '''
    ast = AQParser.parsiraj(aq_lex(program))
    prikaz(ast, 3)
    for ime, vrijednost in ast.izvrši().items():
        print(ime.sadržaj, vrijednost, sep='=')
