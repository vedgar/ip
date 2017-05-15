from pj import *
import RI


class Ri(enum.Enum):
    PRAZAN = '/0'
    EPSILON = '/1'
    ZNAK, OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = 'a()|*+?'
    ESCAPE = '/'

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
        if self.čitaj() ** Ri.ILI: return RI.Unija(disjunkt, self.izraz())
        self.vrati()
        return disjunkt

    def disjunkt(self):
        faktor = self.faktor()
        sljedeći = self.pogledaj()
        if sljedeći ** {Ri.PRAZAN, Ri.EPSILON, Ri.ZNAK, Ri.OTV}:
            return RI.Konkatenacija(faktor, self.disjunkt())
        return faktor

    def faktor(self):
        trenutni = self.element()
        while True:
            postfix = self.čitaj()
            if postfix ** Ri.ZVIJEZDA: trenutni = RI.Zvijezda(trenutni)
            elif postfix ** Ri.PLUS: trenutni = RI.Plus(trenutni)
            elif postfix ** Ri.UPITNIK: trenutni = RI.Upitnik(trenutni)
            else:
                self.vrati()
                return trenutni

    def element(self):
        prvi = self.čitaj()
        if prvi ** Ri.OTV:
            osnovni = self.izraz()
            self.pročitaj(Ri.ZATV)
            return osnovni
        elif prvi ** Ri.PRAZAN: return RI.prazan
        elif prvi ** Ri.EPSILON: return RI.epsilon
        elif prvi ** Ri.ZNAK: return RI.Elementaran(prvi.sadržaj)

def ri_parse(regex):
    parser = RIParser(ri_lex(regex))
    rezultat = parser.izraz()
    parser.pročitaj(E.KRAJ)
    return rezultat

if __name__ == '__main__':
    print(*ri_lex('? )a/1|/('), sep=',')
    print(repr(ri_parse('/1|a(/(c?)*')))
