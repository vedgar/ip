"""Regularni izrazi kao beskontekstni jezik. (Po kolokviju 10. veljače 2017.)

Izgrađeni su od osnovnih (inicijalnih) regularnih izraza:
    /0  prazan jezik
    /1  jezik koji se sastoji samo od prazne riječi
    x   jezik koji se sastoji od jednoslovne riječi x
        - specijalni znakovi zahtijevaju escaping pomoću /
pomoću operatora:
    |       (infiksni) unija
            (ne piše se) konkatenacija
    *,+,?   (postfiksni) Kleenejevi operatori"""


from vepar import *
import RI  # kao backend


specijalni = '()|*+?'

class T(TipoviTokena):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = specijalni
    PRAZAN, EPSILON = '/0', '/1'
    class ZNAK(Token): pass

@lexer
def ri(lex):
    for znak in lex:
        if znak in specijalni: yield lex.literal(T)
        elif znak == '/':
            sljedeći = next(lex)
            if not sljedeći: raise lex.greška('/ na kraju stringa')
            elif sljedeći in {'/', *specijalni}: yield lex.token(T.ZNAK)
            elif sljedeći in {'0', '1'}: yield lex.literal(T)
            else: raise lex.greška('nedefinirana /-sekvenca')
        else: yield lex.token(T.ZNAK)


### Beskontekstna gramatika
# rx -> disjunkt | disjunkt ILI rx
# disjunkt -> faktor | faktor disjunkt
# faktor -> element | faktor ZVIJEZDA | faktor PLUS | faktor UPITNIK
# element -> PRAZAN | EPSILON | ZNAK | OTV rx ZATV

class P(Parser):
    def rx(self) -> 'disjunkt|Unija':
        disjunkt = self.disjunkt()
        if self >= T.ILI: return RI.Unija(disjunkt, self.rx())
        else: return disjunkt

    def disjunkt(self) -> 'faktor|Konkatenacija':
        faktor = self.faktor()
        if self > {T.PRAZAN, T.EPSILON, T.ZNAK, T.OTV}:
            return RI.Konkatenacija(faktor, self.disjunkt())
        else: return faktor

    def faktor(self) -> 'element|Zvijezda|Plus|Upitnik':
        trenutni = self.element()
        while ...:
            if self >= T.ZVIJEZDA: trenutni = RI.Zvijezda(trenutni)
            elif self >= T.PLUS: trenutni = RI.Plus(trenutni)
            elif self >= T.UPITNIK: trenutni = RI.Upitnik(trenutni)
            else: return trenutni

    def element(self) -> 'Prazan|Epsilon|Elementarni|rx':
        if self >= T.PRAZAN: return RI.prazan
        elif self >= T.EPSILON: return RI.epsilon
        elif znak := self >= T.ZNAK:
            t = znak.sadržaj
            if t.startswith('/'): kosa_crta, t = t
            return RI.Elementarni(t)
        elif self >> T.OTV:
            u_zagradi = self.rx()
            self >> T.ZATV
            return u_zagradi


### Kao ASTove koristimo klase iz modula RI
# rx: prazan
#     epsilon
#     Elementarni: znak:str (duljine 1)
#     Unija: r1:rx r2:rx
#     Konkatenacija: r1:rx r2:rx
#     Zvijezda: r:rx
#     Plus: r:rx
#     Upitnik: r:rx

ri(r := '(a(/*c?)+)?')
prikaz(P(r))
print(*P(r).početak(20))
