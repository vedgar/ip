"""Funkcijski jezik simboličkih definicija primitivno rekurzivnih funkcija.

Slažemo funkcije od osnovnih (tzv. inicijalnih) funkcija:
    nulfunkcija: Z(x) := 0
    sljedbenik: Sc(x) := x + 1
    koordinatna projekcija: Ink(x1,...,xk) := xn
pomoću dva operatora:
    kompozicija: 
        (H o (G1,...,Gl)) (x1,...,xk) := H(G1(x1,...,xk),...,Gl(x1,...xk))
    primitivna rekurzija:
        (G PR H) (x1,...,xk,0) := G(x1,...xk)
        (G PR H) (x1,...,xk,y+1) := H(x1,...,xk,y,(G PR H)(x1,...,xk,y))"""


from vepar import *


kriva_mjesnost = SemantičkaGreška('Mjesnosti ne odgovaraju')


class T(TipoviTokena):
    ZAREZ, OTV, ZATV, KOMPOZICIJA, JEDNAKO = ',()o='
    PR = 'PR'

    class FIME(Token):
        """Ime primitivno rekurzivne funkcije."""
        def mjesnost(self): return rt.symtab[self][0]
        def izračunaj(self, *argumenti):
            k, f = rt.symtab[self]
            assert k == self.mjesnost() == len(argumenti)
            return f.izračunaj(*argumenti)

    class NULFUNKCIJA(Token):
        literal = 'Z'
        def mjesnost(self): return 1
        def izračunaj(self, _): return 0

    class SLJEDBENIK(Token):
        literal = 'Sc'
        def mjesnost(self): return 1
        def izračunaj(self, argument): return argument + 1

    class KPROJEKCIJA(Token):
        """Koordinatna projekcija, mjesnosti najviše 9."""
        def mjesnost(self): return int(self.sadržaj[2])
        def izračunaj(self, *argumenti):
            n = int(self.sadržaj[1])
            return argumenti[n - 1]

@lexer
def pr(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == 'I':
            n, k = divmod(lex.prirodni_broj(''), 10)
            if 1 <= n <= k: yield lex.token(T.KPROJEKCIJA)
            else: raise lex.greška('krivo formirani token Ink')
        elif znak.isalpha():
            lex * str.isalnum
            yield lex.literal_ili(T.FIME)
        else: yield lex.literal(T)


### BKG
# program -> definicija | program definicija
# definicija -> FIME JEDNAKO funkcija
# funkcija -> komponenta | komponenta PR komponenta
# komponenta -> lijevo | komponenta KOMPOZICIJA desno
# lijevo -> osnovna | OTV funkcija ZATV
# desno -> osnovna | OTV funkcije ZATV
# osnovna -> FIME | NULFUNKCIJA | SLJEDBENIK | KPROJEKCIJA
# funkcije -> funkcija | funkcije ZAREZ funkcija

class P(Parser):
    def program(p) -> 'Memorija':
        rt.symtab = Memorija(redefinicija=False)
        while not p > KRAJ:
            imef = p >> T.FIME
            p >> T.JEDNAKO
            f = p.funkcija()
            rt.symtab[imef] = (f.mjesnost(), f)
        if not rt.symtab: raise SemantičkaGreška('Prazan program')
        return rt.symtab

    def funkcija(p) -> 'PRekurzija|komponenta':
        baza = p.komponenta()
        if p >= T.PR: return PRekurzija(baza, p.komponenta())
        else: return baza

    def osnovna(p) -> 'FIME|NULFUNKCIJA|SLJEDBENIK|KPROJEKCIJA':
        return p >> {T.FIME, T.NULFUNKCIJA, T.SLJEDBENIK, T.KPROJEKCIJA}

    def komponenta(p) -> 'funkcija|osnovna|Kompozicija':
        if p >= T.OTV:
            t = p.funkcija()
            p >> T.ZATV
        else: t = p.osnovna()
        while p >= T.KOMPOZICIJA: t = Kompozicija(t, p.desno())
        return t

    def desno(p) -> 'funkcija*|osnovna':
        if p >= T.OTV:
            rezultat = [p.funkcija()]
            while p >= T.ZAREZ: rezultat.append(p.funkcija())
            p >> T.ZATV
            return rezultat
        else: return [p.osnovna()]


### AST
# funkcija: FIME|NULFUNKCIJA|SLJEDBENIK|KPROJEKCIJA:Token
#           Kompozicija: lijeva:funkcija desne:[funkcija]
#           PRekurzija: baza:funkcija korak:funkcija

class Kompozicija(AST):
    lijeva: 'funkcija'
    desne: 'funkcija*'

    def mjesnost(self):
        l = self.lijeva.mjesnost()
        if len(self.desne) != l: raise kriva_mjesnost
        G1, *ostale = self.desne
        k = G1.mjesnost()
        if any(G.mjesnost() != k for G in ostale): raise kriva_mjesnost
        return k

    def izračunaj(self, *argumenti):
        međurezultati = (G.izračunaj(*argumenti) for G in self.desne)
        return self.lijeva.izračunaj(*međurezultati)

class PRekurzija(AST):
    baza: 'funkcija'
    korak: 'funkcija'

    def mjesnost(self):
        k = self.baza.mjesnost()
        if self.korak.mjesnost() != k + 2: raise kriva_mjesnost
        return k + 1

    def izračunaj(self, *argumenti):
        *xevi, y = argumenti
        z = self.baza.izračunaj(*xevi)
        for i in range(y): z = self.korak.izračunaj(*xevi, i, z)
        return z


def izračunaj(imef, *argumenti):
    k, f = rt.symtab[imef]
    if len(argumenti) == k: return f.izračunaj(*argumenti)
    else: raise kriva_mjesnost


prikaz(P('''
        C01 = Z
        C11 = Sc o C01
        C21 = Sc o C11
        C23 = C21 o I13
        C58 = Sc o Sc o Sc o Sc o Sc o Z o I18
'''))
print('C11(5) =', izračunaj('C11', 5))
prikaz(P('''
        add2 = I11 PR Sc o I33
        mul2 = Z PR add2 o (I13, I33)
        pow = Sc o Z PR mul2 o (I13, I33)
'''))
print(b:=3, '^', e:=7, '=', izračunaj('pow', b, e))


# DZ**: dokažite ekvivalentnost ovog sustava i programskog jezika LOOP
