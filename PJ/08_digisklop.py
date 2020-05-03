"""Hardverski NAND-realizator i optimizator digitalnih sklopova.
Zadatak s drugog kolokvija ljetnog semestra 2017. https://goo.gl/JGACGH
"""


from pj import *


class DS(enum.Enum):
    OOTV, OZATV, UOTV, UZATV, ILI, NE = "()[]+'"
    class SLOVO(Token):
        def uNand(self): return self.sadržaj


def ds_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha(): yield lex.token(DS.SLOVO)
        else: yield lex.literal(DS)


### Beskontekstna gramatika
# sklop -> sklop ILI disjunkt | disjunkt
# disjunkt -> disjunkt faktor | faktor
# faktor -> SLOVO | faktor NE | OOTV sklop OZATV | UOTV sklop UZATV


class DSParser(Parser):
    def sklop(self):
        disjunkti = [self.disjunkt()]
        while self >> DS.ILI: disjunkti.append(self.disjunkt())
        return disjunkti[0] if len(disjunkti) == 1 else Or(disjunkti)

    def disjunkt(self):
        konjunkti = [self.faktor()]
        while self >= {DS.SLOVO, DS.OOTV, DS.UOTV}:
            konjunkti.append(self.faktor())
        return konjunkti[0] if len(konjunkti) == 1 else And(konjunkti)

    def faktor(self):
        if self >> DS.SLOVO: trenutni = self.zadnji
        elif self >> DS.OOTV:
            trenutni = self.sklop()
            self.pročitaj(DS.OZATV)
        elif self >> DS.UOTV:
            trenutni = Not(self.sklop())
            self.pročitaj(DS.UZATV)
        else: raise self.greška()
        while self >> DS.NE: trenutni = Not(trenutni)
        return trenutni

    start = sklop


class Not(AST('ulaz')):
    def uNand(self): return [self.ulaz.uNand()]

class And(AST('ulazi')):
    def uNand(self): return [[ulaz.uNand() for ulaz in self.ulazi]]

class Or(AST('ulazi')):
    def uNand(self): return [[ulaz.uNand()] for ulaz in self.ulazi]


def pod_negacijom(sklop):
    """Vraća x ako je sklop == [x], inače None."""
    if isinstance(sklop, list) and len(sklop) == 1: return sklop[0]

def optimiziraj(sklop):
    if isinstance(sklop, str): return sklop
    opt = [optimiziraj(ulaz) for ulaz in sklop]
    return pod_negacijom(pod_negacijom(opt)) or opt


opis = "x([yxx']+y')"
print(opis)

tokeni = list(ds_lex(opis))
print(*tokeni)  # SLOVO'x' OOTV'(' UOTV'[' SLOVO'y' SLOVO'x' SLOVO'x'
                # NE"'" UZATV']' ILI'+' SLOVO'y' NE"'" OZATV')'

ast = DSParser.parsiraj(tokeni)
prikaz(ast, 4)
# And(ulazi=[
#   SLOVO'x',
#   Or(ulazi=[
#     Not(ulaz=And(ulazi=[SLOVO'y', SLOVO'x', Not(ulaz=SLOVO'x')])),
#     Not(ulaz=SLOVO'y')
#   ])
# ])
nand = ast.uNand()
print(nand)  # [['x', [[[[['y', 'x', ['x']]]]], [['y']]]]]
opt = optimiziraj(nand)
print(opt)  # [['x', [[['y', 'x', ['x']]], 'y']]]
