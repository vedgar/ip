from pj import *


class AN(enum.Enum):
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self


def an_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        else: yield lex.token(operator(AN, znak) or lex.greška())


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
        član = self.član()
        if self >> AN.PLUS: return Zbroj([član, self.izraz()])
        else: return član

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
        else: self.greška()

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


class Potencija(AST('baza eksponent')):
    def vrijednost(izraz):
        return izraz.baza.vrijednost() ** izraz.eksponent.vrijednost()

    def optim(izraz):
        a = b, e = izraz.baza.optim(), izraz.eksponent.optim()
        if e == nula: return jedan
        elif b == nula: return nula  # 0^0 je gore, jer prepoznamo sve nule
        elif jedan in a: return b
        else: return Potencija(*a)


def testiraj(izraz):
    stablo = ANParser.parsiraj(an_lex(izraz))
    opt = stablo.optim()
    print(stablo, opt, sep='\n')
    mi = opt.vrijednost()
    Python = eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
