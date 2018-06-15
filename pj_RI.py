from pj import *
import RI


class Ri(enum.Enum):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = '()|*+?'
    PRAZAN, EPSILON = '/0', '/1'
    class ZNAK(Token):
        pass


def specijalan(znak):
    assert len(znak) == 1
    return znak in '()|*+?/'


def ri_lex(ri):
    lex = Tokenizer(ri)
    for znak in iter(lex.čitaj, ''):
        if znak == '/':
            lex.token(E.VIŠAK)
            sljedeći = lex.čitaj()
            if sljedeći == '0': yield lex.token(Ri.PRAZAN)
            elif sljedeći == '1': yield lex.token(Ri.EPSILON)
            elif not sljedeći: lex.greška('"escape"an kraj stringa')
            elif specijalan(sljedeći): yield lex.token(Ri.ZNAK)
            else: lex.greška('nepostojeći "escape" znak')
        elif specijalan(znak): yield lex.token(operator(Ri, znak))
        else: yield lex.token(Ri.ZNAK)


### Beskontekstna gramatika
# izraz -> disjunkt ILI izraz | disjunkt
# disjunkt -> faktor disjunkt | faktor
# faktor -> element | faktor ZVIJEZDA | faktor PLUS | faktor UPITNIK
# element -> PRAZAN | EPSILON | ZNAK | OTV izraz ZATV

### Umjesto ASTova koristimo klase iz modula RI
# RI.prazan
# RI.epsilon
# RI.Elementaran(znak)
# RI.Unija(r1, r2)
# RI.Konkatenacija(r1, r2)
# RI.Zvijezda(r)
# RI.Plus(r) i RI.Upitnik(r) su implementirani pomoću gornjih


class RIParser(Parser):
    def izraz(self):
        disjunkt = self.disjunkt()
        if self >> Ri.ILI: return RI.Unija(disjunkt, self.izraz())
        else: return disjunkt

    def disjunkt(self):
        faktor = self.faktor()
        if self >= {Ri.PRAZAN, Ri.EPSILON, Ri.ZNAK, Ri.OTV}:
            return RI.Konkatenacija(faktor, self.disjunkt())
        else: return faktor

    def faktor(self):
        trenutni = self.element()
        while True:
            if self >> Ri.ZVIJEZDA: trenutni = RI.Zvijezda(trenutni)
            elif self >> Ri.PLUS: trenutni = RI.Plus(trenutni)
            elif self >> Ri.UPITNIK: trenutni = RI.Upitnik(trenutni)
            else: return trenutni

    def element(self):
        if self >> Ri.PRAZAN: return RI.prazan
        elif self >> Ri.EPSILON: return RI.epsilon
        elif self >> Ri.ZNAK: return RI.Elementaran(self.zadnji.sadržaj)
        elif self >> Ri.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(Ri.ZATV)
            return u_zagradi
        else: self.greška()

    start = izraz

if __name__ == '__main__':
    # print(*ri_lex('? )a/1|/('), sep=',')
    print(RIParser.parsiraj(ri_lex('/1|a(/(c?)*')).početak())
    # print(repr(RIParser.parsiraj(ri_lex('/1|a|bc*'))))
