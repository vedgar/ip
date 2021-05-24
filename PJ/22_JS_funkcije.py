"""Leksički i sintaksni analizator za JavaScriptove funkcije.
Kolokvij 19. siječnja 2012. (Puljić)"""


from vepar import *


class T(TipoviTokena):
    FUNCTION, VAR, NAREDBA, KOMENTAR = 'function', 'var', 'naredba', '//'
    O_OTV, O_ZATV, V_OTV, V_ZATV, KOSACRTA, ZAREZ, TOČKAZAREZ = '(){}/,;'
    IME = TipTokena()


def js(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha() or znak == '$':
            lex * {str.isalpha, '_'}
            yield lex.literal(T.IME)
        elif znak == '/':
            if lex >= '/':
                lex - '\n'
                yield lex.token(T.KOMENTAR)
            else: yield lex.token(T.KOSACRTA)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# start -> fun | start fun
# fun -> FUNCTION IME O_OTV argumenti? O_ZATV V_OTV KOMENTAR* nar V_ZATV
# argumenti -> VAR IME ZAREZ argumenti | VAR IME
# nar -> NAREDBA TOČKAZAREZ nar | NAREDBA KOMENTAR+ nar | NAREDBA | ''

class P(Parser):
    lexer = js

    def funkcija(p):
        p >> T.FUNCTION
        ime = p >> T.IME
        p >> T.O_OTV
        argumenti = []
        if p > T.VAR:
            argumenti = [p.argument()]
            while p >= T.ZAREZ: argumenti.append(p.argument())
        p >> T.O_ZATV
        return Funkcija(ime, argumenti, p.tijelo())

    def tijelo(p):
        p >> T.V_OTV
        while p >= T.KOMENTAR: pass
        naredbe = []
        while not p >= T.V_ZATV:
            naredbe.append(p.naredba())
            if p >= T.TOČKAZAREZ: pass
            elif p > T.KOMENTAR:
                while p >= T.KOMENTAR: pass
            elif p >> T.V_ZATV: break
        return naredbe

    def start(p):
        funkcije = [p.funkcija()]
        while not p > KRAJ: funkcije.append(p.funkcija())
        return Program(funkcije)

    def argument(p):
        p >> T.VAR
        return p >> T.IME

    def naredba(p): return p >> T.NAREDBA


### AST
# Funkcija: ime:IME argumenti:[IME] tijelo:[NAREDBA]
# Program: funkcije:[Funkcija]

class Funkcija(AST):
    ime: 'IME'
    argumenti: 'IME*'
    tijelo: 'NAREDBA*'

class Program(AST):
    funkcije: 'Funkcija*'


prikaz(P('''
    function ime (var x, var y, var z) {
        //neke naredbe odvojene s ; ili komentarima
        naredba; naredba //kom 
        naredba
    }
    function ništa(){}
    function $trivijalna(var hmmm){naredba// komm/
    //
    }
'''), 3)
