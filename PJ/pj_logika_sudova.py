from pj import *


class LS(enum.Enum):
    NEG, KONJ, DISJ, OTV, ZATV = '!&|()'
    KOND, BIKOND = '->', '<->'
    class PVAR(Token):
        def vrijednost(self, **interpretacija):
            try: return interpretacija[self.sadržaj]
            except KeyError: self.nedeklaracija()
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
        else: yield lex.token(operator(LS, znak) or lex.greška())


### Beskontekstna gramatika:
# formula -> NEG formula | PVAR | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

### Apstraktna sintaksna stabla:
# Negacija: ispod
# Binarna: veznik lijevo desno

class LSParser(Parser):
    def formula(self):
        if self >> LS.PVAR: return self.zadnji
        elif self >> LS.NEG: return Negacija(self.formula())
        elif self >> LS.OTV:
            lijevo = self.formula()
            veznik = self.pročitaj(LS.KONJ, LS.DISJ, LS.KOND, LS.BIKOND)
            desno = self.formula()
            self.pročitaj(LS.ZATV)
            return Binarna(veznik, lijevo, desno)
        else: self.greška()

    start = formula


class Negacija(AST('ispod')):
    def vrijednost(formula, **interpretacija):
        return not formula.ispod.vrijednost(**interpretacija)

    def optim(formula):
        i = formula.ispod.optim()
        return i.ispod if i ** Negacija else Negacija(i)
        
class Binarna(AST('veznik lijevo desno')):
    def vrijednost(formula, **interpretacija):
        v = formula.veznik
        l = formula.lijevo.vrijednost(**interpretacija)
        d = formula.desno.vrijednost(**interpretacija)
        if v ** LS.DISJ: return l or d
        elif v ** LS.KONJ: return l and d
        elif v ** LS.KOND: return l <= d
        elif v ** LS.BIKOND: return l == d
        else: assert not 'slučaj'

    def optim(formula):
        l, d = formula.lijevo.optim(), formula.desno.optim()
        return Binarna(formula.veznik, l, d)


if __name__ == '__main__':
    ulaz = '!(P5&!!(P3->P1))'
    tokeni = list(ls_lex(ulaz))
    print(*tokeni)
    fo = LSParser.parsiraj(tokeni)
    print(fo)
    fo = fo.optim()
    print(fo)
    print(fo.vrijednost(P1=False, P3=True, P5=False))
