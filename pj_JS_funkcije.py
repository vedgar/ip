# 2010 K2-popravni Z1,Z2

from pj import *

class JS(enum.Enum):
    FUNCTION = 'function'
    IME = 'ime_funkcije_ili_argumenta'
    O_OTV = '('
    O_ZATV = ')'
    VAR = 'var'
    ZAREZ = ','
    V_OTV = '{'
    V_ZATV = '}'
    KOMENTAR = '//'
    KOSACRTA = '/'
    TOČKAZAREZ = ';'
    NAREDBA = 'naredba'


def js_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.token(ključna_riječ(JS, lex.sadržaj) or JS.IME)
        elif znak == '/':
            if lex.čitaj() == '/':
                lex.zvijezda(lambda znak: znak != '\n')
                lex.pročitaj('\n')
                yield lex.token(JS.KOMENTAR)
            else:
                lex.vrati()
                yield lex.token(JS.KOSACRTA)
        else: yield lex.token(operator(JS, znak) or lex.greška())

### Beskontekstna gramatika
# funkcija -> FUNCTION IME O_OTV argumenti O_ZATV V_OTV tijelo V_ZATV
# argumenti -> VAR IME ZAREZ argumenti | VAR IME | ε
# tijelo -> možda_komentari naredbe možda_komentari
# možda_komentari -> ε | komentari
# komentari -> KOMENTAR komentari | KOMENTAR
# naredbe -> naredba separator naredbe | naredba
# separator -> TOČKAZAREZ | komentari

class Funkcija(AST('ime argumenti tijelo')): pass

class JSParser(Parser):
    def funkcija(self):
        self.pročitaj(JS.FUNCTION)
        ime = self.pročitaj(JS.IME)
        self.pročitaj(JS.O_OTV)
        if self >> JS.O_ZATV: argumenti = []
        else:
            argumenti = [self.argument()]
            while not self >> JS.O_ZATV:
                self.pročitaj(JS.ZAREZ)
                argumenti.append(self.argument())
        self.pročitaj(JS.V_OTV)
        while self >> JS.KOMENTAR: pass
        naredbe = [self.naredba()]
        while True:
            if self >> JS.KOMENTAR:
                while self >> JS.KOMENTAR: pass
                if self >> JS.V_ZATV: return Funkcija(ime, argumenti, naredbe)
                else: naredbe.append(self.naredba())
            elif self >> JS.TOČKAZAREZ: naredbe.append(self.naredba())
            else:
                self.pročitaj(JS.V_ZATV)
                return Funkcija(ime, argumenti, naredbe)

    start = funkcija

    def argument(self):
        self.pročitaj(JS.VAR)
        return self.pročitaj(JS.IME)

    def naredba(self):
        return self.pročitaj(JS.NAREDBA)

if __name__ == '__main__':
    print(JSParser.parsiraj(js_lex('''\
        function ime (var x, var y, var z) {
            //neke naredbe odvojenih s ; ili komentar
            naredba; naredba //kom
            naredba
        }
    ''')))
