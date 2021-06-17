"""Leksički i sintaksni analizator za JavaScriptove funkcije.
Po uzoru na kolokvij 19. siječnja 2012. (Puljić).

Lexer nije sasvim regularan jer broji slojeve vitičastih zagrada
kako bi znao predstavlja li niz znakova (koji može početi znakom $
u skladu s tradicijom JavaScripta) ime parametra funkcije ili naredba."""


from vepar import *


class T(TipoviTokena):
    FUNCTION, VAR, KOMENTAR = 'function', 'var', '//'
    O_OTV, O_ZATV, V_OTV, V_ZATV, KOSACRTA, ZAREZ, TOČKAZAREZ = '(){}/,;'
    class IME(Token): pass
    class NAREDBA(Token): pass

@lexer
def js(lex):
    ugniježđenost = 0
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isalpha() or znak in {'$', '_'}:
            lex * {str.isalnum, '$', '_'}
            default = T.NAREDBA if ugniježđenost else T.IME
            yield lex.literal_ili(default)
        elif znak == '/':
            if lex >= '/':
                lex - '\n'
                yield lex.token(T.KOMENTAR)
            else: yield lex.token(T.KOSACRTA)
        else:
            token = lex.literal(T)
            if token ^ T.V_OTV: ugniježđenost += 1
            elif token ^ T.V_ZATV: ugniježđenost -= 1
            yield token


### Beskontekstna gramatika
# start -> fun | start fun
# fun -> FUNCTION IME O_OTV argumenti? O_ZATV V_OTV KOMENTAR* nar V_ZATV
# argumenti -> VAR IME | argumenti ZAREZ VAR IME
# nar -> NAREDBA TOČKAZAREZ nar | NAREDBA KOMENTAR+ nar | NAREDBA | ''

class P(Parser):
    def funkcija(p) -> 'Funkcija':
        p >> T.FUNCTION
        ime = p >> T.IME
        p >> T.O_OTV
        argumenti = []
        if p > T.VAR:
            argumenti = [p.argument()]
            while p >= T.ZAREZ: argumenti.append(p.argument())
        p >> T.O_ZATV
        return Funkcija(ime, argumenti, p.tijelo())

    def tijelo(p) -> 'naredba*':
        p >> T.V_OTV
        while p >= T.KOMENTAR: pass
        naredbe = []
        while not p >= T.V_ZATV:
            naredbe.append(p >> T.NAREDBA)
            if p >= T.TOČKAZAREZ: pass
            elif p > T.KOMENTAR:
                while p >= T.KOMENTAR: pass
            elif p >> T.V_ZATV: break
        return naredbe

    def start(p) -> 'Program':
        funkcije = [p.funkcija()]
        while not p > KRAJ: funkcije.append(p.funkcija())
        return Program(funkcije)

    def argument(p) -> 'IME':
        p >> T.VAR
        return p >> T.IME


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
        naredba; druga_naredba //kom 
        još_jedna_naredba
    }
    function ništa(){}
    function $trivijalna(var hmmm){n// komm/
    //
    }
'''), 3)

with SintaksnaGreška: P('function n(){naredba naredba;}')
