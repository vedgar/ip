from pj import *
import itertools, math, pathlib, webbrowser, time, logging


class T(TipoviTokena):
    OTV, ZATV, REPEAT = '[', ']', 'repeat'
    class FORWARD(Token): literal, predznak = 'forward', +1
    class BACKWARD(Token): literal, predznak = 'backward', -1
    class LEFT(Token): literal, predznak = 'left', +1
    class RIGHT(Token): literal, predznak = 'right', -1
    class PENUP(Token): literal, opkod = 'penup', 'move'
    class PENDOWN(Token): literal, opkod = 'pendown', 'line'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)

alias = {'fd': T.FORWARD, 'fw': T.FORWARD,
         'bk': T.BACKWARD, 'back': T.BACKWARD, 'bw': T.BACKWARD,
         'lt': T.LEFT, 'rt': T.RIGHT, 'pu': T.PENUP, 'pd': T.PENDOWN}

def logo(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            s = lex.sadržaj.casefold()
            if s in alias: yield lex.token(alias[s])
            else: yield lex.literal(T, case=False)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# start -> start naredba | naredba
# naredba -> nar1 BROJ | PENUP | PENDOWN | REPEAT BROJ OTV program ZATV
# nar1 -> FORWARD | BACKWARD | LEFT | RIGHT

### Apstraktna sintaksna stabla
# Program: naredbe:[naredba]
# naredba: Pomak: pikseli:BROJ smjer:FORWARD|BACKWARD
#          Okret: stupnjevi:BROJ smjer:LEFT|RIGHT
#          Ponavljanje: koliko:BROJ naredbe:[naredba]
#          Olovka: položaj:PENUP|PENDOWN

class P(Parser):
    lexer = logo

    def start(self):
        naredbe = [self.naredba()]
        while not self >> KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> {T.FORWARD, T.BACKWARD}:
            return Pomak(self.zadnji, self.pročitaj(T.BROJ))
        elif self >> {T.LEFT, T.RIGHT}:
            return Okret(self.zadnji, self.pročitaj(T.BROJ))
        elif self >> {T.PENUP, T.PENDOWN}: return Olovka(self.zadnji)
        elif self >> T.REPEAT:
            koliko = self.pročitaj(T.BROJ)
            self.pročitaj(T.OTV)
            tijelo = [self.naredba()]
            while not self >> T.ZATV: tijelo.append(self.naredba())
            return Ponavljanje(koliko, tijelo)
        else: raise self.greška()

class Program(AST('naredbe')):
    def js(self):
        repeat_br = itertools.count(1)
        yield from [
            "var canvas = document.getElementById('output');",
            "var ctx = canvas.getContext('2d');",
            'var x = canvas.width / 2, y = canvas.height / 2, h = 0;',
            'var to = ctx.lineTo;',
            'ctx.moveTo(x, y);',
        ]
        for naredba in self.naredbe: yield from naredba.js(repeat_br)
        yield 'ctx.stroke();'

class Pomak(AST('smjer pikseli')):
    def js(self, _):
        t = 'to.apply(ctx, [x-=Math.sin(h)*{d}, y-=Math.cos(h)*{d}]);'
        yield t.format(d=self.smjer.predznak*self.pikseli.vrijednost())

class Okret(AST('smjer stupnjevi')):
    def js(self, _):
        if self.smjer ^ T.LEFT: predznak = +1
        elif self.smjer ^ T.RIGHT: predznak = -1
        φ = math.radians(self.smjer.predznak*self.stupnjevi.vrijednost())
        yield 'h += {kut};'.format(kut=φ)

class Ponavljanje(AST('koliko naredbe')):
    def js(self, repeat_br):
        t = 'for (var r{i} = 0; r{i} < {n}; r{i} ++) {{'
        yield t.format(i=next(repeat_br), n=self.koliko.vrijednost())
        for naredba in self.naredbe: yield from naredba.js(repeat_br)
        yield '}'

class Olovka(AST('položaj')):
    def js(self, _): yield 'to = ctx.{što}To'.format(što=self.položaj.opkod)


def prevedi_string(kôd): return '\n'.join(P(kôd).js())

def prevedi_datoteku(datoteka):
    if isinstance(datoteka, str): datoteka = zb[datoteka]
    pathlib.Path('a.js').write_text(prevedi_string(datoteka.read_text()))

def nacrtaj(ime):
    print('Crtam:', ime)
    prevedi_datoteku(zb[ime])
    webbrowser.open(str(pathlib.Path('loader.html')))

zb = {f.stem: f for f in (pathlib.Path(__file__).parent/'crteži').iterdir()}
crteži = set(zb)
print(crteži)

def nacrtaj_sve():
    for crtež in crteži:
        nacrtaj(crtež)
        time.sleep(8)

nacrtaj('pisanje')
# nacrtaj_sve()

# DZ: pogledati http://www.mathcats.com/gallery/15wordcontest.html
#     i implementirati neke od tih crteža (za mnoge trebaju varijable!)
