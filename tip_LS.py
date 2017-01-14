from tip import Parser, Token, AST, Tokenizer
import enum


class LS(enum.Enum):
    PRAZNO, KRAJ, GREŠKA = range(3)
    PVAR, NEG, KON, DIS, KOND, BIKOND, OTV, ZATV = range(3, 11)

class LexError(Exception):
    pass

def ls_lex(kôd):
    lex = Tokenizer(kôd)
    while True:
        znak = lex.čitaj()
        if znak == 'P': yield Token(LS.PVAR, znak + lex.broj())
        elif znak == '!': yield Token(LS.NEG, znak)
        elif znak == '|': yield Token(LS.DIS, znak)
        elif znak == '&': yield Token(LS.KON, znak)
        elif znak == '(': yield Token(LS.OTV, znak)
        elif znak == ')': yield Token(LS.ZATV, znak)
        elif znak == '-':
            drugi = lex.čitaj()
            if drugi == '>': yield Token(LS.KOND, znak + drugi)
            else:
                poruka = 'Nakon - očekivano >, pročitano {}'
                raise LexError(poruka.format(drugi))
        elif znak == '<':
            drugi, treći = lex.čitaj(), lex.čitaj()
            if (drugi, treći) == ('-', '>'):
                yield Token(LS.BIKOND, znak + drugi + treći)
            else:
                poruka = 'Nakon < očekivano ->, pročitano {}{}'
                raise LexError(poruka.format(drugi, treći))
        elif znak is None: yield Token(LS.KRAJ, ''); return
        else: yield Token(LS.GREŠKA, znak)


class LSParser(Parser):    
    def formula(self):
        fo = AST(stablo='formula')
        početak = self.granaj(LS.NEG, LS.PVAR, LS.OTV)
        if početak == LS.PVAR:
            fo.varijabla = self.pročitaj(LS.PVAR)
        elif početak == LS.NEG:
            fo.veznik = self.pročitaj(LS.NEG)
            fo.negirana = self.formula()
        elif početak == LS.OTV:
            self.pročitaj(LS.OTV)
            fo.lijeva = self.formula()
            fo.veznik = self.pročitaj(LS.KON, LS.DIS, LS.KOND, LS.BIKOND)
            fo.desna = self.formula()
            self.pročitaj(LS.ZATV)
        return fo

def ls_parse(niz_znakova):
    parser = LSParser(ls_lex(niz_znakova))
    rezultat = parser.formula()
    parser.pročitaj(LS.KRAJ)
    return rezultat


if __name__ == '__main__':
    print(*ls_lex('P5&(P3->P1)'), sep='\n')
    print(ls_parse('!(P5&(P3->P1))'))
