from pj import *

class AQ(enum.Enum):
    NAT, INT, RAT = 'nat', 'int', 'rat'
    PLUS, MINUS, PUTA, KROZ, NA = '+-*/^'
    OTVORENA, ZATVORENA, JEDNAKO, NOVIRED = '()=\n'
    DIV, MOD = 'div', 'mod'
    class IME(Token): ...
    class BROJ(Token): ...


def aq_lex(niz):
    lex = Tokenizer(niz)
    for znak in iter(lex.čitaj, ''):
        if znak == ' ': lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AQ.BROJ)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.token(ključna_riječ(AQ, lex.sadržaj) or AQ.IME)
        elif znak == '\n':
            lex.zvijezda(lambda znak: znak == '\n')
            yield lex.token(AQ.NOVIRED)
        else: yield lex.token(operator(AQ, znak) or lex.greška())


### Beskontekstna gramatika
# start -> NOVIRED? niz_naredbi NOVIRED?
# niz_naredbi -> naredba | naredba NOVIRED niz_naredbi
# naredba -> izraz | (NAT | INT | RAT) IME JEDNAKO izraz
# izraz -> član | izraz (PLUS | MINUS) član
# član -> faktor | član (PUTA | KROZ | DIV | MOD) faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME | OTVORENA izraz ZATVORENA

### Apstraktna sintaksna stabla
# Program: deklaracije izrazi
# Deklaracija: varijabla tip vrijednost
# Potencija: baza eksponent
# Razlomak: brojnik nazivnik
# Umnožak: faktori
# Razlika: umanjenik umanjitelj
# Zbroj: pribrojnici
# Količnik: djeljenik djelitelj
# Ostatak: djeljenik djelitelj
# Suprotan: od


class AQParser(Parser):
    def start(self):
        self >> AQ.NOVIRED
        deklaracije, izrazi = [], []
        while self.do(E.KRAJ):
            naredba = self.naredba()
            (deklaracije if naredba ** Deklaracija else izrazi).append(naredba)
            self.pročitaj(AQ.NOVIRED, E.KRAJ)
        return Program(deklaracije, izrazi)

    def naredba(self):
        if self >> {AQ.NAT, AQ.INT, AQ.RAT}:
            tip = self.zadnji
            varijabla = self.pročitaj(AQ.IME)
            self.pročitaj(AQ.JEDNAKO)
            inicijalizacija = self.izraz()
            return Deklaracija(varijabla, tip, inicijalizacija)
        else: return self.izraz()

    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> AQ.PLUS: trenutni = Zbroj([trenutni, self.član()])
            elif self >> AQ.MINUS: trenutni = Razlika(trenutni, self.član())
            else: return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> AQ.PUTA: trenutni = Umnožak([trenutni, self.faktor()])
            elif self >> AQ.KROZ: trenutni = Razlomak(trenutni, self.faktor())
            elif self >> AQ.DIV: trenutni = Količnik(trenutni, self.faktor())
            elif self >> AQ.MOD: trenutni = Ostatak(trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AQ.MINUS: return Suprotan(self.faktor())
        baza = self.baza()
        if self >> AQ.NA: return Potencija(baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> {AQ.BROJ, AQ.IME}: return self.zadnji
        elif self >> AQ.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AQ.ZATVORENA)
            return u_zagradi
        else: self.greška()


class Program(AST('deklaracije izrazi')):
    def razriješi(self):
        tip, zavisi = {}, {}
        for deklaracija in self.deklaracije:
            v = deklaracija.varijabla
            tip[v], zavisi[v] = deklaracija.razriješi(tip)
    
class Deklaracija(AST('varijabla tip vrijednost')):
    def razriješi(self, tip):
        for prva in tip:
            if prva == v: v.redeklaracija(prva)
        return self.tip, imena(self.vrijednost)

def imena(izraz):
    if isinstance(izraz, AST0):
        for komponenta in izraz:
    for komponenta in self:
        if komponenta

class Potencija(AST('baza eksponent')): pass
class Razlomak(AST('brojnik nazivnik')): pass
class Umnožak(AST('faktori')): pass
class Razlika(AST('umanjenik umanjitelj')): pass
class Zbroj(AST('pribrojnici')): pass
class Količnik(AST('djeljenik djelitelj')): pass
class Ostatak(AST('djeljenik djelitelj')): pass
class Suprotan(AST('od')): pass
