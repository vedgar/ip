r"""Interpreter za programski "jezik" koji reprezentira liste.
Liste se pišu kao [x1,x2,...,xk], svaki xi može biti broj, string ili lista.
Brojevi su samo prirodni (veći od 0).
Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
Zapravo, "..."-stringovi smiju sadržavati i ", ali escape-ane znakom \.
Dakle, \" označava ". \n označava novi red. \\ označava \.
Unutar '...'-stringova \ nema nikakvo posebno značenje.
"""


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

class L(enum.Enum):
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

def l_lex(lista):
    lex = Tokenizer(lista)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit() and znak != '0':
            lex.zvijezda(str.isdigit)
            yield lex.token(L.BROJ)
        elif znak == N1:
            lex.pročitaj_do(N1)
            yield lex.token(L.STRING1)
        elif znak == N2:
            while True:
                z = lex.čitaj()
                if not z: raise lex.greška('Nezavršeni string!')
                elif z == BKSL: lex.čitaj()
                elif z == N2:
                    yield lex.token(L.STRING2)
                    break
        else: yield lex.literal(L)

## Beskontekstna gramatika
# element -> BROJ | STRING1 | STRING2 | lista
# lista -> UOTV elementi UZATV
# elementi -> element | element ZAREZ elementi | ''

class LParser(Parser):
    def lista(self):
        self.pročitaj(L.UOTV)
        el = self.elementi()
        self.pročitaj(L.UZATV)
        return Lista(el)
        
    def elementi(self):
        rezultat = []
        if not self >= L.UZATV:
            rezultat.append(self.element())
            while self >> L.ZAREZ: rezultat.append(self.element())
        return rezultat

    def element(self):
        if self >= L.UOTV: return self.lista()
        else: return self.pročitaj(L.BROJ, L.STRING1, L.STRING2)
    
    start = element


class Lista(AST('elementi')):
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]


if __name__ == '__main__':
    lista = r'''
        [23, "ab\"c]", 'a[]', [2, 3], 523,
        '"', '\', "\e", "\\"]
    '''
    print(lista)
    tokeni = list(l_lex(lista))
    print(*tokeni)
    ast = LParser.parsiraj(tokeni)
    prikaz(ast, 4)
    print(ast.vrijednost())

# DZ: sve više jezika dopušta stil pisanja listi s opcionalnim zarezom na kraju
#     ([2,3,] je isto što i [2,3]) -- omogućite to (u gramatici gore već jest)!
# DZ: omogućite razne druge \-escape sekvence (npr. \u za znakove Unikoda)
# DZ: omogućite izraze umjesto literala: polimorfni + za zbrajanje/konkatenaciju
