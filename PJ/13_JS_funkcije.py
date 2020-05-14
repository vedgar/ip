"""Leksički i sintaksni analizator za JavaScriptove funkcije.
Kolokvij 19. siječnja 2012. (Puljić)
"""


from pj import *


class JS(enum.Enum):
    FUNCTION, VAR, NAREDBA = 'function', 'var', 'naredba'
    O_OTV, O_ZATV, V_OTV, V_ZATV, KOSACRTA, ZAREZ, TOČKAZAREZ = '(){}/,;'
    KOMENTAR = '//'
    class IME(Token): pass


def js_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.literal(JS.IME)
        elif znak == '/':
            if lex.slijedi('/'):
                lex.pročitaj_do('\n')
                yield lex.token(JS.KOMENTAR)
            else: yield lex.token(JS.KOSACRTA)
        else: yield lex.literal(JS)


### Beskontekstna gramatika
# funkcija -> FUNCTION IME O_OTV argumenti O_ZATV V_OTV tijelo V_ZATV
# argumenti -> VAR IME ZAREZ argumenti | VAR IME | ''
# tijelo -> komentari naredbe | naredbe
# komentari -> KOMENTAR komentari | KOMENTAR
# naredbe -> NAREDBA separator naredbe | NAREDBA | ''
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
            else: raise self.greška()
        return naredbe

    def start(self):
        funkcije = [self.funkcija()]
        while not self >> E.KRAJ: funkcije.append(self.funkcija())
        return Program(funkcije)

    def argument(self):
        self.pročitaj(JS.VAR)
        return self.pročitaj(JS.IME)

    def naredba(self): return self.pročitaj(JS.NAREDBA)


if __name__ == '__main__':
    prikaz(JSParser.parsiraj(js_lex('''\
        function ime (var x, var y, var z) {
            //neke naredbe odvojene s ; ili komentarima
            naredba; naredba //kom
            naredba
        }
        function ništa(){}
        function trivijalna(var hmmm){naredba//
        //
        }
    ''')), 3)
# Program(funkcije=[
#   Funkcija(ime=IME'ime', argumenti=[IME'x', IME'y', IME'z'], tijelo=[
#     NAREDBA'naredba', NAREDBA'naredba', NAREDBA'naredba']),
#   Funkcija(ime=IME'ništa', argumenti=[], tijelo=[]),
#   Funkcija(ime=IME'trivijalna', argumenti=[IME'hmmm'], tijelo=[
#     NAREDBA'naredba'])])
