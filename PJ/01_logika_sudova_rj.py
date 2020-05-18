"""Istinitosna vrijednost, optimizacija, i lijep ispis, formula logike sudova.

Standardna definicija iz [Vuković, Matematička logika]:
* Propozicijska varijabla (P0, P1, P2, ..., P9, P10, P11, ....) je formula
* Ako je F formula, tada je i !F formula (negacija)
* Ako su F i G formule, tada su i (F&G), (F|G), (F->G) i (F<->G) formule
Sve zagrade (oko binarnih veznika) su obavezne!

Interpretaciju zadajemo imenovanim argumentima: vrijednost(F, P2=True, P7=False)
Optimizacija piše svaku formulu u obliku G ili !G, gdje u G nema negacije."""


from pj import *


subskript = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')

class T(TipoviTokena):
    NEG, KONJ, DISJ, OTV, ZATV, KOND, BIKOND = *'!&|()', '->', '<->'
    class PVAR(Token):
        def vrijednost(self, I): return I[self]
        def makni_neg(self): return self, True
        def ispis(self): return self.sadržaj.translate(subskript)


def ls(lex):
    for znak in lex:
        if znak == 'P':
            lex.prirodni_broj()
            yield lex.token(T.PVAR)
        elif znak == '-':
            lex.pročitaj('>')
            yield lex.token(T.KOND)
        elif znak == '<':
            lex.pročitaj('-'), lex.pročitaj('>')
            yield lex.token(T.BIKOND)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# formula -> PVAR | NEG formula | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

### Apstraktna sintaksna stabla (i njihovi atributi):
# formula: PVAR: Token
#          Negacija: ispod:formula
#          Konjunkcija: Binarna
#          Disjunkcija: Binarna
#          Kondicional: Binarna
#          Bikondicional: Binarna
# Binarna: lijevo:formula desno:formula


class P(Parser):
    def formula(self):
        if self >> T.PVAR: return self.zadnji
        elif self >> T.NEG: 
            ispod = self.formula()
            return Negacija(ispod)
        elif self >> T.OTV:
            l, klasa, d = self.formula(), self.binvez(), self.formula()
            self.pročitaj(T.ZATV)
            return klasa(l, d)
        else: raise self.greška()

    def binvez(self):
        if self >> T.KONJ: return Konjunkcija
        elif self >> T.DISJ: return Disjunkcija
        elif self >> T.KOND: return Kondicional
        elif self >> T.BIKOND: return Bikondicional
        else: raise self.greška()

    lexer = ls
    start = formula


class Negacija(AST('ispod')):
    veznik = '¬'

    def vrijednost(self, I): return not self.ispod.vrijednost(I)

    def makni_neg(self):
        bez_neg, pozitivna = self.ispod.makni_neg()
        return bez_neg, not pozitivna

    def ispis(self): return self.veznik + self.ispod.ispis()


class Binarna(AST('lijevo desno')):
    def vrijednost(self, I):
        klasa = type(self)
        l, d = self.lijevo.vrijednost(I), self.desno.vrijednost(I)
        return klasa.tablica(l, d)

    def makni_neg(self):
        klasa = type(self)
        l, lp = self.lijevo.makni_neg()
        d, dp = self.desno.makni_neg()
        return klasa.xform(l, d, lp, dp), klasa.tablica(lp, dp)

    def ispis(self): return '(' + self.lijevo.ispis() + \
            self.veznik + self.desno.ispis() + ')'


class Disjunkcija(Binarna):
    veznik = '∨'

    def tablica(l, d): return l or d

    def xform(l, d, lp, dp):
        if lp and dp: return Disjunkcija(l, d)
        if not lp and dp: return Kondicional(l, d)
        if lp and not dp: return Kondicional(d, l)
        return Konjunkcija(l, d)


class Konjunkcija(Binarna):
    veznik = '∧'

    def tablica(l, d): return l and d

    def xform(l, d, lp, dp): return Disjunkcija.xform(l, d, not lp, not dp)


class Kondicional(Binarna):
    veznik = '→'

    def tablica(l, d):
        if l: return d
        return True
    
    def xform(l, d, lp, dp): return Disjunkcija.xform(l, d, not lp, dp)


class Bikondicional(Binarna):
    veznik = '↔'

    def tablica(l, d): return l == d

    def xform(l, d, lp, dp): return Bikondicional(l, d)


def optim(formula):
    """Pretvara formulu (AST) u oblik s najviše jednom negacijom."""
    bez_neg, pozitivna = formula.makni_neg()
    if pozitivna: return bez_neg
    else: return Negacija(bez_neg)

def istinitost(formula, **interpretacija):
    I = Memorija(interpretacija)
    return formula.vrijednost(I)


for ulaz in '!(P5&!!(P3->P0))', '(!P0&(!P1<->!P5))':
    print(ulaz)
    P.tokeniziraj(ulaz)

    F = P(ulaz)
    print(F.ispis())
    prikaz(F)
    F = optim(F)
    print(F.ispis())
    prikaz(F)
    print(istinitost(F, P0=False, P3=True, P5=False, P1=True))
    print('-' * 60)

for krivo in 'P007', 'P1\nP2', 'P34<>P56', 'P05', 'P-2':
    with očekivano(LeksičkaGreška): P.tokeniziraj(krivo)
