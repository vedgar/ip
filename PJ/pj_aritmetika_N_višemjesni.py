from pj import *


class AN(enum.Enum):
    BROJ = 1
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'


def an_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        else: yield lex.token(operator(AN, znak) or lex.greška())


### Beskontekstna gramatika: (+ i * proizvoljne mjesnosti)
# izraz -> izraz PLUS član | član
# član -> član PUTA faktor | faktor | član faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA

class Zbroj(AST('pribrojnici')): pass
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass

class ANParser(Parser):
    def izraz(self):
        trenutni = [self.član()]
        while self >> AN.PLUS:
            trenutni.append(self.član())
        if len(trenutni) == 1: return trenutni[0]
        else: return Zbroj(trenutni)

    def član(self):
        trenutni = [self.faktor()]
        while True:
            if self >> AN.PUTA:
                trenutni.append(self.faktor())
            elif self >> {AN.OTVORENA, AN.BROJ}:
                self.vrati()
                trenutni.append(self.faktor())
            else: break
        if len(trenutni) == 1: return trenutni[0]
        else: return Umnožak(trenutni)

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
        rezultat = 1
        for faktor in izraz.faktori:
            rezultat *= an_interpret(faktor)
        return rezultat
    elif izraz ** Potencija:
        return an_interpret(izraz.baza) ** an_interpret(izraz.eksponent)


def an_optim(izraz):
    nula, jedan = Token(AN.BROJ, '0'), Token(AN.BROJ, '1')
    if izraz ** AN.BROJ: return izraz
    elif izraz ** Zbroj:
        o_pribr = [an_optim(x) for x in izraz.pribrojnici]
        o_pribr = [x for x in o_pribr if x != nula]
        return Zbroj(o_pribr) if len(o_pribr) > 1 else o_pribr[0]
    elif izraz ** Umnožak:
        o_fakt = [an_optim(x) for x in izraz.faktori]
        if nula in o_fakt: return nula
        o_fakt = [x for x in o_fakt if x != jedan]
        return Umnožak(o_fakt) if len(o_fakt) > 1 else o_fakt[0]
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
    try: Python = eval(izraz.replace('^', '**'))
    except SyntaxError: print('Python ne zna ovo izračunati!', izraz, '==', mi)
    else:
        if mi == Python: print(izraz, '==', mi, 'OK')
        else: print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
