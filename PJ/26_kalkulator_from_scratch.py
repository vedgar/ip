from vepar import *

class T(TipoviTokena):
    PLUS, PUTA, OTV, ZATV = '+', '*', '(', ')'

    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)
        def visina(t): return 1

@lexer
def L(lex):
    for znak in lex:
        if znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)

# BKG
# izraz -> član | član PLUS izraz
# član -> faktor | faktor PUTA član
# faktor -> BROJ | OTV izraz ZATV

class P(Parser):
    def izraz(p):
        s = p.član()
        if p >= T.PLUS: s = Zbroj(s, p.izraz())
        return s

    def član(p):
        s = p.faktor()
        if p >= T.PUTA: s = Umnožak(s, p.član())
        return s

    def faktor(p):
        if p >= T.OTV:
            s = p.izraz()
            p >> T.ZATV
            return s
        else: return p >> T.BROJ

class Zbroj(AST):
    lijevo: ...
    desno: ...

    def visina(s):
        return 1 + max(self.lijevo.visina(), self.desno.visina())

    def pomalo(s):
        if s.visina() == 2:
            ...
        
class Umnožak(Zbroj): ...
