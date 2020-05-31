from vepar import *
import RI  # kao backend


specijalni = '()|*+?'

class T(TipoviTokena):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = specijalni
    PRAZAN, EPSILON, ZNAK = '/0', '/1', TipTokena()


def ri(lex):
    for znak in lex:
        if znak in specijalni: yield lex.literal(T)
        elif znak == '/':
            lex.zanemari()
            sljedeći = lex.čitaj()
            if not sljedeći: lex.greška('/ na kraju stringa')
            elif sljedeći == '0': yield lex.token(T.PRAZAN)
            elif sljedeći == '1': yield lex.token(T.EPSILON)
            elif sljedeći == '/': yield lex.token(T.ZNAK)  # // kao /
            elif sljedeći in specijalni: yield lex.token(T.ZNAK)
            else: lex.greška('nedefinirana /-sekvenca')
        else: yield lex.token(T.ZNAK)


### Beskontekstna gramatika
# rx -> disjunkt ILI rx | disjunkt
# disjunkt -> faktor disjunkt | faktor
# faktor -> element | faktor ZVIJEZDA | faktor PLUS | faktor UPITNIK
# element -> PRAZAN | EPSILON | ZNAK | OTV rx ZATV

### Umjesto ASTova koristimo klase iz modula RI
# rx: prazan
#     epsilon
#     Elementaran: znak:str (duljine 1)
#     Unija: r1:rx r2:rx
#     Konkatenacija: r1:rx r2:rx
#     Zvijezda: r:rx
#     Plus: r:rx
#     Upitnik: r:rx


class P(Parser):
    def rx(self):
        disjunkt = self.disjunkt()
        if self >= T.ILI: return RI.Unija(disjunkt, self.rx())
        else: return disjunkt

    def disjunkt(self):
        faktor = self.faktor()
        if self > {T.PRAZAN, T.EPSILON, T.ZNAK, T.OTV}:
            return RI.Konkatenacija(faktor, self.disjunkt())
        else: return faktor

    def faktor(self):
        trenutni = self.element()
        while True:
            if self >= T.ZVIJEZDA: trenutni = RI.Zvijezda(trenutni)
            elif self >= T.PLUS: trenutni = RI.Plus(trenutni)
            elif self >= T.UPITNIK: trenutni = RI.Upitnik(trenutni)
            else: return trenutni

    def element(self):
        if self >= T.PRAZAN: return RI.prazan
        elif self >= T.EPSILON: return RI.epsilon
        elif znak := self >= T.ZNAK: return RI.Elementaran(znak.sadržaj)
        elif self >> T.OTV:
            u_zagradi = self.rx()
            self >> T.ZATV
            return u_zagradi

    lexer = ri
    start = rx


ri = '(a(/*c?)+)?'
P.tokeniziraj(ri)
prikaz(P(ri))
print(*P(ri).početak(20))
