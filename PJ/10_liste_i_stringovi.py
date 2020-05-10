r"""Interpreter za programski "jezik" koji reprezentira liste.
Liste se pišu kao [x1,x2,...,xk], svaki xi može biti broj, string ili lista.
Brojevi su samo prirodni (veći od 0).
Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
Zapravo, "..."-stringovi smiju sadržavati i ", ali escape-ane znakom \.
Dakle, \" označava ". \n označava novi red. \\ označava \.
Unutar '...'-stringova \ nema nikakvo posebno značenje."""


from pj import *


BKSL, N1, N2, NOVIRED = '\\', "'", '"', '\n'

def makni(it):
    """Miče obrnute kose crte (backslashes) iz iteratora."""
    for znak in it:
        if znak == BKSL:
            sljedeći = next(it)
            if sljedeći == 'n': yield NOVIRED
            else: yield sljedeći
        else: yield znak

class T(TipoviTokena):
    UOTV, UZATV, ZAREZ = '[],'
    class BROJ(Token):
        """Pozitivni prirodni broj."""
        def vrijednost(self): return int(self.sadržaj)
    class STRING1(Token):
        """String u jednostrukim navodnicima (raw string)."""
        def vrijednost(self): return self.sadržaj[1:-1]
    class STRING2(Token):
        """String u dvostrukim navodnicima (backslash kao escape)."""
        def vrijednost(self): return ''.join(makni(iter(self.sadržaj[1:-1])))

def listlexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit() and znak != '0':
            lex.zvijezda(str.isdigit)
            yield lex.token(T.BROJ)
        elif znak == N1:
            lex.pročitaj_do(N1)
            yield lex.token(T.STRING1)
        elif znak == N2:
            while True:
                z = lex.čitaj()
                if not z: raise lex.greška('Nezavršeni string!')
                elif z == BKSL: lex.čitaj()
                elif z == N2:
                    yield lex.token(T.STRING2)
                    break
        else: yield lex.literal(T)

## Beskontekstna gramatika
# element -> BROJ | STRING1 | STRING2 | lista
# lista -> UOTV elementi UZATV
# elementi -> element | element ZAREZ elementi | ''

## AST:
# element: Lista: elementi:[element]
#          BROJ: Token
#          STRING1: Token
#          STRING2: Token

class P(Parser):
    def lista(self):
        self.pročitaj(T.UOTV)
        el = self.elementi()
        self.pročitaj(T.UZATV)
        return Lista(el)
        
    def elementi(self):
        rezultat = []
        if not self >= T.UZATV:
            rezultat.append(self.element())
            while self >> T.ZAREZ: rezultat.append(self.element())
        return rezultat

    def element(self):
        if self >= T.UOTV: return self.lista()
        else: return self.pročitaj(T.BROJ, T.STRING1, T.STRING2)
    
    lexer = listlexer 
    start = element


class Lista(AST('elementi')):
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]


lista = r'''
    [23, "ab\"c]", 'a[]', [2, 3], 523,
    '"', '\', "\e", "\\"]
'''
print(lista)
P.tokeniziraj(lista)
ast = P(lista)
prikaz(ast, 2)
print(ast.vrijednost())


# DZ: sve više jezika dopušta "zarez na kraju" stil pisanja listi
#     (npr. [2,3,] je isto što i [2,3]) -- omogućite to!
# DZ: omogućite razne druge \-escape sekvence (npr. \u za znakove Unikoda)
# DZ: omogućite izraze umjesto literala: polimorfni + za zbrajanje/konkatenaciju
