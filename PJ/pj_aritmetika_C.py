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
            lex.zvijezda(identifikator)
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
            if self >> AC.STRELICA:
                okolina.append((self.pročitaj(AC.IME), izraz))
            elif self >> E.KRAJ: return Program(okolina, izraz)

    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> {AC.PLUS, AC.MINUS}:
                trenutni = Binarna(self.zadnji, trenutni, self.član())
            else: return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> {AC.PUTA, AC.KROZ}:
                trenutni = Binarna(self.zadnji, trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AC.MINUS1: return Unarna(self.zadnji, self.faktor())
        baza = self.baza()
        if self >> AC.NA: return Binarna(self.zadnji, baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> AC.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(AC.ZATV)
            return u_zagradi
        elif self >> {AC.BROJ, AC.IME, AC.I}: return self.zadnji
        else: self.greška()


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

def izračunaj(string): return ac_interpret(ACParser.parsiraj(ac_lex(string)))

if __name__ == '__main__':
    from math import pi
    print(izračunaj('2+2*3'))
    print(izračunaj('(1+6*i)/(-4-3*i)^2'))
    print(izračunaj('i^i'))
    print(izračunaj('''\
        i+1 -> t
        t/2^2^-1 -> a
        a^2^2^2^2^0 -> b
        b
    '''))
    print(abs(izračunaj('''\
        8 -> d
        10^d -> n
        (1+1/n)^n -> e
        {} -> pi
        e^(i*pi) + 1 -> skoro0
        skoro0
    '''.format(pi))))
