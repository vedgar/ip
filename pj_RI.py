from pj import *
import RI


class Ri(enum.Enum):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = '()|*+?'
    PRAZAN, EPSILON, ZNAK, ESCAPE = '/0', '/1', 'a', '/'

def specijalan(znak):
    assert len(znak) == 1
    return znak in '()|*+?/'

def ri_lex(ri):
    lex = Tokenizer(ri)
    for znak in iter(lex.čitaj, ''):
        if znak == '/':
            lex.token(Ri.ESCAPE)
            sljedeći = lex.čitaj()
            if sljedeći == '0': yield lex.token(Ri.PRAZAN)
            elif sljedeći == '1': yield lex.token(Ri.EPSILON)
            elif not sljedeći: lex.greška('"escape"an kraj stringa')
            elif specijalan(sljedeći): yield lex.token(Ri.ZNAK)
            else: lex.greška('nepostojeći "escape" znak')
        elif specijalan(znak): yield lex.token(operator(Ri, znak))
        else: yield lex.token(Ri.ZNAK)

class RIParser(Parser):
    def izraz(self):
        disjunkt = self.disjunkt()
        if self >> Ri.ILI: return RI.Unija(disjunkt, self.izraz())
        else: return disjunkt

    def disjunkt(self):
        faktor = self.faktor()
        if self >> {Ri.PRAZAN, Ri.EPSILON, Ri.ZNAK, Ri.OTV}:
            self.vrati()
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
        else:
            self.pročitaj(Ri.OTV)
            u_zagradi = self.izraz()
            self.pročitaj(Ri.ZATV)
            return u_zagradi

    start = izraz

if __name__ == '__main__':
    print(*ri_lex('? )a/1|/('), sep=',')
    print(RIParser.parsiraj(ri_lex('/1|a(/(c?)*')))
