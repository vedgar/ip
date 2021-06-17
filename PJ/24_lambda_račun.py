"""Lambda-račun: zadatak s kolokvija 28. lipnja 2019.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2.19-06-28.pdf"""


from vepar import *


class Λ(enum.Enum):
    LAMBDA, TOČKA, OTV, ZATV = 'λ.()'
    class SLOVO(Token):
        def slobodne(t): return {t}

@lexer
def λex(l):
    for znak in l:
        if znak.isspace(): l.zanemari()
        elif znak in {'λ', '^'}:
            yield l.token(Λ.LAMBDA)
            if (l >> str.isalpha) == 'λ': raise lex.greška('λ nije slovo!')
            yield l.token(Λ.SLOVO)
        elif znak.isalpha(): yield l.token(Λ.SLOVO)
        else: yield l.literal(Λ)

### Beskontekstna gramatika:
# izraz -> član | LAMBDA slova TOČKA izraz
# slova -> SLOVO | SLOVO slova
# član -> faktor | član faktor
# faktor -> OTV izraz ZATV | SLOVO

# Oneliner BKG: start -> (LAMBDA SLOVO+ TOČKA)* (OTV start ZATV | SLOVO)+

class λ(Parser):
    def izraz(p) -> 'aps|član':
        if p >= Λ.LAMBDA: return p.aps()
        return p.član()

    def aps(p) -> 'izraz|Apstrakcija':
        if p >= Λ.TOČKA: return p.izraz()
        return Apstrakcija(p >> Λ.SLOVO, p.aps())

    def član(p) -> 'faktor|Aplikacija':
        f = p.faktor()
        while p > {Λ.OTV, Λ.SLOVO}: f = Aplikacija(f, p.faktor())
        return f

    def faktor(p) -> 'izraz|SLOVO':
        if p >= Λ.OTV:
            u_zagradi = p.izraz()
            p >> Λ.ZATV
            return u_zagradi
        else: return p >> Λ.SLOVO


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


def kombinator(l): return not λ(l).slobodne()

prikaz(λ('(^x.xx)(^x.xx)'), 3)
print(λ('^xy.x') == λ('^x.^y.x'))
print(kombinator('(^yx.(x))x'))
with SintaksnaGreška: λ('^x.x^y.y')
with LeksičkaGreška: λ('λ x.x')
