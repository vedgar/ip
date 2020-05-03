from pj import *
from backend import StrojSaStogom


class AN(enum.Enum):
    PLUS = '+'
    PUTA = '*'
    NA = '^'
    OTVORENA = '('
    ZATVORENA = ')'
    class BROJ(Token):
        def prevedi(self): yield ['PUSH', int(self.sadržaj)]


def an_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        else: yield lex.literal(AN)


### Beskontekstna gramatika:
# izraz -> izraz PLUS član | član
# član -> član PUTA faktor | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA


### Apstraktna sintaksna stabla
# AN.BROJ (Token): tip sadržaj
# Zbroj: lijevi desni
# Umnožak: lijevi desni
# Potencija: baza eksponent


class ANParser(Parser):
    def izraz(self):
        trenutni = self.član()
        while self >> AN.PLUS:
            sljedeći = self.član()
            trenutni = Zbroj(trenutni, sljedeći)
        return trenutni

    def član(self):
        trenutni = self.faktor()
        while self >> AN.PUTA: trenutni = Umnožak(trenutni, self.faktor())
        return trenutni

    def faktor(self):
        baza = self.baza()
        if self >> AN.NA: return Potencija(baza, self.faktor())
        else: return baza

    def baza(self):
        if self >= AN.BROJ: return self.čitaj()
        self.pročitaj(AN.OTVORENA)
        u_zagradi = self.izraz()
        self.pročitaj(AN.ZATVORENA)
        return u_zagradi

    start = izraz


class Binarni(AST('lijevo desno')):
    def prevedi(izraz):
        yield from izraz.lijevo.prevedi()
        yield from izraz.desno.prevedi()
        yield [izraz.opkod]

class Zbroj(Binarni): opkod = 'ADD'

class Umnožak(Binarni): opkod = 'MUL'

class Potencija(Binarni): opkod = 'POW'


def testiraj(izraz):
    print('-' * 60)
    print(izraz)
    stablo = ANParser.parsiraj(an_lex(izraz))
    prikaz(stablo, 8)

    vm = StrojSaStogom()
    for instrukcija in stablo.prevedi(): 
        vm.izvrši(*instrukcija)
        print(*instrukcija, '\t'*2, vm)
    print('rezultat:', vm.rezultat)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
    testiraj('1+2*3^4+0*5^6*7+8*9')
