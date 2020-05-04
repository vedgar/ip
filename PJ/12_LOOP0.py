"""RAM-stroj i LOOP-jezik.

RAM-stroj je virtualna mašina s prebrojivo mnogo registara R0, R1, R2, ....
U svakom registru može se nalaziti proizvoljni prirodni broj (uključujući 0).
Na početku rada RAM-stroja (reset) su svi registri inicijalizirani na 0.

RAM-stroj se može koristiti za izračunavanje brojevnih funkcija
(kao što se Turingov stroj može koristiti za izračunavanje jezičnih funkcija).
U tu svrhu, k ulaznih podataka se zapiše u registre R1--Rk (ostali su 0)
na početku rada, a na kraju rada se izlazni podatak pročita iz registra R0.

LOOP je strojni jezik (machine code) za RAM-stroj.
LOOP-program je slijed (jedne ili više) instrukcija sljedećeg oblika:
  * INC Rj; (inkrement), čije izvršavanje povećava broj u Rj za 1
  * DEC Rj; (dekrement), čije izvršavanje smanjuje broj u Rj za 1,
        osim ako je taj broj 0 (tada ne radi ništa).
  * Rj{program} (ograničena petlja), čije izvršavanje izvršava program onoliko
        puta koliki je broj bio u registru Rj na početku izvršavanja petlje
        (program može mijenjati Rj, ali to ne mijenja broj izvršavanja petlje).

Npr. LOOP-program "R2{DECR2;} R3{INCR2;DECR3;}" premješta broj iz R3 u R2.
"""

from pj import *
from backend import RAMStroj


class LOOP(enum.Enum):
    INC, DEC = 'INC', 'DEC'
    TOČKAZ, VOTV, VZATV = ';{}'
    
    class REG(Token):
        def broj(self): return int(self.sadržaj[1:])


def loop_lex(prog):
    lex = Tokenizer(prog)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak in 'ID':
            lex.čitaj()  # 'N' ili 'E'
            lex.čitaj()  # 'C'
            yield lex.literal(LOOP)
        elif znak == 'R':
            lex.plus(str.isdigit)
            yield lex.token(LOOP.REG)
        else: yield lex.literal(LOOP)


### Beskontekstna gramatika:
# program -> naredba | naredba program
# naredba -> (INC | DEC) REG TOČKAZ | REG VOTV program VZATV

### Apstraktna sintaksna stabla:
# Petlja: registar:REG, tijelo:Program
# Inkrement: registar:REG
# Dekrement: registar:REG
# Program: naredbe:[Petlja|Inkrement|Dekrement]


class LOOPParser(Parser):
    def program(self):
        naredbe = [self.naredba()]
        while not self >= {E.KRAJ, LOOP.VZATV}: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> {LOOP.INC, LOOP.DEC}:
            opkod = Inkrement if self.zadnji ^ LOOP.INC else Dekrement
            reg = self.pročitaj(LOOP.REG)
            self.pročitaj(LOOP.TOČKAZ)
            return opkod(reg)
        else:
            reg = self.pročitaj(LOOP.REG)
            self.pročitaj(LOOP.VOTV)
            tijelo = self.program()
            self.pročitaj(LOOP.VZATV)
            return Petlja(reg, tijelo)

    start = program


class Program(AST('naredbe')):
    def izvrši(self, stroj):
        for naredba in self.naredbe: naredba.izvrši(stroj)

class Inkrement(AST('registar')):
    def izvrši(self, stroj): stroj.inc(self.registar.broj())

class Dekrement(AST('registar')):
    def izvrši(self, stroj): stroj.dec(self.registar.broj())
        
class Petlja(AST('registar tijelo')):
    def izvrši(self, stroj):
        for ponavljanje in range(stroj.registri[self.registar.broj()]):
            self.tijelo.izvrši(stroj)


def računaj(program, *ulazi):
    stroj = RAMStroj(*ulazi)
    program.izvrši(stroj)
    return stroj.rezultat


if __name__ == '__main__':
    power = LOOPParser.parsiraj(loop_lex('''\
        INC R0;
        R2{
            R0{
                R1 {INC R3;}
                DEC R0;
            }
            R3{DECR3;INCR0;}
        }
    '''))
    prikaz(power, 9)
    baza, eksponent = 3, 7
    print(baza, '^', eksponent, '=', računaj(power, baza, eksponent))

# DZ: napišite multiply i add (puno su jednostavniji od power)
# DZ: Primitivno rekurzivne funkcije predstavljaju funkcijski programski jezik
# **  u kojem postoje inicijalne funkcije [nul Z(x)=0, sljedbenik Sc(x)=x+1, te
#     koordinatne projekcije Ink(x1,...,xk)=xn za sve prirodne 1 <= n <= k].
#     Također postoji operator kompozicije [f(xs)=h(g1(xs),...,gl(xs))]
#     i primitivne rekurzije [f(xs,0)=g(xs); f(xs,y+1)=h(xs,y,f(xs,y))].
#     Napišite kompajler jezika primitivno rekurzivnih funkcija u LOOP.
#     (Uputa: prvo položite, ili barem odslušajte, Izračunljivost!;)
