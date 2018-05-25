"""Aritmetika na N, s jedinom razlikom što su + i * lijevo asocirani višemjesni.
Implementiran je i optimizator, baš kao u originalnom aritmetikaN.py."""

from pj import *


class AN(enum.Enum):
    PLUS, PUTA, NA, OTVORENA, ZATVORENA = '+*^()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self


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


nula, jedan = Token(AN.BROJ, '0'), Token(AN.BROJ, '1')


class Zbroj(AST('pribrojnici')):
    def vrijednost(self): return sum(x.vrijednost() for x in self.pribrojnici)
    
    def optim(self):
        opt_pribr = [x.optim() for x in self.pribrojnici]
        opt_pribr = [x for x in opt_pribr if x != nula]
        if not opt_pribr: return nula
        elif len(opt_pribr) == 1: return opt_pribr[0]
        else: return Zbroj(opt_pribr)


class Umnožak(AST('faktori')):
    def vrijednost(self):
        rezultat = 1
        for faktor in self.faktori: rezultat *= faktor.vrijednost()
        return rezultat

    def optim(self):
        opt_fakt = [x.optim() for x in self.faktori]
        if nula in opt_fakt: return nula
        opt_fakt = [x for x in opt_fakt if x != jedan]
        if not opt_fakt: return jedan
        elif len(opt_fakt) == 1: return opt_fakt[0]
        else: return Umnožak(opt_fakt)


class Potencija(AST('baza eksponent')):
    def vrijednost(self):
        return self.baza.vrijednost() ** self.eksponent.vrijednost()

    def optim(self):
        opt_baza = self.baza.optim()
        opt_eksponent = self.eksponent.optim()
        if opt_eksponent == nula: return jedan
        elif opt_baza == nula: return nula  # 0^0 je gore; prepoznamo sve nule
        elif jedan in {opt_baza, opt_eksponent}: return opt_baza
        else: return Potencija(opt_baza, opt_eksponent)


class ANParser(Parser):
    def izraz(self):
        trenutni = [self.član()]
        while self >> AN.PLUS: trenutni.append(self.član())
        return trenutni[0] if len(trenutni) == 1 else Zbroj(trenutni)

    def član(self):
        trenutni = [self.faktor()]
        while self >> AN.PUTA or self >= AN.OTVORENA:
            trenutni.append(self.faktor())
        return trenutni[0] if len(trenutni) == 1 else Umnožak(trenutni)

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


def testiraj(izraz):
    stablo = ANParser.parsiraj(an_lex(izraz))
    opt = stablo.optim()
    print(stablo, opt, sep='\n')
    mi = opt.vrijednost()
    try: Python = eval(izraz.replace('^', '**'))
    except (SyntaxError, TypeError):
        print('Python ne zna ovo izračunati!', izraz, '==', mi)
    else:
        if mi == Python: print(izraz, '==', mi, 'OK')
        else: print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')

if __name__ == '__main__':
    testiraj('(2+3)*4^1')
    testiraj('2^0^0^0^0')
    testiraj('2+(0+1*1*2)')
    testiraj('2(3+5)')
