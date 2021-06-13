"""Leksički i sintaksni analizator za JavaScriptove funkcije.
Kolokvij 19. siječnja 2012. (Puljić)"""


from vepar import *


class T(TipoviTokena):
    FUNCTION, VAR, NAREDBA, KOMENTAR = 'function', 'var', 'naredba', '//'
    O_OTV, O_ZATV, V_OTV, V_ZATV, KOSACRTA, ZAREZ, TOČKAZAREZ = '(){}/,;'
    IME = TipTokena()

def js_id(znak):
    return znak.isalnum() or znak in '_$'

def js(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha() or znak in '_$':
            lex.zvijezda(js_id)
            yield lex.literal(T.IME)
        elif znak == '/':
            if lex >= '/':
                lex.pročitaj_do('\n')
                yield lex.token(T.KOMENTAR)
            else: yield lex.token(T.KOSACRTA)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# start -> funkcija | start funkcija
# funkcija -> FUNCTION IME O_OTV argumenti? O_ZATV tijelo
# argumenti -> VAR IME ZAREZ argumenti | VAR IME
# tijelo -> V_OTV KOMENTAR* naredbe V_ZATV
# naredbe -> NAREDBA (TOČKAZAREZ | KOMENTAR+) naredbe | NAREDBA | ''

class P(Parser):
    lexer = js

    def start(self):
        funkcije = [self.funkcija()]
        while not self > KRAJ: funkcije.append(self.funkcija())
        return Program(funkcije)

    def funkcija(self):
        self >> T.FUNCTION
        ime = self >> T.IME
        self >> T.O_OTV
        argumenti = []
        if self > T.VAR:
            argumenti = [self.argument()]
            while self >= T.ZAREZ: argumenti.append(self.argument())
        self >> T.O_ZATV
        return Funkcija(ime, argumenti, self.tijelo())

    def argument(self):
        self >> T.VAR
        return self >> T.IME

    def tijelo(self):
        self >> T.V_OTV
        while self >= T.KOMENTAR: pass
        naredbe = []
        while not self >= T.V_ZATV:
            naredbe.append(self >> T.NAREDBA)
            if self >= T.TOČKAZAREZ: pass
            elif self > T.KOMENTAR:
                while self >= T.KOMENTAR: pass
            elif self >> T.V_ZATV: break
        return naredbe


### AST
# Funkcija: ime:IME argumenti:[IME] tijelo:[NAREDBA]
# Program: funkcije:[Funkcija]

class Funkcija(AST('ime argumenti tijelo')): pass
class Program(AST('funkcije')): pass


prikaz(P('''\
    function ime_1 (var x, var y, var z) {
        //neke naredbe odvojene s ; ili komentarima
        naredba; naredba //kom 
        naredba
    }
    function ništa(){}
    function $trivijalna(var hmmm){naredba// komm/
    //
    }
'''), 3)
