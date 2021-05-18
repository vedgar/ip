"""Renderer za XHTML dokumente koji sadrže samo liste.
Kolokvij 2. veljače 2015. (Puljić)"""


from vepar import *


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
            token = lex.literal(T.TEKST, case=False)
            if token ^ T.TEKST: lex.zanemari()
            else: yield token
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
        self >> T.HTML, self >> T.HEAD
        zaglavlje = self.tekst()
        self >> T.ZHEAD, self >> T.BODY
        tijelo = []
        while not self >= T.ZBODY: tijelo.append(self.element())
        self >> T.ZHTML
        return Dokument(zaglavlje, tijelo)
        
    def tekst(self):
        dijelovi = [self >> T.TEKST]
        while tekst := self >= T.TEKST: dijelovi.append(tekst)
        return Tekst(dijelovi)

    def element(self):
        if vrsta := self >= {T.OL, T.UL}:
            stavke = [self.stavka()]
            while self > T.LI: stavke.append(self.stavka())
            self >> zatvoreni(vrsta.tip)
            return Lista(vrsta, stavke)
        else: return self.tekst()

    def stavka(self):
        self >> T.LI
        rezultat = self.element()
        self >> T.ZLI
        return rezultat
            

class Dokument(AST('zaglavlje tijelo')):
    def render(self):
        for element in self.tijelo: element.render([''])
        print()

class Lista(AST('vrsta stavke')):
    def render(self, prefiks):
        prethodni, zadnji = prefiks[:-1], prefiks[-1]
        for i, stavka in enumerate(self.stavke, 1):
            if i > 1 and zadnji.endswith('\t'): zadnji = '\t'
            if self.vrsta ^ T.OL: marker = f'{i}.'
            elif self.vrsta ^ T.UL: marker = '*#@o-.,_ '[len(prethodni)] + ' '
            stavka.render(prethodni + [zadnji, f'{marker:>7}\t'])

class Tekst(AST('dijelovi')):
    def render(self, prefiks):
        print('\n', *prefiks, sep='', end='')
        for dio in self.dijelovi: dio.render()


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

n = P('''\
    <html>
        <head>_</head>
        <body><ol>
                <li><ol>
                    <li>tekst a</li>
                    <li><ol>
                        <li>tekst b</li>
                        <li>tekst c</li>
                        <li>tekst d</li>
                    </ol></li>
                    <li><ul>
                        <li>tekst e</li>
                        <li>tekst f</li>
                    </ul></li>
                    <li>tekst g</li>
                    <li><ol>
                        <li>tekst h</li>
                    </ol></li>
                    <li>tekst i</li>
                </ol></li>
            </ol>
            I još malo<ul><li>uvučeno</li></ul>
        </body>
    </html>
''')

v = P('''\
        <html>
        <head>_</head>
        <body>
        <ol>
        <li>jedan</li>
        <li>dva</li>
        </ol>
        </body>
        </html>
''')
prikaz(r, 7)
r.render()
