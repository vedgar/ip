"""Izračunavanje aritmetičkih izraza nad skupom prirodnih brojeva.

Podržani operatori su + (zbrajanje), * (množenje) i ^ (potenciranje).
Svi operatori su binarni i desno asocirani, radi jednostavnosti parsera.
Zbrajanju i množenju je svejedno jer su to asocijativne operacije,
a potenciranje se obično po dogovoru shvaća desno asocirano (2^3^2=2^9=512).
Zagrade su dozvoljene, ali često nisu nužne. Prioritet je uobičajen (^, *, +).

Implementiran je i jednostavni optimizator, koji detektira sve nule i
jedinice u izrazima, te pojednostavljuje izraze koji ih sadrže
(x+0=0+x=x*1=1*x=x^1=x, x^0=1^x=1, x*0=0*x=0^x=0
  - ovo zadnje pravilo se uvijek primjenjuje nakon x^0=1, jer 0^0=1)."""


from vepar import *
from backend import StrojSaStogom, Python_eval


class T(TipoviTokena):
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self
        def prevedi(self): yield ['PUSH', self.vrijednost()]


def an(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


### Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član PLUS izraz | član
# član -> faktor PUTA član | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA

### Apstraktna sintaksna stabla
# izraz: BROJ: Token
#        Zbroj: pribrojnici:[izraz] (duljine 2)
#        Umnožak: faktori:[izraz] (duljine 2)
#        Potencija: baza:izraz eksponent:izraz


class P(Parser):
    def izraz(self):
        prvi = self.član()
        if self >= T.PLUS:
            drugi = self.izraz()
            return Zbroj([prvi, drugi])
        else:
            return prvi

    def član(self):
        faktor = self.faktor()
        if self >= T.PUTA: return Umnožak([faktor, self.član()])
        else: return faktor

    def faktor(self):
        baza = self.baza()
        if self >= T.NA: return Potencija(baza, self.faktor())
        else: return baza

    def baza(self):
        if broj := self >= T.BROJ: return broj
        elif self >> T.OTVORENA:
            u_zagradi = self.izraz()
            self >> T.ZATVORENA
            return u_zagradi

    lexer = an
    start = izraz


nula = Token(T.BROJ, '0')
jedan = Token(T.BROJ, '1')


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
        for pribrojnik in izraz.pribrojnici: yield from pribrojnik.prevedi()
        yield ['ADD']


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
        for faktor in izraz.faktori: yield from faktor.prevedi()
        yield ['MUL']


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
        yield ['POW']


def testiraj(izraz):
    print('-' * 60)
    print(izraz)
    prikaz(stablo := P(izraz))
    prikaz(opt := stablo.optim())

    vm = StrojSaStogom()
    for instrukcija in opt.prevedi(): 
        vm.izvrši(*instrukcija)
        print(*instrukcija, '\t'*2, vm)
    print('rezultat:', vm.rezultat)

    mi = opt.vrijednost()
    Python = Python_eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: 
        print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')
        raise ArithmeticError


P.tokeniziraj('(2+3)*4^1')
testiraj('(2+3)*4^1')
testiraj('2^0^0^0^0')
testiraj('2+(0+1*1*2)')
testiraj('1+2*3^4+0*5^6*7+8*9')
with LeksičkaGreška: testiraj('2 3')
with SintaksnaGreška: testiraj('2+')
with SintaksnaGreška: testiraj('(2+3)45')
with LeksičkaGreška: testiraj('3+02')
