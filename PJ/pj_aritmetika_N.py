from pj import *


class AN(enum.Enum):
    BROJ = 1
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'


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

class Zbroj(AST('pribrojnici')): pass
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass

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


def an_interpret(izraz):
    if izraz ** AN.BROJ: return int(izraz.sadržaj)
    elif izraz ** Zbroj: return sum(map(an_interpret, izraz.pribrojnici))
    elif izraz ** Umnožak:
        f1, f2 = izraz.faktori
        return an_interpret(f1) * an_interpret(f2)
    elif izraz ** Potencija:
        return an_interpret(izraz.baza) ** an_interpret(izraz.eksponent)


def an_optim(izraz):
    nula, jedan = Token(AN.BROJ, '0'), Token(AN.BROJ, '1')
    if izraz ** AN.BROJ: return izraz
    elif izraz ** Zbroj:
        o1, o2 = map(an_optim, izraz.pribrojnici)
        if o1 == nula: return o2
        elif o2 == nula: return o1
        else: return Zbroj([o1, o2])
    elif izraz ** Umnožak:
        o1, o2 = map(an_optim, izraz.faktori)
        if o1 == jedan: return o2
        elif o2 == jedan: return o1
        elif nula in {o1, o2}: return nula
        else: return Umnožak([o1, o2])
    elif izraz ** Potencija:
        o_baza = an_optim(izraz.baza)
        o_eksponent = an_optim(izraz.eksponent)
        if o_eksponent == nula: return jedan
        elif o_baza == nula: return nula  # 0^0 je gore, jer prepoznamo sve nule
        elif jedan in {o_baza, o_eksponent}: return o_baza
        else: return Potencija(o_baza, o_eksponent)


def testiraj(izraz):
    stablo = ANParser.parsiraj(an_lex(izraz))
    opt = an_optim(stablo)
    print(stablo, opt, sep='\n')
    mi = an_interpret(opt)
    Python = eval(izraz.replace('^', '**'))
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
