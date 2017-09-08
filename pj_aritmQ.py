import fractions
from pj import *


class AQ(enum.Enum):
    BROJ, IME, NOVIRED = 3, 'neko_ime', '\n'
    PLUS, MINUS, PUTA, KROZ, JEDNAKO, OTV, ZATV = '+-*/=()'

def aq_lex(program):
    lex = Tokenizer(program)
    for znak in iter(lex.čitaj, ''):
        if znak.isalpha() or znak == '_':
            lex.zvijezda(identifikator)
            yield lex.token(AQ.IME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AQ.BROJ)
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
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
            if not self >> AQ.NOVIRED: break
        return Program(naredbe)

    def naredba(self):
        ime = self.pročitaj(AQ.IME)
        self.pročitaj(AQ.JEDNAKO)
        return Naredba(ime, self.izraz())

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


def izračunaj(izraz, memorija, pridruženo):
    if izraz ** AQ.BROJ: return fractions.Fraction(izraz.sadržaj)
    if izraz ** AQ.IME:
        if izraz in memorija: return memorija[izraz]
        poruka = 'Nedeklarirano {}, linija {}, stupac {}, pridruženo {}'
        raise SemantičkaGreška(poruka.format(izraz, *izraz.početak, pridruženo))
    l = izračunaj(izraz.lijevo, memorija, pridruženo)
    d = izračunaj(izraz.desno, memorija, pridruženo)
    if izraz.op ** AQ.PLUS: return l + d
    if izraz.op ** AQ.MINUS: return l - d
    if izraz.op ** AQ.PUTA: return l * d
    if d: return l / d
    poruka = 'Dijeljenje broja {} nulom, linija {}, stupac {}'
    raise GreškaIzvođenja(poruka.format(l, *izraz.op.početak))


class Program(AST('naredbe')):
    def detektiraj(self):
        memorija = {}
        for naredba in self.naredbe: memorija[naredba.ime] = izračunaj(
            naredba.vrijednost, memorija, naredba.ime)
            
class Naredba(AST('ime vrijednost')): pass
class Op(AST('op lijevo desno')): pass
