"""Renderer za XHTML dokumente koji sadrže samo liste.
Kolokvij 2. veljače 2015. (Puljić)"""


from vepar import *


class T(TipoviTokena):
    HTML, HEAD, BODY = '<html>', '<head>', '<body>'
    ZHTML, ZHEAD, ZBODY = '</html>', '</head>', '</body>'
    OL, UL, LI = '<ol>', '<ul>', '<li>'
    ZOL, ZUL, ZLI = '</ol>', '</ul>', '</li>'
    class TEKST(Token):
        def render(t): print(t.sadržaj, end=' ')

@lexer
def html(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '<':
            lex - '>'
            try: token = lex.literal(T, case=False)
            except LeksičkaGreška: lex.zanemari()
            else: yield token
        else:
            lex < {'', '<', str.isspace}
            yield lex.token(T.TEKST)


### Beskontekstna gramatika
# dokument -> HTML HEAD TEKST+ ZHEAD BODY element* ZBODY ZHTML
# element -> TEKST | OL stavka+ ZOL | UL stavka+ ZUL
# stavka -> LI element ZLI


class P(Parser):
    def start(p) -> 'Dokument':
        p >> T.HTML, p >> T.HEAD
        zaglavlje = p.tekst()
        p >> T.ZHEAD, p >> T.BODY
        tijelo = []
        while not p >= T.ZBODY: tijelo.append(p.element())
        p >> T.ZHTML
        return Dokument(zaglavlje, tijelo)
        
    def tekst(p) -> 'Tekst':
        dijelovi = [p >> T.TEKST]
        while tekst := p >= T.TEKST: dijelovi.append(tekst)
        return Tekst(dijelovi)

    def element(p) -> 'Lista|tekst':
        if vrsta := p >= {T.OL, T.UL}:
            stavke = [p.stavka()]
            while p > T.LI: stavke.append(p.stavka())
            if vrsta ^ T.OL: p >> T.ZOL
            elif vrsta ^ T.UL: p >> T.ZUL
            else: assert False, 'nepoznata vrsta liste'
            return Lista(vrsta, stavke)
        else: return p.tekst()

    def stavka(p) -> 'element':
        p >> T.LI
        rezultat = p.element()
        p >> T.ZLI
        return rezultat
            

### Apstraktna sintaksna stabla
# Dokument: zaglavlje:Tekst tijelo:[element]
# element: Lista: vrsta:OL|UL stavke:[element]
#          Tekst: dijelovi:[TEKST]

class Dokument(AST):
    zaglavlje: 'Tekst'
    tijelo: 'element*'
    def render(dokument):
        for element in dokument.tijelo: element.render([''])
        print()

class Lista(AST):
    vrsta: 'OL|UL'
    stavke: 'element*'
    def render(lista, prefiks):
        prethodni, zadnji = prefiks[:-1], prefiks[-1]
        for i, stavka in enumerate(lista.stavke, 1):
            if i > 1 and zadnji.endswith('\t'): zadnji = '\t'
            if lista.vrsta ^ T.OL: marker = f'{i}.'
            elif lista.vrsta ^ T.UL: marker = '*#@o-.,_ '[len(prethodni)] + ' '
            stavka.render(prethodni + [zadnji, f'{marker:>7}\t'])

class Tekst(AST):
    dijelovi: 'TEKST*'
    def render(tekst, prefiks):
        print('\n', *prefiks, sep='', end='')
        for dio in tekst.dijelovi: dio.render()


r = P('''
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

n = P('''
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

v = P('''
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
