from pj import *


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


### Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član PLUS izraz | član
# član -> faktor PUTA član | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA

class Zbroj(AST('pribrojnici')): pass
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass

class ArParser(Parser):
    def izraz(self):
        član = self.član()
        if self.čitaj() ** Ar.PLUS: return Zbroj([član, self.izraz()])
        self.vrati()
        return član

    def član(self):
        faktor = self.faktor()
        if self.čitaj() ** Ar.PUTA: return Umnožak([faktor, self.član()])
        self.vrati()
        return faktor

    def faktor(self):
        baza = self.baza()
        if self.čitaj() ** Ar.NA: return Potencija(baza, self.faktor())
        self.vrati()
        return baza

    def baza(self):
        prvi = self.čitaj()
        if prvi ** Ar.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(Ar.ZATVORENA)
            return u_zagradi
        elif prvi ** Ar.BROJ: return prvi

def ar_parse(znakovi):
    parser = ArParser(ar_lex(znakovi))
    rezultat = parser.izraz()
    parser.pročitaj(E.KRAJ)
    return rezultat


def ar_interpret(izraz):
    if izraz ** Ar.BROJ: return int(izraz.sadržaj)
    elif izraz ** Zbroj: return sum(map(ar_interpret, izraz.pribrojnici))
    elif izraz ** Umnožak:
        f1, f2 = map(ar_interpret, izraz.faktori)
        return f1 * f2
    elif izraz ** Potencija:
        return ar_interpret(izraz.baza) ** ar_interpret(izraz.eksponent)


def ar_optim(izraz):
    nula, jedan = Token(Ar.BROJ, '0'), Token(Ar.BROJ, '1')
    if izraz ** Ar.BROJ: return izraz
    elif izraz ** Zbroj:
        o1, o2 = map(ar_optim, izraz.pribrojnici)
        if o1 == nula: return o2
        elif o2 == nula: return o1
        else: return Zbroj([o1, o2])
    elif izraz ** Umnožak:
        o1, o2 = map(ar_optim, izraz.faktori)
        if o1 == jedan: return o2
        elif o2 == jedan: return o1
        elif nula in {o1, o2}: return nula
        else: return Umnožak([o1, o2])
    elif izraz ** Potencija:
        o_baza = ar_optim(izraz.baza)
        o_eksponent = ar_optim(izraz.eksponent)
        if o_eksponent == nula: return jedan
        elif o_baza == nula: return nula  # 0^0 je gore, jer prepoznamo sve nule
        elif jedan in {o_baza, o_eksponent}: return o_baza
        else: return Potencija(o_baza, o_eksponent)


def testiraj(izraz):
    stablo = ar_parse(izraz)
    opt = ar_optim(stablo)
    print(stablo, opt, sep='\n')
    mi = ar_interpret(opt)
    Python = eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
