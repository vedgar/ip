from pj import *

class DS(enum.Enum): OOTV, OZATV, UOTV, UZATV, ILI, NE, SLOVO = "()[]+'a"

def ds_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalpha(): yield lex.token(DS.SLOVO)
        else: yield lex.token(operator(DS, znak) or lex.greška())

### Beskontekstna gramatika
# sklop -> sklop ILI disjunkt | disjunkt
# disjunkt -> faktor disjunkt | faktor
# faktor -> SLOVO | faktor NE | OOTV sklop OZATV | UOTV sklop UZATV

class DSParser(Parser):
    def sklop(self):
        disjunkti = [self.disjunkt()]
        while self >> DS.ILI: disjunkti.append(self.disjunkt())
        return disjunkti[0] if len(disjunkti) == 1 else Or(disjunkti)

    def disjunkt(self):
        konjunkti = [self.faktor()]
        while self >> {DS.SLOVO, DS.OOTV, DS.UOTV}:
            self.vrati()
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
        else: self.greška()
        while self >> DS.NE: trenutni = Not(trenutni)
        return trenutni

    start = sklop

class And(AST('ulazi')): pass
class Or(AST('ulazi')): pass
class Not(AST('ulaz')): pass

def uNand(sklop):
    if sklop ** Not: return [uNand(sklop.ulaz)]
    elif sklop ** DS.SLOVO: return sklop.sadržaj
    elif sklop ** And: return [[uNand(ulaz) for ulaz in sklop.ulazi]]
    elif sklop ** Or: return [[uNand(ulaz)] for ulaz in sklop.ulazi]
    else: assert not 'slučaj'

def pod_negacijom(sklop):
    """Vraća x ako je sklop == [x], inače None."""
    if isinstance(sklop, list) and len(sklop) == 1: return sklop[0]

def optimiziraj(sklop):
    if isinstance(sklop, str): return sklop
    opt = [optimiziraj(ulaz) for ulaz in sklop]
    return pod_negacijom(pod_negacijom(opt)) or opt

opis = "x([yxx']+y')"
tokeni = list(ds_lex(opis))
print(*tokeni)  # SLOVO'x' OOTV'(' UOTV'[' SLOVO'y' SLOVO'x' SLOVO'x'
                # NE"'" UZATV']' ILI'+' SLOVO'y' NE"'" OZATV')'
ast = DSParser.parsiraj(tokeni)
print(ast)  # And(ulazi=[
            #   SLOVO'x',
            #   Or(ulazi=[
            #     Not(ulaz=And(ulazi=[SLOVO'y', SLOVO'x', Not(ulaz=SLOVO'x')])),
            #     Not(ulaz=SLOVO'y')
            #   ])
            # ])
nand = uNand(ast)
print(nand)  # [['x', [[[[['y', 'x', ['x']]]]], [['y']]]]]
opt = optimiziraj(nand)
print(opt)  # [['x', [[['y', 'x', ['x']]], 'y']]]
