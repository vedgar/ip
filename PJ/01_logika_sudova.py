"""Istinitosna vrijednost, i jednostavna optimizacija, formula logike sudova.

Standardna definicija iz [Vuković, Matematička logika]:
* Propozicijska varijabla (P0, P1, P2, ..., P9, P10, P11, ....) je formula
* Ako je F formula, tada je i !F formula (negacija)
* Ako su F i G formule, tada su i (F&G), (F|G), (F->G) i (F<->G) formule
Sve zagrade (oko binarnih veznika) su obavezne!

Interpretacija se zadaje imenovanim argumentima (**interpretacija):
    formula.vrijednost(P2=True, P7=False, P1=True, ...)

Optimizacija (formula.optim()) zamjenjuje potformule oblika !!F sa F.
"""


from pj import *


class LS(enum.Enum):
    NEG, KONJ, DISJ, OTV, ZATV = '!&|()'
    KOND, BIKOND = '->', '<->'
    class PVAR(Token):
        def vrijednost(self, **interpretacija):
            return pogledaj(interpretacija, self)
        def optim(self): return self


def ls_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak == 'P':
            prvo = lex.čitaj()
            if not prvo.isdigit(): lex.greška('očekivana znamenka')
            if prvo != '0': lex.zvijezda(str.isdigit)
            yield lex.token(LS.PVAR)
        elif znak == '-':
            lex.pročitaj('>')
            yield lex.token(LS.KOND)
        elif znak == '<':
            lex.pročitaj('-'), lex.pročitaj('>')
            yield lex.token(LS.BIKOND)
        else: yield lex.literal(LS)


### Beskontekstna gramatika:
# formula -> NEG formula | PVAR | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND


### Apstraktna sintaksna stabla (i njihovi atributi):
# PVAR (Token, odozgo): tip, sadržaj
# Negacija: ispod
# Binarna: veznik lijevo desno


class LSParser(Parser):
    def formula(self):
        if self >> LS.PVAR: return self.zadnji
        elif self >> LS.NEG: 
            ispod = self.formula()
            return Negacija(ispod)
        elif self >> LS.OTV:
            lijevo = self.formula()
            veznik = self.pročitaj(LS.KONJ, LS.DISJ, LS.KOND, LS.BIKOND)
            desno = self.formula()
            self.pročitaj(LS.ZATV)
            return Binarna(veznik, lijevo, desno)
        else: raise self.greška()

    start = formula


class Negacija(AST('ispod')):
    def vrijednost(formula, **interpretacija):
        return not formula.ispod.vrijednost(**interpretacija)

    def optim(self):
        ispod_opt = self.ispod.optim()
        if ispod_opt ^ Negacija: return ispod_opt.ispod 
        else: return Negacija(ispod_opt)


class Binarna(AST('veznik lijevo desno')):
    def vrijednost(formula, **interpretacija):
        v = formula.veznik
        l = formula.lijevo.vrijednost(**interpretacija)
        d = formula.desno.vrijednost(**interpretacija)
        if v ^ LS.DISJ: return l or d
        elif v ^ LS.KONJ: return l and d
        elif v ^ LS.KOND: return l <= d
        elif v ^ LS.BIKOND: return l == d
        else: assert False, 'nepokriveni slučaj'

    def optim(self):
        lijevo_opt = self.lijevo.optim()
        desno_opt = self.desno.optim()
        return Binarna(self.veznik, lijevo_opt, desno_opt)


if __name__ == '__main__':
    ulaz = '!(P5&!!(P3->P0))'
    print(ulaz)

    tokeni = list(ls_lex(ulaz))
    print(*tokeni)
    # NEG'!' OTV'(' PVAR'P5' KONJ'&' NEG'!' NEG'!'
    # OTV'(' PVAR'P3' KOND'->' PVAR'P0' ZATV')' ZATV')'

    fo = LSParser.parsiraj(tokeni)
    prikaz(fo, 4)
    # Negacija(
    #   ispod=Binarna(
    #     veznik=KONJ'&',
    #     lijevo=PVAR'P5',
    #     desno=Negacija(
    #       ispod=Negacija(
    #         ispod=Binarna(
    #           veznik=KOND'->',
    #           lijevo=PVAR'P3',
    #           desno=PVAR'P0'
    #         )
    #       )
    #     )
    #   )
    # )
    
    fo = fo.optim()
    prikaz(fo, 3)
    # Negacija(
    #   ispod=Binarna(
    #     veznik=KONJ'&',
    #     lijevo=PVAR'P5',
    #     desno=Binarna(
    #       veznik=KOND'->',
    #       lijevo=PVAR'P3',
    #       desno=PVAR'P0'
    #     )
    #   )
    # )
    
    print(fo.vrijednost(P0=False, P3=True, P5=False))
    # True

# DZ: implementirajte još neke optimizacije: npr. F|!G u G->F.
# DZ: Napravite totalnu optimizaciju negacije: svaka formula s najviše jednim !
# (Za ovo bi vjerojatno bilo puno lakše imati po jedno AST za svaki veznik.)
