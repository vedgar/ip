"""Aritmetika u Q, s deklaracijama varijabli, statičkim (sintaksnim) tipovima,
i provjerom tipova (typechecking). Podržana su tri tipa, totalno uređena s
obzirom na relaciju "biti podtip": nat (N), int (Z) i rat (Q)."""


from vepar import *


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
    N = Token(T.NAT)
    Z = Token(T.INT)
    Q = Token(T.RAT)

    def __le__(t1, t2): return t1 is Tip.N or t2 is Tip.Q or t1 is t2
    
    def __lt__(t1, t2): return t1 <= t2 and t1 is not t2


### Beskontekstna gramatika
# start -> NOVIRED? niz_naredbi NOVIRED?
# niz_naredbi -> naredba | naredba NOVIRED niz_naredbi
# naredba -> UPIT izraz | (NAT|INT|RAT)? IME JEDNAKO izraz
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član (PUTA|KROZ|DIV|MOD) faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME | OTV izraz ZATV


class P(Parser):
    lexer = aq

    def start(self):
        self >= T.NOVIRED
        self.symtab, naredbe = Memorija(), []
        while not self > KRAJ:
            naredbe.append(self.naredba())
            self >> {T.NOVIRED, KRAJ}
        return Program(naredbe, self.symtab)

    def naredba(self):
        if self >= T.UPIT: return self.izraz()
        tip = self >= {T.NAT, T.INT, T.RAT}
        varijabla = self >> T.IME
        ažuriraj(varijabla, tip, self.symtab)
        self >> T.JEDNAKO
        return Pridruživanje(varijabla, tip, self.izraz())

    def izraz(self):
        t = self.član()
        while op := self >= {T.PLUS, T.MINUS}: t = Op(op, t, self.član())
        return t

    def član(self):
        trenutni = self.faktor()
        while operator := self >= {T.PUTA, T.KROZ, T.DIV, T.MOD}:
            trenutni = Op(operator, trenutni, self.faktor())
        return trenutni

    def faktor(self):
        if op := self >= T.MINUS: return Op(op, nenavedeno, self.faktor())
        baza = self.baza()
        if op := self >= T.NA: return Op(op, baza, self.faktor())
        else: return baza

    def baza(self):
        if broj := self >= T.BROJ: return broj
        elif varijabla := self >= T.IME:
            self.symtab[varijabla]
            return varijabla
        elif self >> T.OTV:
            u_zagradi = self.izraz()
            self >> T.ZATV
            return u_zagradi


### Apstraktna sintaksna stabla
# Program: naredbe symtab
# Pridruživanje: varijabla tip? vrijednost
# Suprotan: operand
# Op: operator lijevo desno


def ažuriraj(var, tip, symtab):
    if tip is not nenavedeno:
        tip = Tip(tip)
        if var in symtab:
            if tip == symtab[var]: raise var.redeklaracija()
            else: raise var.krivi_tip(tip, symtab[var])
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
