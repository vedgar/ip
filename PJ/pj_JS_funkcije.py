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
# tijelo -> komentari naredbe | naredbe
# komentari -> KOMENTAR komentari | KOMENTAR
# naredbe -> naredba separator naredbe | naredba | ε
# separator -> TOČKAZAREZ | komentari

class Funkcija(AST('ime argumenti tijelo')): pass
class Program(AST('funkcije')): pass

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
        return Funkcija(ime, argumenti, self.tijelo())

    def tijelo(self):
        self.pročitaj(JS.V_OTV)
        while self >> JS.KOMENTAR: pass
        naredbe = []
        while not self >> JS.V_ZATV:
            naredbe.append(self.naredba())
            if self >> JS.TOČKAZAREZ: pass
            elif self >> JS.KOMENTAR:
                while self >> JS.KOMENTAR: pass
            elif self >> JS.V_ZATV: break
            else: self.greška()
        return naredbe

    def start(self):
        funkcije = [self.funkcija()]
        while not self >> E.KRAJ: funkcije.append(self.funkcija())
        return Program(funkcije)

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
    print(JSParser.parsiraj(js_lex('''\
        function ime (var x, var y, var z) {
            //neke naredbe odvojene s ; ili komentarima
            naredba; naredba //kom
            naredba
        }
        function ništa(){}
        function trivijalna(var hmmm){naredba//
        //
        }
    ''')))
