"""Lambda-račun: zadatak s kolokvija 2019.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2.19-06-28.pdf"""

from vepar import *

class Λ(enum.Enum):
    LAMBDA, TOČKA, OTV, ZATV = 'λ.()'
    class SLOVO(Token):
        def slobodne(self): return {self}

def λex(l):
    for znak in l:
        if znak.isspace(): l.zanemari()
        elif znak in {'λ', '^'}:
            yield l.token(Λ.LAMBDA)
            if l.čitaj().isalpha(): yield l.token(Λ.SLOVO)
            else: raise l.greška('iza λ mora ići slovo bez razmaka')
        elif znak.isalpha(): yield l.token(Λ.SLOVO)
        else: yield l.literal(Λ)

### Beskontekstna gramatika:
# izraz -> LAMBDA slova TOČKA izraz | član
# slova -> SLOVO | SLOVO slova
# član -> član faktor | faktor
# faktor -> OTV izraz ZATV | SLOVO

# Oneliner BKG: start -> (LAMBDA SLOVO+ TOČKA)* (OTV start ZATV | SLOVO)+

class λ(Parser):
    def izraz(self):
        if self >= Λ.LAMBDA: return self.aps()
        return self.član()

    def aps(self):
        if self >= Λ.TOČKA: return self.izraz()
        return Apstrakcija(self >> Λ.SLOVO, self.aps())

    def član(self):
        f = self.faktor()
        while self > {Λ.OTV, Λ.SLOVO}: f = Aplikacija(f, self.faktor())
        return f

    def faktor(self):
        if self >= Λ.OTV:
            u_zagradi = self.izraz()
            self >> Λ.ZATV
            return u_zagradi
        else: return self >> Λ.SLOVO

    start = izraz
    lexer = λex

### Apstraktna sintaksna stabla
# izraz: SLOVO:Token
#        Apstrakcija: varijabla:SLOVO doseg:izraz
#        Aplikacija: funkcija:izraz argument:izraz

class Apstrakcija(AST('varijabla doseg')):
    def slobodne(self): return self.doseg.slobodne() - self.varijabla.slobodne()

class Aplikacija(AST('funkcija argument')):
    def slobodne(self): return self.funkcija.slobodne()|self.argument.slobodne()

def kombinator(l): return not λ(l).slobodne()

prikaz(λ('(^x.xx)(^x.xx)'), 3)
print(λ('^xy.x') == λ('^x.^y.x'))
print(kombinator('(^yx.(x))x'))
with očekivano(SintaksnaGreška): λ('^x.x^y.y')
