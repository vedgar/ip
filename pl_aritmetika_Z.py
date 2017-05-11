from plutil import *


class Ar(enum.Enum):
    POČETAK = None
    BROJ = 1
    PLUS = '+'
    MINUS = '-'
    PUTA = '*'
    OTVORENA = '('
    ZATVORENA = ')'


def ar_lex(izraz):
    lex = Tokenizer(izraz)
    minus_operator = False  # predstavlja li znak '-' operator ili predznak
    yield Token(Ar.POČETAK, '')
    for znak in iter(lex.čitaj, ''):
        if znak.isspace():
            lex.zvijezda(str.isspace)
            lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(Ar.BROJ)
            minus_operator = True
        elif znak in {'+', '*', '(', ')'} or znak == '-' and minus_operator:
            yield lex.token(Ar(znak))
            minus_operator = znak == ')'
        elif znak == '-':  # predznak
            lex.zvijezda(str.isdigit)
            if lex.sadržaj == '-': raise LexError("unarni '-' nije podržan")
            yield lex.token(Ar.BROJ)
            minus_operator = True
        else: lex.greška()


# Beskontekstna gramatika: (parsiramo reverz)
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | faktor
# faktor -> BROJ | OTVORENA izraz ZATVORENA

Binarni = AST('lijevo desno')
class Zbroj(Binarni): pass
class Razlika(Binarni): pass
class Umnožak(Binarni): pass

class ArParser(Parser):
    def izraz(self):
        član = self.član()
        dalje = self.granaj(Ar.POČETAK, Ar.PLUS, Ar.MINUS, Ar.OTVORENA)
        if dalje ** Ar.PLUS:
            self.pročitaj(Ar.PLUS)
            return Zbroj(self.izraz(), član)
        elif dalje ** Ar.MINUS:
            self.pročitaj(Ar.MINUS)
            return Razlika(self.izraz(), član)
        else: return član

    def član(self):
        faktor = self.faktor()
        dalje = self.granaj(Ar.POČETAK, Ar.PUTA, Ar.PLUS, Ar.MINUS, Ar.OTVORENA)
        if dalje ** Ar.PUTA:
            self.pročitaj(Ar.PUTA)
            return Umnožak(self.član(), faktor)
        else: return faktor

    def faktor(self):
        if self.granaj(Ar.BROJ, Ar.ZATVORENA) ** Ar.BROJ:
            return self.pročitaj(Ar.BROJ)
        else:
            self.pročitaj(Ar.ZATVORENA)
            u_zagradi = self.izraz()
            self.pročitaj(Ar.OTVORENA)
            return u_zagradi

def ar_parse(znakovi):
    tokeni = list(ar_lex(znakovi))
    tokeni.reverse()
    parser = ArParser(tokeni)
    rezultat = parser.izraz()
    parser.pročitaj(Ar.POČETAK)
    return rezultat


def ar_interpret(izraz):
    if izraz ** Ar.BROJ: return int(izraz.sadržaj)
    l, d = ar_interpret(izraz.lijevo), ar_interpret(izraz.desno)
    if izraz ** Zbroj: return l + d
    elif izraz ** Razlika: return l - d
    elif izraz ** Umnožak: return l * d


def ar_optimize(izraz):
    nula = Token(Ar.BROJ, '0')
    jedan = Token(Ar.BROJ, '1')
    minusjedan = Token(Ar.BROJ, '-1')
    if izraz ** Ar.BROJ: return izraz
    o_lijevo = ar_optimize(izraz.lijevo)
    o_desno = ar_optimize(izraz.desno)
    if izraz ** Zbroj:
        if o_lijevo == nula: return o_desno
        elif o_desno == nula: return o_lijevo
        return Zbroj(o_lijevo, o_desno)
    elif izraz ** Razlika:
        if o_desno == nula: return o_lijevo
        return Razlika(o_lijevo, o_desno)
    elif izraz ** Umnožak:
        if o_lijevo == jedan: return o_desno
        elif o_desno == jedan: return o_lijevo
        elif nula in {o_lijevo, o_desno}: return nula
        elif o_lijevo == minusjedan: return Razlika(nula, o_desno)
        elif o_desno == minusjedan: return Razlika(nula, o_lijevo)
        return Umnožak(o_lijevo, o_desno)


def testiraj(izraz):
    mi = ar_interpret(ar_optimize(ar_parse(izraz)))
    Python = eval(izraz)
    if mi == Python: print(izraz, '==', mi, 'OK')
    else: print(izraz, 'mi:', mi, 'Python:', Python)

if __name__ == '__main__':
    testiraj('(2+3)*4-1')
    testiraj('6-1-3')
    testiraj('-2+-3--2*(-2+3)-1')
    testiraj('1+1*0+(0+1)*(2+3)')
