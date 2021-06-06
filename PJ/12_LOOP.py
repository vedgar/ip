"""RAM-stroj i LOOP-jezik.

RAM-stroj je virtualni stroj (VM) s prebrojivo mnogo registara R0, R1, R2, ....
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

Npr. LOOP-program "R2{DECR2;} R3{INCR2;DECR3;}" premješta broj iz R3 u R2."""


from vepar import *
from backend import RAMStroj


class T(TipoviTokena):
    TOČKAZ, VOTV, VZATV, INC, DEC = *';{}', 'inc', 'dec'
    class REG(Token):
        def broj(t): return int(t.sadržaj[1:])

@lexer
def loop(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.casefold() in {'i', 'd'}:
            next(lex)  # 'N' ili 'E', case insensitive
            next(lex)  # 'C'        , case insensitive
            yield lex.literal(T, case=False)
        elif znak == 'R':
            lex.prirodni_broj('')
            yield lex.token(T.REG)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# program -> naredba | program naredba
# naredba -> INC REG TOČKAZ | DEC REG TOČKAZ | REG VOTV program VZATV

class P(Parser):
    def program(p) -> 'Program':
        naredbe = [p.naredba()]
        while not p > {KRAJ, T.VZATV}: naredbe.append(p.naredba())
        return Program(naredbe)

    def naredba(p) -> 'Promjena|Petlja':
        if smjer := p >= {T.INC, T.DEC}:
            instrukcija = Promjena(smjer, p >> T.REG)
            p >> T.TOČKAZ
            return instrukcija
        elif reg := p >> T.REG:
            p >> T.VOTV
            tijelo = p.program()
            p >> T.VZATV
            return Petlja(reg, tijelo)


### Apstraktna sintaksna stabla:
# naredba: Petlja: registar:REG tijelo:Program
#          Promjena: op:INC|DEC registar:REG
# Program: naredbe:[naredba]

class Program(AST):
    naredbe: 'naredba*'
    def izvrši(program):
        for naredba in program.naredbe: naredba.izvrši()

class Promjena(AST):
    op: 'INC|DEC'
    registar: 'REG'
    def izvrši(promjena):
        j = promjena.registar.broj()
        if promjena.op ^ T.INC: rt.stroj.inc(j)
        elif promjena.op ^ T.DEC: rt.stroj.dec(j)
        else: assert False, f'Nepoznata operacija {promjena.op}'

class Petlja(AST):
    registar: 'REG'
    tijelo: 'Program'
    def izvrši(petlja):
        n = rt.stroj.registri[petlja.registar.broj()]
        for ponavljanje in range(n): petlja.tijelo.izvrši()


def računaj(program, *ulazi):
    rt.stroj = RAMStroj(*ulazi)
    program.izvrši()
    return rt.stroj.rezultat


with LeksičkaGreška: loop('inc R00')
prikaz(power := P('''
    INC R0;
    R2{
        R0{
            R1 {INC R3;}
            DEC R0;
        }
        R3{DECR3;INCR0;}
    }
'''), 9)
print(baza:=3, '^', eksponent:=7, '=', računaj(power, baza, eksponent))


# DZ: napišite multiply i add (mnogo su jednostavniji od power)
# DZ: Primitivno rekurzivne funkcije predstavljaju funkcijski programski jezik
# ~~  u kojem postoje inicijalne funkcije [nul Z(x)=0, sljedbenik Sc(x)=x+1, te
# rj  koordinatne projekcije Ink(x1,...,xk)=xn za sve prirodne 1 <= n <= k].
# 13  Također postoje operatori kompozicije [f(xs)=h(g1(xs),...,gl(xs))]
#     i primitivne rekurzije [f(xs,0)=g(xs); f(xs,y+1)=h(xs,y,f(xs,y))].
# **  Napišite kompajler jezika primitivno rekurzivnih funkcija u LOOP.
#     (Uputa: prvo položite, ili barem odslušajte, kolegij Izračunljivost!)
