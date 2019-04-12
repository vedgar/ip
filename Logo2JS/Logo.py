from pj import *
import itertools, math, pathlib, webbrowser, time, logging


class LOGO(enum.Enum):
    OTVORENA, ZATVORENA = '[]'
    REPEAT, FORWARD, LEFT, RIGHT = 'repeat', 'forward', 'left', 'right'
    PENUP, PENDOWN = 'penup', 'pendown'
    BACKWARD = 'backward'

    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)

alias = {'fd': 'forward', 'lt': 'left', 'rt': 'right', 'pu': 'penup',
    'pd': 'pendown', 'bk': 'backward', 'back': 'backward', 'bw': 'backward'}

def logo_lex(kod):
    lex = Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(LOGO.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            s = lex.sadržaj.casefold()
            if s in alias: s = alias[s]
            yield lex.token(LOGO(s))
        else: yield lex.literal(LOGO)


### Beskontekstna gramatika
# program -> naredba program | naredba
# naredba -> FD BROJ | LT BROJ | RT BROJ | BW BROJ | PU | PD | petlja
# petlja -> REPEAT BROJ OTVORENA program ZATVORENA

### Apstraktna sintaksna stabla
# Program: naredbe:list - LOGO program
# Pomak: pikseli:LOGO.BROJ, smjer:+-1 - FORWARD ili BACKWARD naredba
# Okret: stupnjevi:LOGO.BROJ, smjer:+-1 - LEFT ili RIGHT naredba
# Ponavljanje: koliko:LOGO.BROJ, naredbe:list - REPEAT naredba
# Olovka: down:bool - PU ili PD naredba

def naredbe(parser):
    for kw in iter(parser.čitaj, None):
        if kw ** {LOGO.FORWARD,LOGO.BACKWARD,LOGO.LEFT,LOGO.RIGHT,LOGO.REPEAT}:
            koliko = parser.pročitaj(LOGO.BROJ)
        if kw ** LOGO.PENUP: yield Olovka(False)
        elif kw ** LOGO.PENDOWN: yield Olovka(True)
        elif kw ** LOGO.FORWARD: yield Pomak(koliko, +1)
        elif kw ** LOGO.LEFT: yield Okret(koliko, +1)
        elif kw ** LOGO.BACKWARD: yield Pomak(koliko, -1)
        elif kw ** LOGO.RIGHT: yield Okret(koliko, -1)
        elif kw ** LOGO.REPEAT:
            parser.pročitaj(LOGO.OTVORENA)
            u_petlji = list(naredbe(parser))
            parser.pročitaj(LOGO.ZATVORENA)
            yield Ponavljanje(koliko, u_petlji)
        else:
            parser.vrati()
            return


def prevedi(naredbe):
    repeat_br = itertools.count(1)
    yield from [
        "var canvas = document.getElementById('output');",
        "var ctx = canvas.getContext('2d');",
        'var x = canvas.width / 2, y = canvas.height / 2, h = 0;',
        'var to = ctx.lineTo;',
        'ctx.moveTo(x, y);',
    ]
    for naredba in naredbe: yield from naredba.js(repeat_br)
    yield 'ctx.stroke();'


class Pomak(AST('pikseli smjer')):
    def js(self, _):
        yield 'to.apply(ctx, [x-=Math.sin(h)*{0}, y-=Math.cos(h)*{0}]);'\
              .format(self.pikseli.vrijednost() * self.smjer)

class Okret(AST('stupnjevi smjer')):
    def js(self, _):
        zaokret = math.radians(self.stupnjevi.vrijednost() * self.smjer)
        yield 'h += {};'.format(zaokret)

class Ponavljanje(AST('koliko naredbe')):
    def js(self, repeat_br):
        petlja = 'for (var r{i} = 0; r{i} < {n}; r{i} ++)'
        yield petlja.format(i=next(repeat_br), n=self.koliko.vrijednost())
        yield '{'
        for naredba in self.naredbe: yield from naredba.js(repeat_br)
        yield '}'

class Olovka(AST('crtaj')):
    def js(self, _):
        yield 'to = ctx.{}To;'.format('line' if self.crtaj else 'move')


def prevedi_string(kôd):
    p = Parser(logo_lex(kôd))
    prevedeno = '\n'.join(prevedi(naredbe(p)))
    p.pročitaj(E.KRAJ)
    return prevedeno

def prevedi_datoteku(datoteka):
    if isinstance(datoteka, str): datoteka = dat[datoteka]
    p = Parser(logo_lex(itertools.chain.from_iterable(datoteka.open())))
    with pathlib.Path('a.js').open('w') as izlaz:
        for javascript in prevedi(naredbe(p)): print(javascript, file=izlaz)
    p.pročitaj(E.KRAJ)

def logirano_prevedi_datoteku(datoteka):
    if isinstance(datoteka, str): datoteka = dat[datoteka]
    def logiran(niz, tag=None):
        logging.getLogger().setLevel(logging.DEBUG)
        if tag is None: tag = niz.__name__
        for element in niz:
            logging.debug('%s %r', tag, element)
            yield element
    f = logiran(datoteka.open(), 'datoteka')
    c = logiran(itertools.chain.from_iterable(f), 'linija')
    l = logiran(logo_lex(c), 'tokenizer')
    n = logiran(naredbe(Parser(l)), 'parser')
    j = logiran(prevedi(n), 'kompajler')
    print('\n'.join(j))

def nacrtaj(ime):
    prevedi_datoteku(dat[ime])
    webbrowser.open(str(pathlib.Path('loader.html')))

dat = {f.stem: f for f in (pathlib.Path(__file__).parent/'crteži').iterdir()}
crteži = set(dat)

def nacrtaj_sve():
    for crtež in crteži:
        nacrtaj(crtež)
        time.sleep(8)
