from pj import *

class AQ(enum.Enum):
    NAT, INT, RAT = 'nat', 'int', 'rat'
    PLUS, MINUS, PUTA, KROZ, NA = '+-*/^'
    OTVORENA, ZATVORENA, JEDNAKO, UPITNIK = '()=?'
    DIV, MOD = 'div', 'mod'
    class IME(Token):
        def provjeri_tip(self, symtab): return pogledaj(symtab, self)
    class BROJ(Token):
        def provjeri_tip(self, symtab): return Tip.N
    class NOVIRED(Token): pass


def aq_lex(niz):
    lex = Tokenizer(niz)
    for znak in iter(lex.čitaj, ''):
        if znak == '\n':
            lex.zvijezda(str.isspace)
            yield lex.token(AQ.NOVIRED)
        elif znak.isspace(): lex.zanemari()
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(AQ.BROJ)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.literal(AQ.IME, case=False)
        else: yield lex.literal(AQ)


class Tip(enum.Enum):
    N = Token(AQ.NAT)
    Z = Token(AQ.INT)
    Q = Token(AQ.RAT)

    def __lt__(manji, veći): return (manji, veći) in {
        (Tip.N, Tip.Z), (Tip.N, Tip.Q), (Tip.Z, Tip.Q)}

    def __le__(manji, veći): return manji < veći or manji == veći


### Beskontekstna gramatika
# start -> NOVIRED? niz_naredbi NOVIRED?
# niz_naredbi -> naredba | naredba NOVIRED niz_naredbi
# naredba -> UPITNIK izraz | (NAT | INT | RAT)? IME JEDNAKO izraz
# izraz -> član | izraz (PLUS | MINUS) član
# član -> faktor | član (PUTA | KROZ | DIV | MOD) faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME | OTVORENA izraz ZATVORENA


class AQParser(Parser):
    def start(self):
        self >> AQ.NOVIRED
        self.symtab, naredbe = {}, []
        while not self >> E.KRAJ:
            n = self.naredba()
            if n ^ Pridruživanje:
                if n.tip is nenavedeno:
                    pogledaj(self.symtab, n.varijabla)
                elif n.varijabla.sadržaj in self.symtab:
                    if Tip(n.tip) is self.symtab[n.varijabla.sadržaj]:
                        raise SemantičkaGreška('redeklaracija {} varijable {}'.format(Tip(n.tip), n.varijabla.sadržaj))
                    else:
                        raise n.varijabla.krivi_tip(Tip(n.tip),
                                self.symtab[n.varijabla.sadržaj])
                else: self.symtab[n.varijabla.sadržaj] = Tip(n.tip)
            naredbe.append(n)
            self.pročitaj(AQ.NOVIRED, E.KRAJ)
        return Program(naredbe, self.symtab)

    def naredba(self):
        if self >> AQ.UPITNIK: return self.izraz()
        tip = self >> {AQ.NAT, AQ.INT, AQ.RAT} or nenavedeno
        varijabla = self.pročitaj(AQ.IME)
        self.pročitaj(AQ.JEDNAKO)
        inicijalizacija = self.izraz()
        return Pridruživanje(varijabla, tip, inicijalizacija)

    def izraz(self):
        trenutni = self.član()
        while self >> {AQ.PLUS, AQ.MINUS}:
            trenutni = BinOp(self.zadnji, trenutni, self.član())
        return trenutni

    def član(self):
        trenutni = self.faktor()
        while self >> {AQ.PUTA, AQ.KROZ, AQ.DIV, AQ.MOD}:
            trenutni = BinOp(self.zadnji, trenutni, self.faktor())
        return trenutni

    def faktor(self):
        if self >> AQ.MINUS: return Suprotan(self.faktor())
        baza = self.baza()
        if self >> AQ.NA: return BinOp(self.zadnji, baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> AQ.BROJ: return self.zadnji
        elif self >> AQ.IME:
            varijabla = self.zadnji
            pogledaj(self.symtab, varijabla)
            return varijabla
        elif self >> AQ.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AQ.ZATVORENA)
            return u_zagradi
        else: raise self.greška()


### Apstraktna sintaksna stabla
# Program: naredbe symtab
# Pridruživanje: varijabla tip? vrijednost
# Suprotan: operand
# BinOp: operator lijevo desno


class Program(AST('naredbe symtab')):
    def provjeri_tipove(self):
        symtab = dict(self.symtab)
        for naredba in self.naredbe:
            tip = naredba.provjeri_tip(symtab)
            if tip: print(tip)

class Pridruživanje(AST('varijabla tip vrijednost')):
    def provjeri_tip(self, symtab):
        lijevo = pogledaj(symtab, self.varijabla)
        desno = self.vrijednost.provjeri_tip(symtab)
        if not desno <= lijevo: raise self.varijabla.krivi_tip(lijevo, desno)

class Suprotan(AST('operand')):
    def provjeri_tip(self, symtab):
        return max(self.operand.provjeri_tip(symtab), Tip.Z)

class BinOp(AST('operator lijevo desno')):
    def provjeri_tip(self, symtab):
        prvi = self.lijevo.provjeri_tip(symtab)
        drugi = self.desno.provjeri_tip(symtab)
        op = self.operator
        greška = op.krivi_tip(prvi, drugi)
        if op ^ {AQ.PLUS, AQ.PUTA}: return max(prvi, drugi)
        elif op ^ AQ.KROZ: return Tip.Q
        elif op ^ AQ.MINUS: return max(prvi, drugi, Tip.Z)
        elif op ^ {AQ.DIV, AQ.MOD}:
            if prvi == Tip.Q or drugi != Tip.N: raise greška
            return prvi
        elif op ^ AQ.NA:
            if drugi == Tip.Q: raise greška
            return Tip.Q if drugi == Tip.Z else prvi


ast = AQParser.parsiraj(aq_lex('''\
    rat a = 6 / 2
    a = a + 4
    nat b = 8 + 1
    int c = 6 ^ 2
    rat d = 6
    d = d ^ 5
    ? b mod 1
    ? c mod b
    ? 6 ^ -3 - 3
'''))
prikaz(ast, 3)
ast.provjeri_tipove()
