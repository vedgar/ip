"""Lambda-račun: zadatak s kolokvija 28. lipnja 2019.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2.19-06-28.pdf"""


from vepar import *


class T(TipoviTokena):
    LAMBDA, TOČKA, OTV, ZATV = 'λ.()'
    class SLOVO(Token):
        def slobodne(t): return {t}

lambde = {'λ', '^'}

@lexer
def λex(l):
    for znak in l:
        if znak.isspace(): l.zanemari()
        elif znak in lambde:
            yield l.token(T.LAMBDA)
            if l > lambde: raise l.greška('λ nije slovo!')
            elif l > str.isspace: raise l.greška('nedopušten razmak između lambde i vezanog slova')
        elif znak.isalpha(): yield l.token(T.SLOVO)
        else: yield l.literal(T)

### Beskontekstna gramatika:
# izraz -> član | LAMBDA slova TOČKA izraz
# slova -> SLOVO | SLOVO slova
# član -> faktor | član faktor
# faktor -> OTV izraz ZATV | SLOVO

# Oneliner BKG: start -> (LAMBDA SLOVO+ TOČKA)* (OTV start ZATV | SLOVO)+

class P(Parser):
    def izraz(p) -> 'aps|član':
        if p >= T.LAMBDA: return p.aps()
        return p.član()

    def aps(p) -> 'izraz|Apstrakcija':
        if p >= T.TOČKA: return p.izraz()
        return Apstrakcija(p >> T.SLOVO, p.aps())

    def član(p) -> 'faktor|Aplikacija':
        f = p.faktor()
        while p > {T.OTV, T.SLOVO}: f = Aplikacija(f, p.faktor())
        return f

    def faktor(p) -> 'izraz|SLOVO':
        if p >= T.OTV:
            u_zagradi = p.izraz()
            p >> T.ZATV
            return u_zagradi
        else: return p >> T.SLOVO


### Apstraktna sintaksna stabla
# izraz: SLOVO:Token
#        Apstrakcija: varijabla:SLOVO doseg:izraz
#        Aplikacija: funkcija:izraz argument:izraz

class Apstrakcija(AST):
    varijabla: 'SLOVO'
    doseg: 'izraz'
    def slobodne(apstrakcija):
        return apstrakcija.doseg.slobodne() - apstrakcija.varijabla.slobodne()

class Aplikacija(AST):
    funkcija: 'izraz'
    argument: 'izraz'
    def slobodne(aplikacija):
        return aplikacija.funkcija.slobodne() | aplikacija.argument.slobodne()


def kombinator(l): return not P(l).slobodne()

prikaz(P('(^x.xx)(^x.xx)'), 3)
print(P('^xy.x') == P('^x.^y.x'))
print(kombinator('(^yx.(x))x'))
with SintaksnaGreška: P('^x.x^y.y')
with LeksičkaGreška: P('λ x.x')
