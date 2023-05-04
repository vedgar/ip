r"""Interpreter za programski "jezik" koji reprezentira liste.
Liste se pišu kao [x1,x2,...,xk], svaki xi može biti broj, string ili lista.
Neprazne liste mogu imati "viseći zarez" prije zatvorene uglate zagrade.
Brojevi su samo prirodni (veći od 0).
Stringovi se pišu kao "...", gdje unutar ... ne smije biti znak ".
Stringovi se mogu pisati i kao '...', gdje unutar ... nema znaka '.
Zapravo, "..."-stringovi smiju sadržavati i ", ali uvedene znakom \.
Dakle, \" označava ". \n označava novi red. \\ označava \.
Unutar '...'-stringova \ nema nikakvo posebno značenje."""


from vepar import *


BKSL, N1, N2, NOVIRED = '\\', "'", '"', '\n'

@cache
def raspiši(string):
    """Interpretira obrnute kose crte (backslashes) u stringu."""
    iterator, rezultat = iter(string), []
    for znak in iterator:
        if znak == BKSL:
            sljedeći = next(iterator)
            if sljedeći == 'n': rezultat.append(NOVIRED)
            else: rezultat.append(sljedeći)
        else: rezultat.append(znak)
    return ''.join(rezultat)

class T(TipoviTokena):
    UOTV, UZATV, ZAREZ = '[],'
    class BROJ(Token):
        """Pozitivni prirodni broj."""
        def vrijednost(t): return int(t.sadržaj)
    class STRING1(Token):
        """String u jednostrukim navodnicima (raw string)."""
        def vrijednost(t): return t.sadržaj[1:-1]
    class STRING2(Token):
        """String u dvostrukim navodnicima (backslash kao escape)."""
        def vrijednost(t): return raspiši(t.sadržaj[1:-1])

@lexer
def listlexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak, nula=False)
            yield lex.token(T.BROJ)
        elif znak == N1:
            lex - N1
            yield lex.token(T.STRING1)
        elif znak == N2:
            while (znak := next(lex)) != N2:
                if not znak:
                    raise lex.greška('nezavršeni string do kraja ulaza!')
                elif znak == NOVIRED:
                    raise lex.greška('nezavršeni string do kraja retka!')
                elif znak == BKSL: next(lex)
            yield lex.token(T.STRING2)
        else: yield lex.literal(T)


## Beskontekstna gramatika
# element -> BROJ | STRING1 | STRING2 | UOTV elementi UZATV
# elementi -> element | elementi ZAREZ element | ''

class P(Parser):
    def element(self) -> 'Lista|BROJ|STRING1|STRING2':
        if self >= T.UOTV:
            if self >= T.UZATV: return Lista([])
            elementi = [self.element()]
            while self >= T.ZAREZ and not self > T.UZATV:
                elementi.append(self.element())
            self >> T.UZATV
            return Lista(elementi)
        else: return self >> {T.BROJ, T.STRING1, T.STRING2}
    

## AST:
# element: Lista: elementi:[element]
#          BROJ: Token
#          STRING1: Token
#          STRING2: Token

class Lista(AST):
    elementi: 'element*'
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]


print(lista := r'''
  [[], 23, "ab\"c]", 'a[]', [2, 3, ], 523, [1,2,2,3], '"', '\', "\e",
   "\\", '', "", "\[", ]
''')
listlexer(lista)
prikaz(ast := P(lista), 2)
print(v := ast.vrijednost())
print(*v, sep='\t')


# DZ: omogućite razne druge \-escape sekvence (npr. \u za znakove Unikoda)
# DZ: omogućite izraze umjesto samih konstantnih vrijednosti:
#         implementirajte polimorfni + za zbrajanje/konkatenaciju
