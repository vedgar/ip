from pj import *

class T(TipoviTokena):
    NAT, INT, RAT, DIV, MOD = 'nat', 'int', 'rat', 'div', 'mod'
    PLUS, MINUS, PUTA, KROZ, NA, OTV, ZATV, JEDNAKO, UPIT = '+-*/^()=?'
    NOVIRED = TipTokena()
    class IME(Token):
        def provjeri_tip(self, symtab): return symtab[self]
    class BROJ(Token):
        def provjeri_tip(self, symtab): return Tip.N


def aq(lex):
    for znak in lex:
        if znak == '\n': yield lex.token(T.NOVIRED)
        elif znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.literal(T.IME, case=False)
        else: yield lex.literal(T)


class Tip(enum.Enum):
    N = T.NAT
    Z = T.INT
    Q = T.RAT

    @classmethod
    def iz_tokena(cls, token): return cls(token.tip)

    def __le__(prvi, drugi):
        return prvi is Tip.N or drugi is Tip.Q or prvi is drugi

    def __lt__(prvi, drugi): return prvi <= drugi and prvi is not drugi


### Beskontekstna gramatika
# start -> NOVIRED? niz_naredbi NOVIRED?
# niz_naredbi -> naredba | naredba NOVIRED niz_naredbi
# naredba -> UPIT izraz | (NAT|INT|RAT) IME JEDNAKO izraz
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član (PUTA|KROZ|DIV|MOD) faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME | OTV izraz ZATV


class P(Parser):
    lexer = aq

    def start(self):
        self >> T.NOVIRED
        self.symtab, naredbe = Memorija(), []
        while not self >> KRAJ:
            naredbe.append(self.naredba())
            self.pročitaj(T.NOVIRED, KRAJ)
        return Program(naredbe, self.symtab)


    def naredba(self):
        if self >> T.UPIT: return self.izraz()
        if self >> {T.NAT, T.INT, T.RAT}: tip = self.zadnji
        else: tip = nenavedeno
        varijabla = self.pročitaj(T.IME)
        ažuriraj(varijabla, tip, self.symtab)
        self.pročitaj(T.JEDNAKO)
        inicijalizacija = self.izraz()
        return Pridruživanje(varijabla, tip, inicijalizacija)

    def izraz(self):
        t = self.član()
        while self >> {T.PLUS, T.MINUS}: t = Op(self.zadnji, t, self.član())
        return t

    def član(self):
        trenutni = self.faktor()
        while self >> {T.PUTA, T.KROZ, T.DIV, T.MOD}:
            trenutni = Op(self.zadnji, trenutni, self.faktor())
        return trenutni

    def faktor(self):
        if self >> T.MINUS: return Op(self.zadnji, nenavedeno, self.faktor())
        baza = self.baza()
        if self >> T.NA: return Op(self.zadnji, baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> T.BROJ: return self.zadnji
        elif self >> T.IME:
            varijabla = self.zadnji
            self.symtab[varijabla]
            return varijabla
        elif self >> T.OTV:
            u_zagradi = self.izraz()
            self.pročitaj(T.ZATV)
            return u_zagradi
        else: raise self.greška()


### Apstraktna sintaksna stabla
# Program: naredbe symtab
# Pridruživanje: varijabla tip? vrijednost
# Suprotan: operand
# Op: operator lijevo desno


def ažuriraj(var, tip, symtab):
    if tip is not nenavedeno:
        tip = Tip.iz_tokena(tip)
        if var in symtab: raise var.krivi_tip(tip, symtab[var])
        symtab[var] = tip
    return symtab[var]


class Program(AST('naredbe symtab')):
    def provjeri_tipove(self):
        symtab = Memorija(dict(self.symtab))
        for naredba in self.naredbe:
            tip = naredba.provjeri_tip(symtab)
            if tip: print(tip)

class Pridruživanje(AST('varijabla tip vrijednost')):
    def provjeri_tip(self, symtab):
        lijevo = symtab[self.varijabla]
        desno = self.vrijednost.provjeri_tip(symtab)
        if not desno <= lijevo: raise self.varijabla.krivi_tip(lijevo, desno)

class Op(AST('operator lijevo desno')):
    def provjeri_tip(self, symtab):
        if self.lijevo is nenavedeno: prvi = Tip.N  # -x = 0 - x
        else: prvi = self.lijevo.provjeri_tip(symtab)
        drugi = self.desno.provjeri_tip(symtab)
        o = self.operator
        greška = o.krivi_tip(prvi, drugi)
        if o ^ T.KROZ: return Tip.Q
        elif o ^ {T.PLUS, T.PUTA}: return max(prvi, drugi)
        elif o ^ T.MINUS: return max(prvi, drugi, Tip.Z)
        elif o ^ {T.DIV, T.MOD}:
            if prvi is Tip.Q: raise greška
            elif drugi is Tip.N: return prvi
            else: raise greška
        elif o ^ T.NA:
            if drugi is Tip.N: return prvi
            elif drugi is Tip.Z: return Tip.Q 
            else: raise greška


ast = P('''\
    rat a = 6 / 2
    a = a + 4
    nat b = 8 + 1
    int c = 6 ^ 2
    rat d = 6
    d = d ^ 5
    ? b mod 1
    ? c mod b
    ? 6 ^ -3 - 3
''')
prikaz(ast, 3)
ast.provjeri_tipove()