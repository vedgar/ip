from pj import *

class KF(enum.Enum):
    OTV, ZATV = '()'
    class ATOM(Token):
        def Mr(self, **atomi):
            return pogledaj(atomi,self)
    class BROJ(Token):
        def vrijednost(self,**_):
            return int(self.sadržaj)
    class N(Token):
        literal='n'
        def vrijednost(self, **atomi):
            return atomi['n']

def kf_lex(formula):
    lex=Tokenizer(formula)
    for i, znak in enumerate(iter(lex.čitaj, '')):
        print(znak)
        if not i and znak=='n' or znak!=')' and lex.slijedi('n'):
            raise lex.greška("nema ')' prije n!")
        elif znak.isdigit() and znak!='0':
            lex.zvijezda(str.isdigit)
            yield lex.token(KF.BROJ)
        elif znak.isupper():
            idući=lex.čitaj()
            print('"', idući)
            if not idući.islower(): lex.vrati()
            yield lex.literal(KF.ATOM)
        else: yield lex.literal(KF)

### Beskontekstna gramatika
# formula -> formula skupina | skupina
# skupina -> ATOM BROJ? | OTV formula ZATV (N | BROJ)?

### Apstraktna sintaksna stabla
# Formula: skupine:[(Formula, broj|'n')]

jedan=Token(KF.BROJ,'1')

class KFParser(Parser):
    def formula(self):
        skupine=[self.skupina()]
        while not self>={E.KRAJ,KF.ZATV}:
            skupine.append(self.skupina())
        return Formula(skupine)

    def skupina(self):
        if self >> KF.ATOM:
            atom=self.zadnji
            if self >> KF.BROJ:
                broj=self.zadnji
            else:
                broj=jedan
            return (atom,broj)
        else:
            self.pročitaj(KF.OTV)
            f=self.formula()
            self.pročitaj(KF.ZATV)
            if self >> {KF.N, KF.BROJ}:
                broj=self.zadnji
            else:
                broj=jedan
            return (f,broj)

    start = formula

class Formula(AST('skupine')):
    def Mr(self, **atomi):
        suma=0
        for skupina, broj in self.skupine:
            suma += skupina.Mr(**atomi)*broj.vrijednost(**atomi)
        return suma

if __name__=='__main__':
    formula='CabH3(CabH2)nCabH3'
    formula = 'AbcdeF'
    tokeni=list(kf_lex(formula))
    p=KFParser.parsiraj(tokeni)
    print(tokeni,p,p.Mr(Cab=12.01,H=1.008,n=2),sep='\n\n')
