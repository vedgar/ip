"""Istinitosna vrijednost, optimizacija, i lijep ispis, formula logike sudova.

Standardna definicija iz [Vuković, Matematička logika]:
* Propozicijska varijabla (P0, P1, P2, ..., P9, P10, P11, ....) je formula
* Ako je F formula, tada je i !F formula (negacija)
* Ako su F i G formule, tada su i (F&G), (F|G), (F->G) i (F<->G) formule
Sve zagrade (oko binarnih veznika) su obavezne!

Interpretaciju zadajemo imenovanim argumentima: vrijednost(F, P2=True, P7=False)
Optimizacija piše svaku formulu u obliku G ili !G, gdje u G nema negacije."""


from vepar import *


subskript = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')

class T(TipoviTokena):
    NEG, KONJ, DISJ, OTV, ZATV, KOND, BIKOND = *'!&|()', '->', '<->'
    class PVAR(Token):
        def vrijednost(self): return rt.interpretacija[self]
        def makni_neg(self): return self, True
        def ispis(self): return self.sadržaj.translate(subskript)

@lexer
def ls(lex):
    for znak in lex:
        match znak:
            case 'P':
                lex.prirodni_broj('')
                yield lex.token(T.PVAR)
            case '-':
                lex >> '>'
                yield lex.token(T.KOND)
            case '<':
                lex >> '-', lex >> '>'
                yield lex.token(T.BIKOND)
            case _: yield lex.literal(T)


### Beskontekstna gramatika:
# formula -> PVAR | NEG formula | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

class P(Parser):
    def formula(p) -> \
            'PVAR|Negacija|Konjunkcija|Disjunkcija|Kondicional|Bikondicional':
        if varijabla := p >= T.PVAR: return varijabla
        elif p >= T.NEG: 
            ispod = p.formula()
            return Negacija(ispod)
        elif p >> T.OTV:
            lijevo, klasa, desno = p.formula(), p.binvez(), p.formula()
            p >> T.ZATV
            return klasa(lijevo, desno)

    def binvez(p):
        if p >= T.KONJ: return Konjunkcija
        elif p >= T.DISJ: return Disjunkcija
        elif p >= T.KOND: return Kondicional
        elif p >= T.BIKOND: return Bikondicional
        else: raise p.greška()


### Apstraktna sintaksna stabla (i njihovi atributi):
# formula: PVAR: Token
#          Negacija: ispod:formula
#          Konjunkcija: Binarna
#          Disjunkcija: Binarna
#          Kondicional: Binarna
#          Bikondicional: Binarna
# Binarna: lijevo:formula desno:formula

class Negacija(AST):
    ispod: P.formula
    veznik = '¬'

    def vrijednost(negacija): return not negacija.ispod.vrijednost()

    def makni_neg(negacija):
        bez_neg, pozitivna = negacija.ispod.makni_neg()
        return bez_neg, not pozitivna

    def ispis(negacija): return negacija.veznik + negacija.ispod.ispis()


class Binarna(AST):
    lijevo: P.formula
    desno: P.formula

    def vrijednost(self):
        klasa = type(self)
        lijevo, desno = self.lijevo.vrijednost(), self.desno.vrijednost()
        return klasa.tablica(lijevo, desno)

    def makni_neg(self):
        klasa = type(self)
        lijevo, lp = self.lijevo.makni_neg()
        desno, dp = self.desno.makni_neg()
        return klasa.xform(lijevo, desno, lp, dp), klasa.tablica(lp, dp)

    def ispis(self): return '(' + self.lijevo.ispis() + \
            self.veznik + self.desno.ispis() + ')'


class Disjunkcija(Binarna):
    veznik = '∨'

    def tablica(lijevo, desno): return lijevo or desno

    def xform(lijevo, desno, lp, dp):
        match lp, dp:
            case False, False: return Konjunkcija(lijevo, desno)
            case False, True: return Kondicional(lijevo, desno)
            case True, False: return Kondicional(desno, lijevo)
            case True, True: return Disjunkcija(lijevo, desno)
            case _: assert False, 'nepokriveni slučaj!'


class Konjunkcija(Binarna):
    veznik = '∧'

    def tablica(lijevo, desno): return lijevo and desno

    def xform(l, d, lp, dp): return Disjunkcija.xform(l, d, not lp, not dp)


class Kondicional(Binarna):
    veznik = '→'

    def tablica(lijevo, desno):
        if lijevo: return desno
        return True
    
    def xform(l, d, lp, dp): return Disjunkcija.xform(l, d, not lp, dp)


class Bikondicional(Binarna):
    veznik = '↔'

    def tablica(lijevo, desno): return lijevo == desno

    def xform(l, d, lp, dp): return Bikondicional(l, d)


def optim(formula):
    """Pretvara formulu (AST) u oblik s najviše jednom negacijom."""
    bez_neg, pozitivna = formula.makni_neg()
    if pozitivna: return bez_neg
    else: return Negacija(bez_neg)

def istinitost(formula, **interpretacija):
    rt.interpretacija = Memorija(interpretacija)
    return formula.vrijednost()


for ulaz in '!(P5&!!(P3->P0))', '(!P0&(!P1<->!P5))':
    ls(ulaz)
    prikaz(F := P(ulaz))
    print(F.ispis())
    prikaz(F := optim(F))
    print(F.ispis())
    print(f'{istinitost(F, P0=False, P3=True, P5=False, P1=True)=}')
    print('-' * 60)

for nije_formula in 'P007', 'P1 P2', 'P34<>P56', 'P05', 'P-2':
    with LeksičkaGreška: ls(nije_formula)
