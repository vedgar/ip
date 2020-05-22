"""Renderer za XHTML dokumente koji sadrže samo liste.

Kolokvij 2. veljače 2015. (Puljić)
"""


from pj import *


class HTML(enum.Enum):
    HTML, ZHTML = '<html>', '</html>'
    HEAD, ZHEAD = '<head>', '</head>'
    BODY, ZBODY = '<body>', '</body>'
    OL, ZOL = '<ol>', '</ol>'
    UL, ZUL = '<ul>', '</ul>'
    LI, ZLI = '<li>', '</li>'
    class TEXT(Token): pass


def html_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak == '<':
            lex.pročitaj_do('>')
            yield lex.literal(HTML)
        else:
            lex.zvijezda(lambda z: z and not z.isspace() and z != '<')
            yield lex.token(HTML.TEXT)            


### Beskontekstna gramatika
# dokument -> HTML HEAD tekst ZHEAD BODY tijelo ZBODY ZHTML
# tekst -> TEXT | TEXT tekst
# tijelo -> '' | element tijelo
# element -> tekst | OL stavke ZOL | UL stavke ZUL
# stavke -> LI element ZLI | LI element ZLI stavke

### Apstraktna sintaksna stabla
# Dokument: zaglavlje, tijelo
# Lista: uređena:bool, stavke
# Tekst: dijelovi


class XLParser(Parser):
    def start(self):
        self.pročitaj(HTML.HTML)
        self.pročitaj(HTML.HEAD)
        zaglavlje = self.tekst()
        self.pročitaj(HTML.ZHEAD)
        self.pročitaj(HTML.BODY)
        tijelo = self.tijelo()
        self.pročitaj(HTML.ZBODY)
        self.pročitaj(HTML.ZHTML)
        return Dokument(zaglavlje, tijelo)
        
    def tekst(self):
        dijelovi = [self.pročitaj(HTML.TEXT)]
        while self >> HTML.TEXT: dijelovi.append(self.zadnji)
        return Tekst(dijelovi)

    def tijelo(self):
        sve = []
        while not self >= HTML.ZBODY: sve.append(self.element())
        return sve

    def element(self):
        if self >> HTML.OL:
            lista = Lista(True, self.stavke())
            self.pročitaj(HTML.ZOL)
            return lista
        elif self >> HTML.UL:
            lista = Lista(False, self.stavke())
            self.pročitaj(HTML.ZUL)
            return lista
        else: return self.tekst()

    def stavke(self):
        self.pročitaj(HTML.LI)
        rezultat = [self.element()]
        self.pročitaj(HTML.ZLI)
        while self >> HTML.LI:
            rezultat.append(self.element())
            self.pročitaj(HTML.ZLI)
        return rezultat
            

class Dokument(AST('zaglavlje tijelo')):
    def render(self):
        for element in self.tijelo: element.render(0, '')
    
class Lista(AST('uređena stavke')):
    def render(self, razina, prefiks):
        for i, stavka in enumerate(self.stavke, 1):
            prefiks = '{:3}. '.format(i) if self.uređena else '  * '
            stavka.render(razina + 1, prefiks)

class Tekst(AST('dijelovi')):
    def render(self, razina, prefiks):
        if razina: print('\t' * razina, end=prefiks)
        for dio in self.dijelovi: print(dio.sadržaj, end=' ')
        print()

r = XLParser.parsiraj(html_lex('''\
    <html>
        <head>
            bla   bla
        </head>
        <body>
            12#hmm
            hm hm
            <ol>
                <li>Ovo je prvi item.</li>
                <li>A ovo je drugi.</li>
                <li> Ovo, pak, je   --- ne bi čovjek vjerovao --- treći.</li>
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
            I još malo hm.<ul><li>uvučeno</li></ul>Hm.
        </body>
    </html>
'''))
prikaz(r, 7)
# Dokument(zaglavlje=Tekst(dijelovi=[TEXT'bla', TEXT'bla']), tijelo=[
#   Tekst(dijelovi=[TEXT'12#hmm', TEXT'hm', TEXT'hm']),
#   Lista(uređena=True, stavke=[
#     Tekst(dijelovi=[TEXT'Ovo', TEXT'je', TEXT'prvi', TEXT'item.']),
#     Tekst(dijelovi=[TEXT'A', TEXT'ovo', TEXT'je', TEXT'drugi.']),
#     Tekst(dijelovi=[TEXT'Ovo,', TEXT'pak,', TEXT'je', TEXT'---', TEXT'ne',
#       TEXT'bi', TEXT'čovjek', TEXT'vjerovao', TEXT'---', TEXT'treći.']),
#     Lista(uređena=False, stavke=[
#       Lista(uređena=True, stavke=[
#         Tekst(dijelovi=[TEXT'Trostruka', TEXT'dubina!'])]),
#       Tekst(dijelovi=[TEXT'Dvostruka!'])]),
#     Tekst(dijelovi=[TEXT'nastavak...'])]),
#   Tekst(dijelovi=[TEXT'I', TEXT'još', TEXT'malo', TEXT'hm.']),
#   Lista(uređena=False, stavke=[Tekst(dijelovi=[TEXT'uvučeno'])]),
#   Tekst(dijelovi=[TEXT'Hm.'])])
r.render()
