"""Izračunavanje aritmetičkih izraza nad skupom prirodnih brojeva.

Podržani operatori su + (zbrajanje), * (množenje) i ^ (potenciranje).
Svi operatori su binarni i desno asocirani, radi jednostavnosti parsera.
Zbrajanju i množenju je svejedno jer su to asocijativne operacije,
a potenciranje se obično po dogovoru shvaća desno asocirano (2^3^2=2^9=512).
Zagrade su dozvoljene, ali često nisu nužne. Prioritet je uobičajen (^, *, +).

Implementiran je i jednostavni optimizator, koji detektira sve nule i
jedinice u izrazima, te pojednostavljuje izraze koji ih sadrže
(x+0=0+x=x*1=1*x=x^1=x, x^0=1^x=1, x*0=0*x=0^x=0
  - ovo zadnje pravilo se uvijek primjenjuje nakon x^0=1, jer 0^0=1).
"""


from pj import *


class AN(enum.Enum):
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self
        def prevedi(self): yield 'PUSH', self.vrijednost()


def an_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        else: yield lex.literal(AN)


### Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član PLUS izraz | član
# član -> faktor PUTA član | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA


### Apstraktna sintaksna stabla
# Zbroj: pribrojnici
# Umnožak: faktori
# Potencija: baza eksponent


class ANParser(Parser):
    def izraz(self):
        prvi = self.član()
        if self >> AN.PLUS:
            drugi = self.izraz()
            return Zbroj([prvi, drugi])
        else:
            return prvi

    def član(self):
        faktor = self.faktor()
        if self >> AN.PUTA: return Umnožak([faktor, self.član()])
        else: return faktor

    def faktor(self):
        baza = self.baza()
        if self >> AN.NA: return Potencija(baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> AN.BROJ: return self.zadnji
        elif self >> AN.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AN.ZATVORENA)
            return u_zagradi
        else: raise self.greška()

    start = izraz


nula = Token(AN.BROJ, '0')
jedan = Token(AN.BROJ, '1')


class Zbroj(AST('pribrojnici')):
    def vrijednost(izraz):
        a, b = izraz.pribrojnici
        return a.vrijednost() + b.vrijednost()

    def optim(izraz):
        a, b = izraz.pribrojnici
        a, b = a.optim(), b.optim()
        if a == nula: return b
        elif b == nula: return a
        else: return Zbroj([a, b])

    def prevedi(izraz):
        a, b = izraz.pribrojnici
        yield from a.prevedi()
        yield from b.prevedi()
        yield 'ADD',


class Umnožak(AST('faktori')):
    def vrijednost(izraz):
        a, b = izraz.faktori
        return a.vrijednost() * b.vrijednost()

    def optim(izraz):
        a, b = izraz.faktori
        a, b = a.optim(), b.optim()
        if a == jedan: return b
        elif b == jedan: return a
        elif nula in {a, b}: return nula
        else: return Umnožak([a, b])

    def prevedi(izraz):
        a, b = izraz.faktori
        yield from a.prevedi()
        yield from b.prevedi()
        yield 'MUL',


class Potencija(AST('baza eksponent')):
    def vrijednost(izraz):
        return izraz.baza.vrijednost() ** izraz.eksponent.vrijednost()

    def optim(izraz):
        b, e = izraz.baza.optim(), izraz.eksponent.optim()
        if e == nula: return jedan
        elif b == nula: return nula  # 0^0 je gore, jer prepoznamo sve nule
        elif jedan in {b, e}: return b
        else: return Potencija(b, e)

    def prevedi(izraz):
        yield from izraz.baza.prevedi()
        yield from izraz.eksponent.prevedi()
        yield 'POW',


def testiraj(izraz):
    print('-' * 60)
    print(izraz)
    stablo = ANParser.parsiraj(an_lex(izraz))
    prikaz(stablo, 6)
    opt = stablo.optim()
    prikaz(opt, 6)
    mi = opt.vrijednost()
    Python = eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)
    for instrukcija in opt.prevedi(): print('\t', *instrukcija)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
    with očekivano(LeksičkaGreška): testiraj('2 3')
    with očekivano(SintaksnaGreška): testiraj('2+')
    with očekivano(SintaksnaGreška): testiraj('(2+3)45')
