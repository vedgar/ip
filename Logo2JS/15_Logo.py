"""Transpiler Logo -> JavaScript, prema kolokviju 24. veljače 2017."""


from vepar import *
import itertools, math, pathlib, webbrowser, time, random


class T(TipoviTokena):
    OTV, ZATV, REPEAT = '[', ']', 'repeat'
    class FORWARD(Token): literal, predznak = 'forward', +1
    class BACKWARD(Token): literal, predznak = 'backward', -1
    class LEFT(Token): literal, predznak = 'left', +1
    class RIGHT(Token): literal, predznak = 'right', -1
    class PENUP(Token): literal, opkod = 'penup', 'move'
    class PENDOWN(Token): literal, opkod = 'pendown', 'line'
    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)

alias = {'fd': T.FORWARD, 'fw': T.FORWARD,
         'bk': T.BACKWARD, 'back': T.BACKWARD, 'bw': T.BACKWARD,
         'lt': T.LEFT, 'rt': T.RIGHT, 'pu': T.PENUP, 'pd': T.PENDOWN}

@lexer
def logo(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * str.isalpha
            try: yield lex.token(alias[lex.sadržaj.casefold()])
            except KeyError: yield lex.literal(T, case=False)
        else: yield lex.literal(T)


### Beskontekstna gramatika
# program -> naredba | program naredba
# naredba -> naredba1 BROJ | PENUP | PENDOWN | REPEAT BROJ OTV program ZATV
# naredba1 -> FORWARD | BACKWARD | LEFT | RIGHT

### Apstraktna sintaksna stabla
# Program: naredbe:[naredba]
# naredba: Pomak: pikseli:BROJ smjer:FORWARD|BACKWARD
#          Okret: stupnjevi:BROJ smjer:LEFT|RIGHT
#          Ponavljanje: koliko:BROJ naredbe:[naredba]
#          Olovka: položaj:PENUP|PENDOWN

class P(Parser):
    def program(p) -> 'Program':
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)

    def naredba(p) -> 'Pomak|Okret|Olovka|Ponavljanje':
        if smjer := p >= {T.FORWARD, T.BACKWARD}:
            return Pomak(smjer, p >> T.BROJ)
        elif smjer := p >= {T.LEFT, T.RIGHT}:
            return Okret(smjer, p >> T.BROJ)
        elif položaj := p >= {T.PENUP, T.PENDOWN}:
            return Olovka(položaj)
        elif p >> T.REPEAT:
            koliko = p >> T.BROJ
            p >> T.OTV
            tijelo = [p.naredba()]
            while not p >= T.ZATV: tijelo.append(p.naredba())
            return Ponavljanje(koliko, tijelo)


class Program(AST):
    naredbe: 'naredba*'
    def js(program):
        rt.repeat = Registri(prefiks='r', start=1)
        yield from [
            "var canvas = document.getElementById('output');",
            "var ctx = canvas.getContext('2d');",
            'var x = canvas.width / 2, y = canvas.height / 2, h = 0;',
            'var to = ctx.lineTo;',
            'ctx.moveTo(x, y);',
        ]
        for naredba in program.naredbe: yield from naredba.js()
        yield 'ctx.stroke();'

class Pomak(AST):
    smjer: 'FORWARD|BACKWARD'
    pikseli: 'BROJ'
    def js(pomak):
        d = pomak.smjer.predznak * pomak.pikseli.vrijednost()
        yield f'to.apply(ctx, [x-=Math.sin(h)*{d}, y-=Math.cos(h)*{d}]);'

class Okret(AST):
    smjer: 'LEFT|RIGHT'
    stupnjevi: 'BROJ'
    def js(okret):
        φ = okret.smjer.predznak * okret.stupnjevi.vrijednost()
        yield f'h += {math.radians(φ)};'

class Ponavljanje(AST):
    koliko: 'BROJ'
    naredbe: 'naredba*'
    def js(petlja):
        r, n = next(rt.repeat), petlja.koliko.vrijednost()
        yield f'for (var {r} = 0; {r} < {n}; {r} ++) '
        yield '{'
        for naredba in petlja.naredbe: yield from naredba.js()
        yield '}'

class Olovka(AST):
    položaj: 'PENUP|PENDOWN'
    def js(olovka): yield f'to = ctx.{olovka.položaj.opkod}To'


direktorij = pathlib.Path(__file__).parent

def prevedi_string(kôd): return '\n'.join(P(kôd).js())

def prevedi_datoteku(datoteka):
    if isinstance(datoteka, str): datoteka = zb[datoteka]
    (direktorij/'a.js').write_text(prevedi_string(datoteka.read_text()))

def nacrtaj(ime):
    print('Crtam:', ime)
    prevedi_datoteku(zb[ime])
    webbrowser.open(str(direktorij/'loader.html'))

# print(pathlib.Path(__file__).parent.parent)
zb = {f.stem: f for f in (direktorij/'crteži').iterdir()}
crteži = sorted(zb)

def nacrtaj_sve():
    for crtež in crteži:
        nacrtaj(crtež)
        time.sleep(4)

if __name__ == '__main__':
    for i, crtež in enumerate(crteži): print(i, crtež)
    utipkano = input('Što da nacrtam? (samo Enter: slučajni odabir, *: sve) ')
    if not utipkano: nacrtaj(random.choice(crteži))
    elif utipkano == '*': nacrtaj_sve()
    elif utipkano.isdecimal(): nacrtaj(crteži[int(utipkano)])
    else: print('Ne razumijem.')


# DZ: dodajte REPCOUNT (pogledajte na webu kako se koristi)
# DZ: pogledati http://www.mathcats.com/gallery/15wordcontest.html
#     i implementirati neke od tih crteža (za mnoge trebaju varijable!)
# DZ: dodati *varijable i **procedure (pogledati 09_ za inspiraciju)
