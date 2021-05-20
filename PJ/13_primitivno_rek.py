"""Funkcijski jezik primitivno rekurzivnih simboličkih definicija funkcija.

Slažemo funkcije od osnovnih (tzv. inicijalnih) funkcija:
    nulfunkcija: Z(x) := 0
    sljedbenik: Sc(x) := x + 1
    koordinatna projekcija: Ikn(x1,...,xk) := xn
pomoću dva operatora:
    kompozicija: 
        (H o (G1,...,Gl)) (x1,...,xk) := H(G1(x1,...,xk),...,Gl(x1,...xk))
    primitivna rekurzija:
        (G PR H) (x1,...,xk,0) := G(x1,...xk)
        (G PR H) (x1,...,xk,y+1) := H(x1,...,xk,y,(G PR H)(x1,...,xk,y))"""


from vepar import *


class T(TipoviTokena):
    ZAREZ, OTV, ZATV, KOMPOZICIJA, JEDNAKO = ',()o='
    PR = 'PR'

    class FIME(Token):
        """Ime primitivno rekurzivne funkcije."""
        def mjesnost(self, symtab): return symtab[self][0]
        def izračunaj(self, symtab, *argumenti):
            k, f = symtab[self]
            assert k == len(argumenti)
            return f.izračunaj(symtab, *argumenti)

    class NULFUNKCIJA(Token):
        literal = 'Z'
        def mjesnost(self, symtab): return 1
        def izračunaj(self, symtab, argument): return 0

    class SLJEDBENIK(Token):
        literal = 'Sc'
        def mjesnost(self, symtab): return 1
        def izračunaj(self, symtab, argument): return argument + 1

    class KPROJEKCIJA(Token):
        """Koordinatna projekcija, mjesnosti najviše 9."""
        def mjesnost(self, symtab): return int(self.sadržaj[2])
        def izračunaj(self, symtab, *argumenti):
            n = int(self.sadržaj[1])
            return argumenti[n - 1]


def pr(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == 'I':
            n, k = divmod(lex.prirodni_broj(''), 10)
            if 1 <= n <= k: yield lex.token(T.KPROJEKCIJA)
            else: raise lex.greška('krivo formirani token Ink')
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.literal(T.FIME)
        else: yield lex.literal(T)


### BKG
# program -> definicija | definicija program
# definicija -> FIME JEDNAKO funkcija
# funkcija -> komponenta | komponenta PR komponenta
# komponenta -> lijevo | komponenta KOMPOZICIJA desno
# lijevo -> osnovna | OTV funkcija ZATV
# desno -> osnovna | OTV funkcije ZATV
# osnovna -> FIME | NULFUNKCIJA | SLJEDBENIK | KPROJEKCIJA
# funkcije -> funkcija | funkcija ZAREZ funkcije


class P(Parser):
    def program(self):
        symtab = Memorija(redefinicija=False)
        while not self > KRAJ:
            imef = self >> T.FIME
            self >> T.JEDNAKO
            f = self.funkcija()
            symtab[imef] = (f.mjesnost(symtab), f)
        if not symtab: raise SemantičkaGreška('Prazan program')
        return symtab

    def funkcija(self):
        baza = self.komponenta()
        if self >= T.PR: return PRekurzija(baza, self.komponenta())
        else: return baza

    def osnovna(self):
        return self >> {T.FIME, T.NULFUNKCIJA, T.SLJEDBENIK, T.KPROJEKCIJA}

    def komponenta(self):
        if self >= T.OTV:
            t = self.funkcija()
            self >> T.ZATV
        else: t = self.osnovna()
        while self >= T.KOMPOZICIJA: t = Kompozicija(t, self.desno())
        return t

    def desno(self):
        if self >= T.OTV:
            rezultat = [self.funkcija()]
            while self >= T.ZAREZ: rezultat.append(self.funkcija())
            self >> T.ZATV
            return rezultat
        else: return [self.osnovna()]

    start = program
    lexer = pr


### AST
# funkcija: FIME|NULFUNKCIJA|SLJEDBENIK|KPROJEKCIJA:Token
#           Kompozicija: lijeva:funkcija desne:[funkcija]
#           PRekurzija: baza:funkcija korak:funkcija


kriva_mjesnost = SemantičkaGreška('Mjesnosti ne odgovaraju')


class Kompozicija(AST('lijeva desne')):
    def mjesnost(self, symtab):
        l = self.lijeva.mjesnost(symtab)
        if len(self.desne) != l: raise kriva_mjesnost
        G1, *ostale = self.desne
        k = G1.mjesnost(symtab)
        if any(G.mjesnost(symtab) != k for G in ostale): raise kriva_mjesnost
        return k

    @cache
    def izračunaj(self, symtab, *argumenti):
        međurezultati = (G.izračunaj(symtab, *argumenti) for G in self.desne)
        return self.lijeva.izračunaj(symtab, *međurezultati)


class PRekurzija(AST('baza korak')):
    def mjesnost(self, symtab):
        k = self.baza.mjesnost(symtab)
        if self.korak.mjesnost(symtab) != k + 2: raise kriva_mjesnost
        return k + 1

    @cache
    def izračunaj(self, symtab, *argumenti):
        *xevi, y = argumenti
        z = self.baza.izračunaj(symtab, *xevi)
        for i in range(y): z = self.korak.izračunaj(symtab, *xevi, i, z)
        return z


def izračunaj(memorija, imef, *argumenti):
    k, f = memorija[imef]
    if len(argumenti) == k: return f.izračunaj(memorija, *argumenti)
    else: raise kriva_mjesnost


prikaz(konstante := P('''\
        C01 = Z
        C11 = Sc o C01
        C21 = Sc o C11
        C23 = C21 o I13
        C58 = Sc o Sc o Sc o Sc o Sc o Z o I18
'''))
prikaz(operacije := P('''\
        add2 = I11 PR Sc o I33
        mul2 = Z PR add2 o (I13, I33)
        pow = Sc o Z PR mul2 o (I13, I33)
'''))
print(3, '^', 7, '=', izračunaj(operacije, 'pow', 3, 7))

# DZ**: dokažite ekvivalentnost ovog sustava i programskog jezika LOOP
