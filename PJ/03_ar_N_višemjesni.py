"""Aritmetika na N, s razlikom što su + i * lijevo asocirani višemjesni.
Uz implicitno množenje ako desni faktor počinje zagradom (npr. 2(3+1)=8).
Implementiran je i optimizator, baš kao u originalnom aritmetika_N.py."""


from pj import *


class T(TipoviTokena):
    PLUS, PUTA, OTVORENA, ZATVORENA = '+*()'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def optim(self): return self


def an(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# izraz -> izraz PLUS član | član
# član -> član PUTA faktor | faktor | član zagrade
# faktor -> BROJ | zagrade
# zagrade -> OTVORENA izraz ZATVORENA


class P(Parser):
    def izraz(self):
        trenutni = [self.član()]
        while self >> T.PLUS: trenutni.append(self.član())
        return Zbroj.ili_samo(trenutni)

    def član(self):
        trenutni = [self.faktor()]
        while self >> T.PUTA or self >= T.OTVORENA:
            trenutni.append(self.faktor())
        return Umnožak.ili_samo(trenutni)

    def faktor(self):
        if self >> T.BROJ: return self.zadnji
        elif self >> T.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(T.ZATVORENA)
            return u_zagradi
        else: raise self.greška()

    lexer = an
    start = izraz


nula, jedan = Token(T.BROJ, '0'), Token(T.BROJ, '1')


class Zbroj(AST('pribrojnici')):
    def vrijednost(self):
        return sum(x.vrijednost() for x in self.pribrojnici)
    
    def optim(self):
        opt_pribr = [x.optim() for x in self.pribrojnici]
        opt_pribr = [x for x in opt_pribr if x != nula]
        if not opt_pribr: return nula
        return Zbroj.ili_samo(opt_pribr)


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
        else: return Umnožak.ili_samo(opt_fakt)


def testiraj(izraz):
    print('-' * 60)
    stablo = P(izraz)
    izraz = izraz.strip()
    prikaz(stablo, 3)
    opt = stablo.optim()
    prikaz(opt, 2)
    mi = opt.vrijednost()
    try: Python = eval(izraz)
    except (SyntaxError, TypeError):
        print('Python ne zna ovo izračunati!', izraz, '==', mi)
    else:
        if mi == Python: print(izraz, '==', mi, 'OK')
        else: print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')

P.tokeniziraj('(2+3)*4')
testiraj('(2+3)*4')
testiraj('2 + (0+1*1*2)')
testiraj('2(3+5)')
testiraj('(1+1) (0+2+0) (0+1) (3+4)')
with očekivano(SintaksnaGreška): testiraj('(2+3)4')
with očekivano(SintaksnaGreška): testiraj('2\n37')
with očekivano(LeksičkaGreška): testiraj('2^3')
with očekivano(LeksičkaGreška): testiraj('3+00')
with očekivano(SintaksnaGreška): testiraj('+1')
with očekivano(LeksičkaGreška): testiraj('-1')
