from pj import *
import RI


specijalni = '()|*+?'

class RX(enum.Enum):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = specijalni
    PRAZAN, EPSILON = '/0', '/1'
    class ZNAK(Token): pass


def ri_lex(ri):
    lex = Tokenizer(ri)
    for znak in iter(lex.čitaj, ''):
        if znak in specijalni: yield lex.literal(RX)
        elif znak == '/':
            lex.zanemari()
            sljedeći = lex.čitaj()
            if not sljedeći: lex.greška('"escape"an kraj stringa')
            elif sljedeći == '0': yield lex.token(RX.PRAZAN)
            elif sljedeći == '1': yield lex.token(RX.EPSILON)
            elif sljedeći == '/': yield lex.token(RX.ZNAK)  # // kao /
            elif sljedeći in specijalni: yield lex.token(RX.ZNAK)
            else: lex.greška('nepostojeći "escape" znak')
        else: yield lex.token(RX.ZNAK)


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
        if self >> RX.ILI: return RI.Unija(disjunkt, self.izraz())
        else: return disjunkt

    def disjunkt(self):
        faktor = self.faktor()
        if self >= {RX.PRAZAN, RX.EPSILON, RX.ZNAK, RX.OTV}:
            return RI.Konkatenacija(faktor, self.disjunkt())
        else: return faktor

    def faktor(self):
        trenutni = self.element()
        while True:
            if self >> RX.ZVIJEZDA: trenutni = RI.Zvijezda(trenutni)
            elif self >> RX.PLUS: trenutni = RI.Plus(trenutni)
            elif self >> RX.UPITNIK: trenutni = RI.Upitnik(trenutni)
            else: return trenutni

    def element(self):
        if self >> RX.PRAZAN: return RI.prazan
        elif self >> RX.EPSILON: return RI.epsilon
        elif self >> RX.ZNAK: return RI.Elementaran(self.zadnji.sadržaj)
        elif self >> RX.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(RX.ZATV)
            return u_zagradi
        else: self.greška()

    start = izraz


if __name__ == '__main__':
    print(*ri_lex('? )a/1|/('), sep=', ')
    print(RIParser.parsiraj(ri_lex('/1|a(/(c?)*')).početak())
    prikaz(RIParser.parsiraj(ri_lex('/1|a|bc*')), 7)
