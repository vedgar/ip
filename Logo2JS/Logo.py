from pj import *
import itertools, math, pathlib, webbrowser, time


class Logo(enum.Enum):
    OTVORENA = '['
    ZATVORENA = ']'
    BROJ = 153
    REPEAT = 'REPEAT'
    FORWARD = FD = 'FORWARD'
    LEFT = LT = 'LEFT'
    PU = PENUP = 'PU'
    PD = PENDOWN = 'PD'
    BACKWARD = BACK = BK = BW = 'BACKWARD'
    RIGHT = RT = 'RIGHT'
    

def logo_lex(kod):
    lex = Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(Logo.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            kw = ključna_riječ(Logo, lex.sadržaj, False)
            yield lex.token(kw or E.GREŠKA)
        else: yield lex.token(operator(Logo, znak) or lex.greška())


### Beskontekstna gramatika
# program -> naredba program | naredba
# naredba -> FORWARD BROJ | LEFT BROJ | PU | PD | petlja
# petlja -> REPEAT BROJ OTVORENA program ZATVORENA

### Apstraktna sintaksna stabla
# Program: naredbe:tuple - Logo program
# Forward: pikseli:Logo.BROJ, smjer:+-1 - FORWARD ili BACKWARD naredba
# Left: stupnjevi:Logo.BROJ, smjer:+-1 - LEFT ili RIGHT naredba
# Repeat: koliko:Logo.BROJ, naredbe:tuple - REPEAT naredba
# Pen: down:bool - PU ili PD naredba

def naredbe(parser):
    for kw in iter(parser.čitaj, None):
        if kw ** {Logo.FORWARD,Logo.BACKWARD,Logo.LEFT,Logo.RIGHT,Logo.REPEAT}:
            koliko = parser.pročitaj(Logo.BROJ)
        if kw ** Logo.PU: yield Pen(False)
        elif kw ** Logo.PD: yield Pen(True)
        elif kw ** Logo.FORWARD: yield Forward(koliko, +1)
        elif kw ** Logo.LEFT: yield Left(koliko, +1)
        elif kw ** Logo.BACKWARD: yield Forward(koliko, -1)
        elif kw ** Logo.RIGHT: yield Left(koliko, -1)
        elif kw ** Logo.REPEAT:
            parser.pročitaj(Logo.OTVORENA)
            u_petlji = list(naredbe(parser))
            parser.pročitaj(Logo.ZATVORENA)
            yield Repeat(koliko, u_petlji)
        else:
            parser.vrati()
            return


def prevedi(naredbe):
    repeat_br = itertools.count(1)
    yield from [
        "var canvas = document.getElementById('output');",
        "var ctx = canvas.getContext('2d');",
        'var x = canvas.width / 2;',
        'var y = canvas.height / 2;',
        'var h = 0;',
        'var to = ctx.lineTo;',
        'ctx.moveTo(x, y);',
    ]
    for naredba in naredbe: yield from naredba.js(repeat_br)
    yield 'ctx.stroke();'

class Forward(AST('pikseli smjer')):
    """FORWARD (ili FD) naredba."""
    def js(self, _):
        yield 'to.apply(ctx, [x-=Math.sin(h)*{0}, y-=Math.cos(h)*{0}]);'\
              .format(int(self.pikseli.sadržaj) * self.smjer)

class Left(AST('stupnjevi smjer')):
    """LEFT (ili LT) naredba."""
    def js(self, _):
        zaokret = math.radians(int(self.stupnjevi.sadržaj) * self.smjer)
        yield 'h += {};'.format(zaokret)

class Repeat(AST('koliko naredbe')):
    """REPEAT naredba."""
    def js(self, repeat_br):
        for_petlja = 'for (var r{i} = 0; r{i} < {n}; r{i} ++)'
        yield for_petlja.format(i=next(repeat_br), n=int(self.koliko.sadržaj))
        yield '{'
        for naredba in self.naredbe: yield from naredba.js(repeat_br)
        yield '}'

class Pen(AST('down')):
    """PU ili PD naredba."""
    def js(self, _):
        if self.down: yield 'to = ctx.lineTo;'
        else: yield 'to = ctx.moveTo;'


def prevedi_string(kôd):
    p = Parser(logo_lex(kôd))
    prevedeno = '\n'.join(prevedi(naredbe(p)))
    p.pročitaj(E.KRAJ)
    return prevedeno

def prevedi_datoteku(datoteka):
    p = Parser(logo_lex(itertools.chain.from_iterable(open(datoteka))))
    with open(pathlib.Path('a.js'), 'w') as izlaz:
        for javascript in prevedi(naredbe(p)): print(javascript, file=izlaz)
    p.pročitaj(E.KRAJ)

def nacrtaj(ime):
    prevedi_datoteku(pathlib.Path('crteži/{}.logo'.format(ime)))
    webbrowser.open(pathlib.Path('loader.html'))

if __name__ == '__main__':
    for crtež in (pathlib.Path(__file__).parent / 'crteži').iterdir():
        prevedi_datoteku(crtež)
        webbrowser.open_new_tab(pathlib.Path('loader.html'))
        time.sleep(2)
