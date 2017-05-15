from pj import *
import cmath


class Ar(enum.Enum):
    BROJ = '1.23e-12'
    I = 'i'
    PLUS, MINUS, PUTA, KROZ, OTV, ZATV = '+-*/()'
    MINUS1 = 'unarni -'
    NA = '**'
    IME = 'neko_ime'
    STRELICA = '->'

def ar_lex(string):
    lex = Tokenizer(string)
    unarni = True  # hoće li sljedeći pročitani '-' biti unarni
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '-':
            if lex.pogledaj() == '>':
                lex.čitaj()
                yield lex.token(Ar.STRELICA)
            else: yield lex.token(Ar.MINUS1 if unarni else Ar.MINUS)
            unarni = True
        elif znak == '*':
            if lex.pogledaj() == '*':
                lex.čitaj()
                yield lex.token(Ar.NA)
            else: yield lex.token(Ar.PUTA)
            unarni = True
        elif znak == '^':
            yield lex.token(Ar.NA)
            unarni = True
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            if lex.pogledaj() == '.':
                lex.čitaj()
                lex.zvijezda(str.isdigit)
            if lex.pogledaj() == 'e':
                lex.čitaj()
                if lex.pogledaj() == '-': lex.čitaj()
                if lex.pogledaj().isdigit(): lex.zvijezda(str.isdigit)
                else: lex.greška('očekivana znamenka')
            yield lex.token(Ar.BROJ)
            unarni = False
        elif znak.isalpha():
            lex.zvijezda(lambda znak: znak.isalnum() or znak == '_')
            yield lex.token(ključna_riječ(Ar, lex.sadržaj) or Ar.IME)
            unarni = False
        else:
            yield lex.token(operator(Ar, znak) or lex.greška())
            unarni = znak != ')'
        
# Beskontekstna gramatika
# program -> izraz STRELICA IME program | izraz
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS1 faktor 
# baza -> BROJ | IME | I | OTV izraz ZATV

class Program(AST('okolina izraz')): pass
class Binarna(AST('operacija lijevo desno')): pass
class Unarna(AST('operacija od')): pass

class ArParser(Parser):
    def program(self):
        okolina = []
        while True:
            izraz = self.izraz()
            kontekst = self.čitaj()
            if kontekst ** Ar.STRELICA:
                okolina.append((self.pročitaj(Ar.IME), izraz))
            elif kontekst ** E.KRAJ: return Program(okolina, izraz)

    def izraz(self):
        trenutni = self.član()
        while True:
            op = self.čitaj()
            if op ** {Ar.PLUS, Ar.MINUS}:
                trenutni = Binarna(op, trenutni, self.član())
            else:
                self.vrati()
                return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            op = self.čitaj()
            if op ** {Ar.PUTA, Ar.KROZ}:
                trenutni = Binarna(op, trenutni, self.faktor())
            else:
                self.vrati()
                return trenutni

    def faktor(self):
        if self.pogledaj() ** Ar.MINUS1:
            return Unarna(self.čitaj(), self.faktor())
        baza = self.baza()
        op = self.čitaj()
        if op ** Ar.NA: return Binarna(op, baza, self.faktor())
        else:
            self.vrati()
            return baza

    def baza(self):
        prvi = self.čitaj()
        if prvi ** Ar.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(Ar.ZATV)
            return u_zagradi
        elif prvi ** {Ar.BROJ, Ar.IME, Ar.I}: return prvi

def ar_parse(string):
    parser = ArParser(ar_lex(string))
    rezultat = parser.program()
    parser.pročitaj(E.KRAJ)
    return rezultat


def ar_interpret(stablo, okolina=None):
    if stablo ** Ar.BROJ: return complex(stablo.sadržaj)
    elif stablo ** Ar.I: return 1j
    elif stablo ** Ar.IME:
        try: return okolina[stablo.sadržaj]
        except KeyError: stablo.problem('Neinicijalizirana varijabla')
    elif stablo ** Unarna:
        assert stablo.operacija ** Ar.MINUS1
        return -ar_interpret(stablo.od, okolina)
    elif stablo ** Binarna:
        op = stablo.operacija
        x = ar_interpret(stablo.lijevo, okolina)
        y = ar_interpret(stablo.desno, okolina)
        try:
            if op ** Ar.PLUS: return x + y
            elif op ** Ar.MINUS: return x - y
            elif op ** Ar.PUTA: return x * y
            elif op ** Ar.KROZ: return x / y
            elif op ** Ar.NA: return x ** y
        except ArithmeticError as ex: op.problem(*ex.args)
    elif stablo ** Program:
        okolina = {}
        for ime, izraz in stablo.okolina:
            okolina[ime.sadržaj] = ar_interpret(izraz, okolina)
        return ar_interpret(stablo.izraz, okolina)
