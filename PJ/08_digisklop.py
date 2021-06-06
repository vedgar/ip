"""Hardverski NAND-realizator i optimizator digitalnih sklopova.
Zadatak s drugog kolokvija ljetnog semestra 2017. https://goo.gl/JGACGH
Kao međuprikaz (koji se optimizira) korištene su Pythonove liste."""


from vepar import *


class T(TipoviTokena):
    OOTV, OZATV, UOTV, UZATV, ILI, NE = "()[]+'"
    class SLOVO(Token):
        def uNand(t): return t.sadržaj

@lexer
def ds(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha(): yield lex.token(T.SLOVO)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# sklop -> disjunkt | sklop ILI disjunkt
# disjunkt -> faktor | disjunkt faktor
# faktor -> SLOVO | faktor NE | OOTV sklop OZATV | UOTV sklop UZATV

class P(Parser):
    def sklop(p) -> 'Or|disjunkt':
        disjunkti = [p.disjunkt()]
        while p >= T.ILI: disjunkti.append(p.disjunkt())
        return Or.ili_samo(disjunkti)

    def disjunkt(p) -> 'And|faktor':
        konjunkti = [p.faktor()]
        while p > {T.SLOVO, T.OOTV, T.UOTV}: konjunkti.append(p.faktor())
        return And.ili_samo(konjunkti)

    def faktor(p) -> 'sklop|Not|SLOVO':
        if p >= T.OOTV:
            trenutni = p.sklop()
            p >> T.OZATV
        elif p >= T.UOTV:
            trenutni = Not(p.sklop())
            p >> T.UZATV
        else: trenutni = p >> T.SLOVO
        while p >= T.NE: trenutni = Not(trenutni)
        return trenutni


class Not(AST):
    ulaz: 'sklop'
    def uNand(self): return [self.ulaz.uNand()]

class And(AST):
    ulazi: 'sklop*'
    def uNand(self): return [[ulaz.uNand() for ulaz in self.ulazi]]

class Or(AST):
    ulazi: 'sklop*'
    def uNand(self): return [[ulaz.uNand()] for ulaz in self.ulazi]


def pod_negacijom(sklop):
    """Vraća x ako je sklop == [x], inače None."""
    if isinstance(sklop, list) and len(sklop) == 1: return sklop[0]

def optimiziraj(sklop):
    if isinstance(sklop, str): return sklop
    opt = [optimiziraj(ulaz) for ulaz in sklop]
    return pod_negacijom(pod_negacijom(opt)) or opt


print(opis := "x ([yxx'] + y')")
ds(opis)
prikaz(ast := P(opis))
print(nand := ast.uNand())  # [['x', [[[[['y', 'x', ['x']]]]], [['y']]]]]
print(optimiziraj(nand))
