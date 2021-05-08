from pj import *

class Λ(enum.Enum):
    LAMBDA, TOČKA, OTV, ZATV = 'λ.()'
    class SLOVO(Token):
        def slobodne(self): return {self}

def λ_lex(lam):
    lex = Tokenizer(lam)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak in {'λ', '^'}:
            yield lex.token(Λ.LAMBDA)
            if lex.čitaj().isalpha(): yield lex.token(Λ.SLOVO)
            else: raise lex.greška('iza λ mora ići slovo bez razmaka')
        elif znak.isalpha(): yield lex.token(Λ.SLOVO)
        else: yield lex.literal(Λ)

### Beskontekstna gramatika:
# izraz -> LAMBDA slova TOČKA izraz | član
# slova -> SLOVO | SLOVO slova
# član -> član faktor | faktor
# faktor -> OTV izraz ZATV | SLOVO

# Oneliner BKG: start -> (LAMBDA SLOVO+ TOČKA)* (OTV start ZATV | SLOVO)+

class ΛParser(Parser):
    def izraz(self):
        if self >> Λ.LAMBDA: return self.aps()
        return self.član()

    def aps(self):
        if self >> Λ.TOČKA: return self.izraz()
        return Apstrakcija(self.pročitaj(Λ.SLOVO), self.aps())

    def član(self):
        f = self.faktor()
        while self >= {Λ.OTV, Λ.SLOVO}: f = Aplikacija(f, self.faktor())
        return f

    def faktor(self):
        if self >> Λ.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(Λ.ZATV)
            return u_zagradi
        else: return self.pročitaj(Λ.SLOVO)

    start = izraz

### Apstraktna sintaksna stabla
# Apstrakcija: varijabla doseg
# Aplikacija: funkcija argument

class Apstrakcija(AST('varijabla doseg')):
    def slobodne(self): return self.doseg.slobodne() - self.varijabla.slobodne()

class Aplikacija(AST('funkcija argument')):
    def slobodne(self): return self.funkcija.slobodne()|self.argument.slobodne()

def kombinator(lam): return not ΛParser.parsiraj(λ_lex(lam)).slobodne()

prikaz(ΛParser.parsiraj(λ_lex('(^x.xx)(^x.xx)')), 3)
print(ΛParser.parsiraj(λ_lex('^xy.x')) == ΛParser.parsiraj(λ_lex('^x.^y.x')))
print(kombinator('(^yx.(x))x'))
with očekivano(SintaksnaGreška): print(ΛParser.parsiraj(λ_lex('^x.x^y.y')))
