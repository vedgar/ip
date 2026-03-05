r"""Interpreter za programski "jezik" koji reprezentira liste.
Liste se pišu kao [x1,x2,...,xk]; svaki xi može biti broj, string ili lista.
Neprazne liste mogu imati "viseći zarez" prije zatvorene uglate zagrade.

Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
Zapravo, "..."-stringovi smiju sadržavati i ", ali uvedene znakom \.
Dakle, \" označava ". \n označava novi red. \\ označava \.
Unutar '...'-stringova \ nema nikakvo posebno značenje.

Brojevi su samo prirodni (pozitivni).
Implementiran je operator + koji zna zbrajati liste, stringove i brojeve.
Operatori i rezultat su mu uvijek istog tipa (inače diže TypeError)."""


from vepar import *


class ZNAK: OKOSA, N1, N2, NOVIRED = '\\', "'", '"', '\n'

def raspiši(iterator):
    """Interpretira obrnute kose crte (backslashes)."""
    for znak in iterator:
        if znak == ZNAK.OKOSA:
            sljedeći = next(iterator)
            if sljedeći == 'n': yield ZNAK.NOVIRED
            else: yield sljedeći
        else: yield znak

class T(TipoviTokena):
    UOTV, UZATV, ZAREZ, PLUS = '[],+'
    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)
    class STRING(Token):
        def vrijednost(t):
            match list(t.sadržaj):
                case ZNAK.N1, *r, ZNAK.N1: return ''.join(r)
                case ZNAK.N2, *r, ZNAK.N2: return ''.join(raspiši(iter(r)))
                case _: raise ValueError('Krivo spareni navodnici!')

@lexer
def listlexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak, nula=False)
            yield lex.token(T.BROJ)
        elif znak == ZNAK.N1:
            lex - ZNAK.N1
            yield lex.token(T.STRING)
        elif znak == ZNAK.N2:
            while (znak := next(lex)) != ZNAK.N2:
                if not znak:
                    raise lex.greška('nezavršeni string do kraja ulaza!')
                elif znak == ZNAK.NOVIRED:
                    raise lex.greška('nezavršeni string do kraja retka!')
                elif znak == ZNAK.OKOSA: next(lex)
            yield lex.token(T.STRING)
        else: yield lex.literal(T)


## Beskontekstna gramatika
# element -> BROJ | STRING | UOTV elementi UZATV | element PLUS element
# elementi -> '' | element | element ZAREZ elementi

class P(Parser):
    def element(p):
        if p >= T.UOTV: trenutni = Lista(p.elementi())
        else: trenutni = p >> {T.BROJ, T.STRING}
        while p >= T.PLUS: trenutni = Skupa(trenutni, p.element())
        return trenutni

    def elementi(p):
        popis = []
        while ...:
            if p >= T.UZATV: return popis
            popis.append(p.element())
            if p >= T.UZATV: return popis
            p >> T.ZAREZ


## AST:
# element: Lista: elementi:[element]
#          Skupa: lijevo:element, desno:element
#          BROJ: Token
#          STRING: Token

class Lista(AST):
    elementi: list[P.element]
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]

class Skupa(AST):
    lijevo: P.element
    desno: P.element
    def vrijednost(self):
        try: return self.lijevo.vrijednost() + self.desno.vrijednost()
        except TypeError as ex: raise self.iznimka(ex)


print(lista := r'''
  [[], 23, "ab\"c]", 'a[]', [2, 3, ], 523, [1,2,2,3], '"', '\', "\e",
   "\\", '', "", "\[", ]
''')
listlexer(lista)
prikaz(ast := P(lista), 2)
print(v := ast.vrijednost())
print(*v, sep='«\t')
prikaz(ast := P(''' [] + ["3" + "2" + "1",] + [ 3 + 2 + 1, ""] '''))
print(ast.vrijednost())

# DZ: omogućite razne druge \-escape sekvence (npr. \u za znakove Unikoda)
