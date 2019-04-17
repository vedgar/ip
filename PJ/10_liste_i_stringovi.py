r"""Interpreter za programski "jezik" koji reprezentira liste.
Liste se pišu kao [x1,x2,...,xk], svaki xi može biti broj, string ili lista.
Brojevi su samo prirodni (veći od 0).
Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
Zapravo, "..."-stringovi smiju sadržavati i ", ali escape-ane znakom \.
\n označava novi red. \\ označava \.
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
        def vrijednost(self): return int(self.sadržaj)
    class STRING(Token):
        def vrijednost(self):
            s = self.sadržaj[1:-1]
            if self.sadržaj.startswith(N2): return ''.join(makni(iter(s)))
            else: return s

def l_lex(lista):
    lex = Tokenizer(lista)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit() and znak != '0':
            lex.zvijezda(str.isdigit)
            yield lex.token(L.BROJ)
        elif znak == N1:
            lex.pročitaj_do(N1)
            yield lex.token(L.STRING)
        elif znak == N2:
            while True:
                z = lex.čitaj()
                if not z: raise lex.greška('Nezavršeni string!')
                elif z == BKSL: lex.čitaj()
                elif z == N2:
                    yield lex.token(L.STRING)
                    break
        else: yield lex.literal(L)

# lista -> UOTV elementi UZATV
# elementi -> element | element ZAREZ elementi | ''
# element -> BROJ | STRING | lista

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
        else: return self.pročitaj(L.BROJ, L.STRING)
    
    start = element


class Lista(AST('elementi')):
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]


if __name__ == '__main__':
    print(LParser.parsiraj(l_lex(r'''
        [23, "ab\"c]", 'a[]', [2, 3], 523,
        '"', '\', "\e", "\\"]
    ''')).vrijednost())
