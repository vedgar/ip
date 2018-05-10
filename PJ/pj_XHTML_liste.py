from pj import *


class HTML(enum.Enum):
    HTML, ZHTML = 'html', 'Zhtml'
    HEAD, ZHEAD = 'head', 'Zhead'
    BODY, ZBODY = 'body', 'Zbody'
    OL, ZOL = 'ol', 'Zol'
    UL, ZUL = 'ul', 'Zul'
    LI, ZLI = 'li', 'Zli'
    TEXT = 'neki tekst'


def html_lex(string):
    def preskoči_praznine():
        lex.zvijezda(str.isspace)
        lex.token(E.PRAZNO)

    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): preskoči_praznine()
        elif znak == '<':
            pref = ''
            preskoči_praznine()
            if lex.slijedi('/'):
                pref = 'Z'
                preskoči_praznine()
            lex.zvijezda(str.isalpha)
            yield lex.token(ključna_riječ(HTML, pref + lex.sadržaj) or E.GREŠKA)
            preskoči_praznine(), lex.pročitaj('>'), preskoči_praznine()
        else:
            lex.zvijezda(lambda z: z and not z.isspace() and z != '<')
            yield lex.token(HTML.TEXT)            


### Beskontekstna gramatika
# dokument -> HTML HEAD tekst ZHEAD BODY tijelo ZBODY ZHTML
# tekst -> TEXT | TEXT tekst
# tijelo -> ε | element tijelo
# element -> tekst | OL stavke ZOL | UL stavke ZUL
# stavke -> LI element ZLI | LI element ZLI stavke

### Apstraktna sintaksna stabla
# Dokument: zaglavlje, tijelo
# Lista: uređena:bool, stavke
# Tekst: dijelovi


class XLParser(Parser):
    def start(self):
        self.pročitaj(HTML.HTML), self.pročitaj(HTML.HEAD)
        zaglavlje = self.tekst()
        self.pročitaj(HTML.ZHEAD), self.pročitaj(HTML.BODY)
        tijelo = self.tijelo()
        self.pročitaj(HTML.ZBODY), self.pročitaj(HTML.ZHTML)
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
        elif self >= HTML.TEXT:
            return self.tekst()
        else: self.greška()

    def stavke(self):
        self.pročitaj(HTML.LI)
        rezultat = [self.element()]
        self.pročitaj(HTML.ZLI)
        while self >> HTML.LI:
            stavka = self.element()
            self.pročitaj(HTML.ZLI)
            rezultat.append(stavka)
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
        if razina:
            print('\t' * razina, end=prefiks)
        for dio in self.dijelovi:
            print(dio.sadržaj, end=' ')
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
            I još malo hm.<ul><li>jauč!</li></ul>Hm.
        </body>
    </html>
'''))

r.render()
