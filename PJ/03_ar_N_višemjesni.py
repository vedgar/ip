"""Aritmetika na N, s razlikom što su + i * lijevo asocirani višemjesni.
Uz implicitno množenje ako desni faktor počinje zagradom (npr. 2(3+1)=8).
Implementiran je i optimizator, baš kao u originalnom aritmetika_N.py."""


from vepar import *
from backend import Python_eval


class T(TipoviTokena):
    PLUS, PUTA, OTVORENA, ZATVORENA = '+*()'
    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)
        def optim(t): return t

@lexer
def an(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# izraz -> član | izraz PLUS član
# član -> faktor | član PUTA faktor | član zagrade
# faktor -> BROJ | zagrade
# zagrade -> OTVORENA izraz ZATVORENA


class P(Parser):
    def izraz(p) -> 'Zbroj|član':
        trenutni = [p.član()]
        while p >= T.PLUS: trenutni.append(p.član())
        return Zbroj.ili_samo(trenutni)

    def član(p) -> 'Umnožak|faktor':
        trenutni = [p.faktor()]
        while p >= T.PUTA or p > T.OTVORENA:
            trenutni.append(p.faktor())
        return Umnožak.ili_samo(trenutni)

    def faktor(p) -> 'BROJ|izraz':
        if broj := p >= T.BROJ: return broj
        elif p >> T.OTVORENA:
            u_zagradi = p.izraz()
            p >> T.ZATVORENA
            return u_zagradi


nula, jedan = Token(T.BROJ, '0'), Token(T.BROJ, '1')


class Zbroj(AST):
    pribrojnici: 'izraz*'

    def vrijednost(zbroj):
        return sum(pribrojnik.vrijednost() for pribrojnik in zbroj.pribrojnici)
    
    def optim(zbroj):
        opt_pribr = [pribrojnik.optim() for pribrojnik in zbroj.pribrojnici]
        opt_pribr = [x for x in opt_pribr if x != nula]
        if not opt_pribr: return nula
        return Zbroj.ili_samo(opt_pribr)


class Umnožak(AST):
    faktori: 'izraz*'

    def vrijednost(umnožak):
        return math.prod(faktor.vrijednost() for faktor in umnožak.faktori)

    def optim(umnožak):
        opt_fakt = [faktor.optim() for faktor in umnožak.faktori]
        if nula in opt_fakt: return nula
        opt_fakt = [x for x in opt_fakt if x != jedan]
        if not opt_fakt: return jedan
        else: return Umnožak.ili_samo(opt_fakt)


def testiraj(izraz):
    print('-' * 60)
    prikaz(stablo := P(izraz), 3)
    prikaz(opt := stablo.optim(), 3)
    mi = opt.vrijednost()
    try: Python = Python_eval(izraz)
    except SyntaxError: return print('Python ovo ne zna!', izraz, '==', mi)
    if mi == Python: return print(izraz, '==', mi, 'OK')
    print(izraz, 'mi:', mi, 'Python:', Python, 'krivo')
    raise ArithmeticError

an('(2+3)*4')
testiraj('(2+3)*4')
testiraj('2 + (0+1*1*2)')
testiraj('2(3+5)')
testiraj('(1+1) (0+2+0) (0+1) (3+4)')
with SintaksnaGreška: testiraj('(2+3)4')
with SintaksnaGreška: testiraj('2\t37')
with LeksičkaGreška: testiraj('2^3')
with LeksičkaGreška: testiraj('3+00')
with SintaksnaGreška: testiraj('+1')
with LeksičkaGreška: testiraj('-1')
