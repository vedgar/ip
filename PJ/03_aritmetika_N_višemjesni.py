"""Aritmetika na N, s razlikom što su + i * lijevo asocirani višemjesni.
Uz implicitno množenje ako desni faktor počinje zagradom (npr. 2(3+1)=8).
Implementiran je i optimizator, baš kao u originalnom aritmetika_N.py."""

from pj import *


class AN(enum.Enum):
    PLUS, PUTA, OTVORENA, ZATVORENA = '+*()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self


def an_lex(izraz):
    lex = Tokenizer(izraz)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit():
            if znak != '0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        else: yield lex.literal(AN)


### Beskontekstna gramatika
# izraz -> izraz PLUS član | član
# član -> član PUTA faktor | faktor | član zagrade
# faktor -> BROJ | zagrade
# zagrade -> OTVORENA izraz ZATVORENA


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
        if self >> AN.BROJ: return self.zadnji
        elif self >> AN.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AN.ZATVORENA)
            return u_zagradi
        else: raise self.greška()

    start = izraz


nula, jedan = Token(AN.BROJ, '0'), Token(AN.BROJ, '1')


class Zbroj(AST('pribrojnici')):
    def vrijednost(self):
        return sum(x.vrijednost() for x in self.pribrojnici)
    
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


def testiraj(izraz):
    print('-' * 60)
    stablo = ANParser.parsiraj(an_lex(izraz))
    izraz = izraz.strip()
    prikaz(stablo, 6)
    opt = stablo.optim()
    prikaz(opt, 6)
    mi = opt.vrijednost()
    try: Python = eval(izraz)
    except (SyntaxError, TypeError):
        print('Python ne zna ovo izračunati!', izraz, '==', mi)
    else:
        if mi == Python: print(izraz, '==', mi, 'OK')
        else: print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')

if __name__ == '__main__':
    testiraj('(2+3)*4')
    testiraj('2+(0+1*1*2)')
    testiraj('2(3+5)\n')
    testiraj('(1+1)(0+2+0)(0+1)(3+4)')
    with očekivano(SintaksnaGreška): testiraj('(2+3)4')
    with očekivano(SintaksnaGreška): testiraj('2\n37')
    with očekivano(LeksičkaGreška): testiraj('2^3')
