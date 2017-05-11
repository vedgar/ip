from plutil import *


class Ar(enum.Enum):
    BROJ = 1
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'


def ar_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(Ar.BROJ)
        else: yield lex.token(operator(Ar, znak) or lex.greška())


# Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član PLUS izraz | član
# član -> potencija PUTA član | potencija
# potencija -> baza NA potencija | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA

class Zbroj(AST('pribrojnici')): pass
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass

class ArParser(Parser):
    def izraz(self):
        član = self.član()
        dalje = self.granaj(E.KRAJ, Ar.PLUS, Ar.ZATVORENA)
        if dalje ** Ar.PLUS:
            self.pročitaj(Ar.PLUS)
            return Zbroj([član, self.izraz()])
        return član

    def član(self):
        potencija = self.potencija()
        dalje = self.granaj(E.KRAJ, Ar.PUTA, Ar.PLUS, Ar.ZATVORENA)
        if dalje ** Ar.PUTA:
            self.pročitaj(Ar.PUTA)
            return Umnožak([potencija, self.član()])
        return potencija

    def potencija(self):
        baza = self.baza()
        dalje = self.granaj(E.KRAJ, Ar.NA, Ar.PUTA, Ar.PLUS, Ar.ZATVORENA)
        if dalje ** Ar.NA:
            self.pročitaj(Ar.NA)
            return Potencija(baza, self.potencija())
        else: return baza

    def baza(self):
        if self.granaj(Ar.BROJ, Ar.OTVORENA) ** Ar.OTVORENA:
            self.pročitaj(Ar.OTVORENA)
            u_zagradi = self.izraz()
            self.pročitaj(Ar.ZATVORENA)
            return u_zagradi            
        return self.pročitaj(Ar.BROJ)

def ar_parse(znakovi):
    parser = ArParser(ar_lex(znakovi))
    rezultat = parser.izraz()
    parser.pročitaj(E.KRAJ)
    return rezultat


def ar_interpret(izraz):
    if isinstance(izraz, Token): return int(izraz.sadržaj)
    elif isinstance(izraz, Zbroj):
        return sum(map(ar_interpret, izraz.pribrojnici))
    elif isinstance(izraz, Umnožak):
        f1, f2 = map(ar_interpret, izraz.faktori)
        return f1 * f2
    elif isinstance(izraz, Potencija):
        return ar_interpret(izraz.baza) ** ar_interpret(izraz.eksponent)


def ar_optimize(izraz):
    nula, jedan = Token(Ar.BROJ, '0'), Token(Ar.BROJ, '1')
    if izraz ** Ar.BROJ: return izraz
    elif izraz ** Zbroj:
        o1, o2 = map(ar_optimize, izraz.pribrojnici)
        if o1 == nula: return o2
        elif o2 == nula: return o1
        else: return Zbroj([o1, o2])
    elif izraz ** Umnožak:
        o1, o2 = map(ar_optimize, izraz.faktori)
        if o1 == jedan: return o2
        elif o2 == jedan: return o1
        elif nula in (o1, o2): return nula
        else: return Umnožak([o1, o2])
    elif izraz ** Potencija:
        o_baza = ar_optimize(izraz.baza)
        o_eksponent = ar_optimize(izraz.eksponent)
        if o_eksponent == nula: return jedan
        elif o_baza == nula: return nula  # 0^0 je gore, jer prepoznamo sve nule
        elif jedan in (o_baza, o_eksponent): return o_baza
        else: return Potencija(baza=o_baza, eksponent=o_eksponent)


def testiraj(izraz):
    stablo = ar_parse(izraz)
    opt = ar_optimize(stablo)
    print(stablo, opt, sep='\n')
    mi = ar_interpret(opt)
    Python = eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
