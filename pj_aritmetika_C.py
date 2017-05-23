from pj import *
import cmath


class AC(enum.Enum):
    BROJ = '1.23e-12'
    I = 'i'
    PLUS, MINUS, PUTA, KROZ, OTV, ZATV = '+-*/()'
    MINUS1 = 'unarni -'
    NA = '**'
    IME = 'neko_ime'
    STRELICA = '->'

def ac_lex(string):
    lex = Tokenizer(string)
    unarni = True  # hoće li sljedeći pročitani '-' biti unarni
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '-':
            if lex.pogledaj() == '>':
                lex.čitaj()
                yield lex.token(AC.STRELICA)
            else: yield lex.token(AC.MINUS1 if unarni else AC.MINUS)
            unarni = True
        elif znak == '*':
            if lex.pogledaj() == '*':
                lex.čitaj()
                yield lex.token(AC.NA)
            else: yield lex.token(AC.PUTA)
            unarni = True
        elif znak == '^':
            yield lex.token(AC.NA)
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
            yield lex.token(AC.BROJ)
            unarni = False
        elif znak.isalpha():
            lex.zvijezda(lambda znak: znak.isalnum() or znak == '_')
            yield lex.token(ključna_riječ(AC, lex.sadržaj) or AC.IME)
            unarni = False
        else:
            yield lex.token(operator(AC, znak) or lex.greška())
            unarni = znak != ')'
        
# Beskontekstna gramatika
# start -> izraz STRELICA IME start | izraz
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS1 faktor 
# baza -> BROJ | IME | I | OTV izraz ZATV

class Program(AST('okolina izraz')): pass
class Binarna(AST('operacija lijevo desno')): pass
class Unarna(AST('operacija od')): pass

class ACParser(Parser):
    def start(self):
        okolina = []
        while True:
            izraz = self.izraz()
            kontekst = self.čitaj()
            if kontekst ** AC.STRELICA:
                okolina.append((self.pročitaj(AC.IME), izraz))
            elif kontekst ** E.KRAJ: return Program(okolina, izraz)

    def izraz(self):
        trenutni = self.član()
        while True:
            op = self.čitaj()
            if op ** {AC.PLUS, AC.MINUS}:
                trenutni = Binarna(op, trenutni, self.član())
            else:
                self.vrati()
                return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            op = self.čitaj()
            if op ** {AC.PUTA, AC.KROZ}:
                trenutni = Binarna(op, trenutni, self.faktor())
            else:
                self.vrati()
                return trenutni

    def faktor(self):
        if self.pogledaj() ** AC.MINUS1:
            return Unarna(self.čitaj(), self.faktor())
        baza = self.baza()
        op = self.čitaj()
        if op ** AC.NA: return Binarna(op, baza, self.faktor())
        else:
            self.vrati()
            return baza

    def baza(self):
        prvi = self.čitaj()
        if prvi ** AC.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(AC.ZATV)
            return u_zagradi
        elif prvi ** {AC.BROJ, AC.IME, AC.I}: return prvi


def ac_interpret(stablo, okolina=None):
    if stablo ** AC.BROJ: return complex(stablo.sadržaj)
    elif stablo ** AC.I: return 1j
    elif stablo ** AC.IME:
        try: return okolina[stablo.sadržaj]
        except KeyError: stablo.problem('Neinicijalizirana varijabla')
    elif stablo ** Unarna:
        assert stablo.operacija ** AC.MINUS1
        return -ac_interpret(stablo.od, okolina)
    elif stablo ** Binarna:
        op = stablo.operacija
        x = ac_interpret(stablo.lijevo, okolina)
        y = ac_interpret(stablo.desno, okolina)
        try:
            if op ** AC.PLUS: return x + y
            elif op ** AC.MINUS: return x - y
            elif op ** AC.PUTA: return x * y
            elif op ** AC.KROZ: return x / y
            elif op ** AC.NA: return x ** y
        except ArithmeticError as ex: op.problem(*ex.args)
    elif stablo ** Program:
        okolina = {}
        for ime, izraz in stablo.okolina:
            okolina[ime.sadržaj] = ac_interpret(izraz, okolina)
        return ac_interpret(stablo.izraz, okolina)
