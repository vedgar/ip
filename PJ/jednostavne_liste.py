# Napišimo interpreter za programski "jezik" koji reprezentira liste.
# Liste se pišu kao [x1,x2,...,xk], svaki xi može biti broj ili string.
# Brojevi su samo prirodni (veći od 0).
# Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
# Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
# Zapravo, stringovi smiju sadržavati i " i ', ali escape-ane znakom \.

from pj import *

class L(enum.Enum):
    UOTV, UZATV, ZAREZ = '[],'
    class BROJ(Token):
        def vrijednost(self):
            return int(self.sadržaj)
    class STRING(Token):
        def vrijednost(self):
            return self.sadržaj.replace('\\', '')

def l_lex(lista):
    lex = Tokenizer(lista)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isdigit() and znak != '0':
            lex.zvijezda(str.isdigit)
            yield lex.token(L.BROJ)
        elif znak == '"':
            lex.token(E.VIŠAK)
            escape = False
            while True:
                z = lex.čitaj()
                if not z: lex.greška('Nezavršeni string!')
                elif z == '\\': lex.čitaj()
                elif z == '"':
                    lex.vrati()
                    yield lex.token(L.STRING)
                    lex.pročitaj('"')
                    lex.token(E.VIŠAK)
                    break
        elif znak == "'":
            lex.token(E.VIŠAK)
            lex.zvijezda(lambda znak: znak != "'")
            yield lex.token(L.STRING)
            lex.pročitaj("'")
            lex.token(E.VIŠAK)
        else: yield lex.token(operator(L, znak) or lex.greška())

# lista -> UOTV elementi UZATV
# elementi -> element | element ZAREZ elementi | ''
# element -> BROJ | STRING

class LParser(Parser):
    def lista(self):
        self.pročitaj(L.UOTV)
        el = self.elementi()
        self.pročitaj(L.UZATV)
        return el
        
    def elementi(self):
        rezultat = []
        if not self >= L.UZATV:
            rezultat.append(self.element())
            while self >> L.ZAREZ:
                rezultat.append(self.element())
        return rezultat

    def element(self):
        return self.pročitaj(L.BROJ, L.STRING)
    
    start = lista


def vrijednost(l):
    return [el.vrijednost() for el in l]

if __name__ == '__main__':
    print(vrijednost(LParser.parsiraj(l_lex(r'''
        [23, "ab\"c]", 'a[]', 523]
    '''))))
