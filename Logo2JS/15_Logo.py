from vepar import *
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
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if smjer := self >= {T.FORWARD, T.BACKWARD}:
            return Pomak(smjer, self >> T.BROJ)
        elif smjer := self >= {T.LEFT, T.RIGHT}:
            return Okret(smjer, self >> T.BROJ)
        elif položaj := self >= {T.PENUP, T.PENDOWN}:
            return Olovka(položaj)
        elif self >> T.REPEAT:
            koliko = self >> T.BROJ
            self >> T.OTV
            tijelo = [self.naredba()]
            while not self >= T.ZATV: tijelo.append(self.naredba())
            return Ponavljanje(koliko, tijelo)


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
    def js(self, repeat_br):
        d = self.smjer.predznak * self.pikseli.vrijednost()
        yield f'to.apply(ctx, [x-=Math.sin(h)*{d}, y-=Math.cos(h)*{d}]);'

class Okret(AST('smjer stupnjevi')):
    def js(self, repeat_br):
        φ = self.smjer.predznak * self.stupnjevi.vrijednost()
        yield f'h += {math.radians(φ)};'

class Ponavljanje(AST('koliko naredbe')):
    def js(self, repeat_br):
        i, n = next(repeat_br), self.koliko.vrijednost()
        yield f'for (var r{i} = 0; r{i} < {n}; r{i} ++) ' + '{'
        for naredba in self.naredbe: yield from naredba.js(repeat_br)
        yield '}'

class Olovka(AST('položaj')):
    def js(self, repeat_br): yield f'to = ctx.{self.položaj.opkod}To'


def prevedi_string(kôd): return '\n'.join(P(kôd).js())

def prevedi_datoteku(datoteka):
    if isinstance(datoteka, str): datoteka = zb[datoteka]
    (pathlib.Path(__file__).parent.parent/'Logo2JS'/'a.js').write_text(prevedi_string(datoteka.read_text()))

def nacrtaj(ime):
    print('Crtam:', ime)
    prevedi_datoteku(zb[ime])
    webbrowser.open(str(pathlib.Path(__file__).parent.parent/'Logo2JS'/'loader.html'))

print(pathlib.Path(__file__).parent.parent)
zb = {f.stem: f for f in (pathlib.Path(__file__).parent.parent/'Logo2JS'/'crteži').iterdir()}
crteži = set(zb)
print(crteži)

def nacrtaj_sve():
    for crtež in crteži:
        nacrtaj(crtež)
        time.sleep(4)

# nacrtaj('pisanje')
nacrtaj_sve()

# DZ: dodajte REPCOUNT (pogledajte na webu kako se koristi)
# DZ: pogledati http://www.mathcats.com/gallery/15wordcontest.html
#     i implementirati neke od tih crteža (za mnoge trebaju varijable!)
