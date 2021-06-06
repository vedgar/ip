"""Istinitosna vrijednost, i jednostavna optimizacija, formula logike sudova.

Standardna definicija iz [Vuković, Matematička logika]:
* Propozicijska varijabla (P0, P1, P2, ..., P9, P10, P11, ....) je formula
* Ako je F formula, tada je i !F formula (negacija)
* Ako su F i G formule, tada su i (F&G), (F|G), (F->G) i (F<->G) formule
Sve zagrade (oko binarnih veznika) su obavezne!

Interpretaciju zadajemo imenovanim argumentima: vrijednost(F, P2=True, P7=False)
Optimizacija (formula.optim()) zamjenjuje potformule oblika !!F sa F."""


from vepar import *


class T(TipoviTokena):
    NEG, KONJ, DISJ, OTV, ZATV = '!&|()'
    KOND, BIKOND = '->', '<->'
    class PVAR(Token):
        def vrijednost(var, I): return I[var]
        def optim(var): return var


@lexer
def ls(lex):
    for znak in lex:
        if znak == 'P':
            prvo = next(lex)
            if not prvo.isdecimal(): raise lex.greška('očekivana znamenka')
            if prvo != '0': lex * str.isdigit
            yield lex.token(T.PVAR)
        elif znak == '-':
            lex >> '>'
            yield lex.token(T.KOND)
        elif znak == '<':
            lex >> '-'
            lex >> '>'
            yield lex.token(T.BIKOND)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# formula -> NEG formula | PVAR | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

### Apstraktna sintaksna stabla (i njihovi atributi):
# formula: PVAR: Token
#          Negacija: ispod:formula
#          Binarna: veznik:T lijevo:formula desno:formula


class P(Parser):
    def formula(p) -> 'PVAR|Negacija|Binarna':
        if varijabla := p >= T.PVAR: return varijabla
        elif p >= T.NEG: 
            ispod = p.formula()
            return Negacija(ispod)
        elif p >> T.OTV:
            lijevo = p.formula()
            veznik = p >> {T.KONJ, T.DISJ, T.KOND, T.BIKOND}
            desno = p.formula()
            p >> T.ZATV
            return Binarna(veznik, lijevo, desno)


class Negacija(AST):
    ispod: 'formula'

    def vrijednost(negacija, I): return not negacija.ispod.vrijednost(I)

    def optim(negacija):
        ispod_opt = negacija.ispod.optim()
        if ispod_opt ^ Negacija: return ispod_opt.ispod 
        else: return Negacija(ispod_opt)


class Binarna(AST):
    veznik: 'T'
    lijevo: 'formula'
    desno: 'formula'

    def vrijednost(self, I):
        v = self.veznik
        l = self.lijevo.vrijednost(I)
        d = self.desno.vrijednost(I)
        if v ^ T.DISJ: return l or d
        elif v ^ T.KONJ: return l and d
        elif v ^ T.KOND: return l <= d
        elif v ^ T.BIKOND: return l == d
        else: assert False, 'nepokriveni slučaj'

    def optim(self):
        lijevo_opt = self.lijevo.optim()
        desno_opt = self.desno.optim()
        return Binarna(self.veznik, lijevo_opt, desno_opt)


def istinitost(formula, **interpretacija):
    I = Memorija(interpretacija)
    return formula.vrijednost(I)


ls(ulaz := '!(P5&!!(P3->P0))')
prikaz(F := P(ulaz))
prikaz(F := F.optim())
print(f'{istinitost(F, P0=False, P3=True, P5=False)=}')  # True

for krivo in 'P', 'P00', 'P1\tP2', 'P34<>P56':
    with LeksičkaGreška: ls(krivo)


# DZ: implementirajte još neke optimizacije: npr. F|!G u G->F.
# DZ: Napravite totalnu optimizaciju negacije: svaka formula s najviše jednim !
# ~~  *Za ovo bi vjerojatno bilo puno lakše imati po jedno AST za svaki veznik.
