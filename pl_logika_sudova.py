from plutil import *


class LS(enum.Enum):
    PVAR = 'P1'
    NEG = '!'
    KONJ = '&'
    DISJ = '|'
    KOND = '->'
    BIKOND = '<->'
    OTV = '('
    ZATV = ')'


def ls_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak == 'P':
            prvo = lex.čitaj()
            if not prvo.isdigit(): lex.greška('očekivana znamenka')
            if prvo != '0': lex.zvijezda(str.isdigit)
            yield lex.token(LS.PVAR)
        elif znak == '-':
            lex.očekuj('>')
            yield lex.token(LS.KOND)
        elif znak == '<':
            lex.očekuj('->')
            yield lex.token(LS.BIKOND)
        else: yield lex.token(operator(LS, znak) or lex.greška())


# Beskontekstna gramatika:
# formula -> NEG formula | PVAR | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND

class Negacija(AST('ispod')): """Negacija formule ispod."""
class Binarna(AST('veznik lijevo desno')): "Formula s glavnim binarnim veznikom"

class LSParser(Parser):
    def formula(self):
        početak = self.pročitaj(LS.NEG, LS.PVAR, LS.OTV)
        if početak ** LS.PVAR: return početak
        elif početak ** LS.NEG: return Negacija(self.formula())
        elif početak ** LS.OTV:
            lijevo = self.formula()
            veznik = self.pročitaj(LS.KONJ, LS.DISJ, LS.KOND, LS.BIKOND)
            desno = self.formula()
            self.pročitaj(LS.ZATV)
            return Binarna(veznik, lijevo, desno)

def ls_parse(niz_znakova):
    parser = LSParser(ls_lex(niz_znakova))
    rezultat = parser.formula()
    parser.pročitaj(E.KRAJ)
    return rezultat


def ls_interpret(fo, **interpretacija):
    def I(fo):
        if fo ** LS.PVAR: return interpretacija[fo.sadržaj]
        elif fo ** Negacija: return not I(fo.ispod)
        elif fo.veznik ** LS.DISJ: return I(fo.lijevo) or I(fo.desno)
        elif fo.veznik ** LS.KONJ: return I(fo.lijevo) and I(fo.desno)
        elif fo.veznik ** LS.KOND: return not I(fo.lijevo) or I(fo.desno)
        elif fo.veznik ** LS.BIKOND: return I(fo.lijevo) == I(fo.desno)
        else: assert False
    return I(fo)

def ls_optimize(fo):
    """Jednostavna optimizacija, pojednostavljuje !!F u F svuda u formuli."""
    if fo ** LS.PVAR: return fo
    elif fo ** Binarna:
        return Binarna(fo.veznik, ls_optimize(fo.lijevo), ls_optimize(fo.desno))
    elif fo ** Negacija:
        oi = ls_optimize(fo.ispod)
        if oi ** Negacija: return oi.ispod
        return Negacija(oi)
    else: assert False

if __name__ == '__main__':
    ulaz = '!(P5&!!(P3->P1))'
    print(*ls_lex(ulaz), sep='\n')
    fo = ls_parse(ulaz)
    print(fo)
    fo = ls_optimize(fo)
    print(fo)
    print(ls_interpret(fo, P1=False, P3=True, P5=False))
