"""Renderer za XHTML dokumente koji sadrže samo liste.
Kolokvij 2. veljače 2015. (Puljić)"""


from pj import *


class T(TipoviTokena):
    HTML, HEAD, BODY = '<html>', '<head>', '<body>'
    ZHTML, ZHEAD, ZBODY = '</html>', '</head>', '</body>'
    OL,ZOL,UL,ZUL,LI,ZLI = '<ol>','</ol>','<ul>','</ul>','<li>','</li>'
    class TEKST(Token):
        def render(self): print(self.sadržaj, end=' ')

def zatvoreni(tag): return T['Z' + tag.name]

def html(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '<':
            lex.pročitaj_do('>')
            yield lex.literal(T.TEKST, case=False)
        else:
            lex.zvijezda(lambda z: z and not z.isspace() and z != '<')
            yield lex.token(T.TEKST)            


### Beskontekstna gramatika
# dokument -> HTML HEAD TEKST+ ZHEAD BODY element* ZBODY ZHTML
# element -> TEKST | OL stavka+ ZOL | UL stavka+ ZUL
# stavka -> LI element ZLI

### Apstraktna sintaksna stabla
# Dokument: zaglavlje:Tekst tijelo:[element]
# element: Lista: vrsta:OL|UL stavke:[element]
#          Tekst: dijelovi:[TEKST]


class P(Parser):
    lexer = html

    def start(self):
        self.pročitaj(T.HTML), self.pročitaj(T.HEAD)
        zaglavlje = self.tekst()
        self.pročitaj(T.ZHEAD), self.pročitaj(T.BODY)
        tijelo = []
        while not self >> T.ZBODY: tijelo.append(self.element())
        self.pročitaj(T.ZHTML)
        return Dokument(zaglavlje, tijelo)
        
    def tekst(self):
        dijelovi = [self.pročitaj(T.TEKST)]
        while self >> T.TEKST: dijelovi.append(self.zadnji)
        return Tekst(dijelovi)

    def element(self):
        if self >> {T.OL, T.UL}:
            vrsta = self.zadnji
            stavke = [self.stavka()]
            while self >= T.LI: stavke.append(self.stavka())
            self.pročitaj(zatvoreni(vrsta.tip))
            return Lista(vrsta, stavke)
        elif self >= T.TEKST: return self.tekst()
        else: raise self.greška()

    def stavka(self):
        self.pročitaj(T.LI)
        rezultat = self.element()
        self.pročitaj(T.ZLI)
        return rezultat
            

class Dokument(AST('zaglavlje tijelo')):
    def render(self):
        for element in self.tijelo: element.render(0, '')
    
class Lista(AST('vrsta stavke')):
    def render(self, razina, prefiks):
        for i, stavka in enumerate(self.stavke, 1):
            if self.vrsta ^ T.OL: prefiks = '{:3}. '.format(i) 
            elif self.vrsta ^ T.UL: prefiks = '  * '
            stavka.render(razina + 1, prefiks)

class Tekst(AST('dijelovi')):
    def render(self, razina, prefiks):
        print('\t' * razina, end=prefiks)
        for dio in self.dijelovi: dio.render()
        print()

r = P('''\
    <html>
        <head>
            bla   bla
        </head>
        <body>
            &hmm;
            hm hm
            <ol>
                <li>Ovo je <a?> prvi item.</li>
                <li>A ovo je drugi.</li>
                <li> Ovo je   --- ne bi čovjek vjerovao  --- treći.</li>
                <li>
                    <ul>
                        <li>
                            <ol>
                                <li>Trostruka dubina!</li>
                            </ol>
                        </li>
                        <li>Dvostruka!</li>
                    </ul>
                </li>
                <li>nastavak...</li>
            </ol>
            I još malo<ul><li>uvučeno</li></ul>
        </body>
    </html>
''')
prikaz(r, 7)
r.render()
