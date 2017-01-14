from tip import Parser, Token, AST, Tokenizer, vrsta
import enum


class Ar(enum.Enum):
    PRAZNO, KRAJ, GREŠKA = 0, 1, 2
    BROJ = 3
    PLUS = '+'
    MINUS = '-'
    PUTA = '*'
    OTVORENA = '('
    ZATVORENA = ')'


def aritm_lex(izraz):
    lex = Tokenizer(izraz)
    minus_operator = False
    while True:
        znak = lex.pogledaj()
        vr = vrsta(znak)
        if vr == 'kraj':
            yield Token(Ar.KRAJ, '')
            return
        elif vr == 'praznina':
            Token(Ar.PRAZNO, lex.praznine())  # ne yieldamo, zanemarujemo
        elif vr == 'znamenka':
            yield Token(Ar.BROJ, lex.broj())
            minus_operator = True
        elif znak in '+*(':
            yield Token(Ar(znak), lex.čitaj())
            minus_operator = False
        elif znak == '-':
            if minus_operator:
                yield Token(Ar.MINUS, lex.čitaj())
                minus_operator = False
            else:
                yield Token(Ar.BROJ, lex.čitaj() + lex.broj())
                minus_operator = True
        elif znak == ')':
            yield Token(Ar.ZATVORENA, lex.čitaj())
            minus_operator = True
        else:
            yield Token(Ar.GREŠKA, lex.čitaj())


class AritmParser(Parser):
    def izraz(self):
        č1 = self.član()
        dalje = self.granaj(Ar.KRAJ, Ar.PLUS, Ar.MINUS, Ar.ZATVORENA)
        if dalje == Ar.PLUS:
            self.pročitaj(Ar.PLUS)
            č2 = self.izraz()
            return AST(stablo='zbroj', lijevo=č2, desno=č1)
        elif dalje == Ar.MINUS:
            self.pročitaj(Ar.MINUS)
            č2 = self.izraz()
            return AST(stablo='razlika', lijevo=č2, desno=č1)
        else:
            return č1

    def član(self):
        f1 = self.faktor()
        dalje = self.granaj(Ar.KRAJ, Ar.PUTA, Ar.PLUS, Ar.MINUS, Ar.ZATVORENA)
        if dalje == Ar.PUTA:
            self.pročitaj(Ar.PUTA)
            f2 = self.član()
            return AST(stablo='umnožak', lijevo=f2, desno=f1)
        else:
            return f1

    def faktor(self):
        if self.granaj(Ar.BROJ, Ar.OTVORENA) == Ar.BROJ:
            return self.pročitaj(Ar.BROJ)
        else:
            self.pročitaj(Ar.OTVORENA)
            u_zagradi = self.izraz()
            self.pročitaj(Ar.ZATVORENA)
            return u_zagradi

def aritm_parse(znakovi):
    *tokeni, KRAJ = aritm_lex(znakovi)
    assert KRAJ == Token(Ar.KRAJ, '')
    tokeni.reverse()
    for token in tokeni:
        if token.tip == Ar.OTVORENA: token.tip = Ar.ZATVORENA
        elif token.tip == Ar.ZATVORENA: token.tip = Ar.OTVORENA
    tokeni.append(KRAJ)
    parser = AritmParser(tokeni)
    rezultat = parser.izraz()
    parser.pročitaj(Ar.KRAJ)
    return rezultat


def vrijednost(fragment):
    if isinstance(fragment, Token):
        return int(fragment.sadržaj)
    else:
        l = vrijednost(fragment.lijevo)
        d = vrijednost(fragment.desno)
        if fragment.stablo == 'zbroj': return l + d
        elif fragment.stablo == 'razlika': return l - d
        elif fragment.stablo == 'umnožak': return l * d


def testiraj(izraz):
    mi = vrijednost(aritm_parse(izraz))
    Python = eval(izraz)
    if mi == Python:
        print(izraz, '==', mi, 'OK')
    else:
        print(izraz, 'mi:', mi, 'Python:', Python)


if __name__ == '__main__':
    testiraj('(2+3)*4-1')
    testiraj('6-1-3')
    testiraj('-2+-3--2*(-2+3)-1')
