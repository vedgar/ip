import fractions
from pj import *


class AQ(enum.Enum):
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV, NOVIRED = '+-*/=()\n'

    class BROJ(Token):
        def izračunaj(self, memorija, čemu):
            return fractions.Fraction(self.sadržaj)

    class IME(Token):
        def izračunaj(self, memorija, čemu):
            try: return memorija[self]
            except KeyError: self.nedeklaracija('pridruženo {}'.format(čemu))


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
        elif znak.isspace(): lex.token(E.PRAZNO)
        else: yield lex.token(operator(AQ, znak) or lex.greška())


# start = program -> '' | naredba | naredba NOVIRED program
# naredba -> IME JEDNAKO izraz
# izraz -> član | izraz PLUS član | izraz MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | OTV izraz ZATV


class AQParser(Parser):
    def start(self):
        naredbe = []
        while True:
            if self >= AQ.IME:
                naredbe.append(self.naredba())
                self.pročitaj(AQ.NOVIRED)
            elif self >> E.KRAJ: return Program(naredbe)
            else: self.greška()

    def naredba(self):
        ime = self.pročitaj(AQ.IME)
        self.pročitaj(AQ.JEDNAKO)
        pridruženo = self.izraz()
        return Naredba(ime, pridruženo)

    def izraz(self):
        trenutni = self.član()
        while self >> {AQ.PLUS, AQ.MINUS}:
            operator = self.zadnji
            novi = self.član()
            trenutni = Op(self.zadnji, trenutni, novi)
        return trenutni

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
    def detektiraj(self):
        memorija = {}
        for naredba in self.naredbe: naredba.izvrši(memorija)


class Naredba(AST('ime vrijednost')):
    def izvrši(self, memorija):
        memorija[self.ime] = self.vrijednost.izračunaj(memorija, self.ime)


class Op(AST('op lijevo desno')):
    def izračunaj(self, memorija, pridruženo):
        l = self.lijevo.izračunaj(memorija, pridruženo)
        d = self.desno.izračunaj(memorija, pridruženo)
        o = self.op
        if o ** AQ.PLUS: return l + d
        if o ** AQ.MINUS: return l - d
        if o ** AQ.PUTA: return l * d
        if d: return l / d
        poruka = 'Dijeljenje broja {} nulom, linija {}, stupac {}'
        raise GreškaIzvođenja(poruka.format(l, *o.početak))


if __name__ == '__main__':
    program = '''\
        a = 3 / 7
        b = a + 3
        c = b - b
        b = a * f
        d = a / c
        e = 3 / 0
    '''
    AQParser.parsiraj(aq_lex(program)).detektiraj()
