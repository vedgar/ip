"""Aritmetika u Q, s deklaracijama varijabli, statičkim (sintaksnim) tipovima,
i provjerom tipova (typechecking). Podržana su tri tipa, totalno uređena s
obzirom na relaciju "biti podtip": nat (N), int (Z) i rat (Q)."""


from vepar import *


class T(TipoviTokena):
    NAT, INT, RAT, DIV, MOD = 'nat', 'int', 'rat', 'div', 'mod'
    PLUS, MINUS, PUTA, KROZ, NA, OTV, ZATV, JEDNAKO, UPIT = '+-*/^()=?'
    NOVIRED = '\n'
    class IME(Token):
        def provjeri_tip(t): return rt.symtab[t]
    class BROJ(Token):
        def provjeri_tip(t): return Tip.N

@lexer
def aq(lex):
    for znak in lex:
        if znak == '\n': yield lex.literal(T)  # prije provjere isspace!
        elif znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * {str.isalpha, '_'}
            yield lex.literal_ili(T.IME, case=False)
        else: yield lex.literal(T)


class Tip(enum.Enum):
    N = Token(T.NAT)
    Z = Token(T.INT)
    Q = Token(T.RAT)

    def __le__(t1, t2): return t1 is Tip.N or t2 is Tip.Q or t1 is t2
    
    def __lt__(t1, t2): return t1 <= t2 and t1 is not t2


### Beskontekstna gramatika
# start -> NOVIRED? niz_naredbi NOVIRED?
# niz_naredbi -> naredba | niz_naredbi NOVIRED naredba
# naredba -> UPIT izraz | (NAT|INT|RAT)? IME JEDNAKO izraz
# izraz -> član | izraz (PLUS|MINUS) član
# član -> faktor | član (PUTA|KROZ|DIV|MOD) faktor
# faktor -> baza | baza NA faktor | MINUS faktor
# baza -> BROJ | IME | OTV izraz ZATV


class P(Parser):
    def start(self) -> 'Program':
        self >= T.NOVIRED
        rt.symtab, naredbe = Memorija(), []
        while not self > KRAJ:
            naredbe.append(self.naredba())
            self >> {T.NOVIRED, KRAJ}
        return Program(naredbe)

    def naredba(self) -> 'izraz|Pridruživanje':
        if self >= T.UPIT: return self.izraz()
        token_za_tip = self >= {T.NAT, T.INT, T.RAT}
        ažuriraj(varijabla := self >> T.IME, token_za_tip)
        self >> T.JEDNAKO
        return Pridruživanje(varijabla, token_za_tip, self.izraz())

    def izraz(self) -> 'član|Op':
        t = self.član()
        while op := self >= {T.PLUS, T.MINUS}: t = Op(op, t, self.član())
        return t

    def član(self) -> 'faktor|Op':
        trenutni = self.faktor()
        while operator := self >= {T.PUTA, T.KROZ, T.DIV, T.MOD}:
            trenutni = Op(operator, trenutni, self.faktor())
        return trenutni

    def faktor(self) -> 'baza|Op':
        if op := self >= T.MINUS: return Op(op, nenavedeno, self.faktor())
        baza = self.baza()
        if op := self >= T.NA: return Op(op, baza, self.faktor())
        else: return baza

    def baza(self) -> 'BROJ|IME|izraz':
        if broj := self >= T.BROJ: return broj
        elif varijabla := self >= T.IME:
            varijabla.provjeri_tip()  # zapravo provjeri deklaraciju
            return varijabla
        elif self >> T.OTV:
            u_zagradi = self.izraz()
            self >> T.ZATV
            return u_zagradi


### Apstraktna sintaksna stabla
# Program: naredbe:[naredba]  # rt.symtab:Memorija
# Pridruživanje: varijabla:IME tip:T? vrijednost:izraz
# Op: operator:T lijevo:izraz desno:izraz

def ažuriraj(var, token_za_tip):
    if token_za_tip:
        tip = Tip(token_za_tip)
        if var in rt.symtab:
            pravi = var.provjeri_tip()
            if tip is pravi: raise var.redeklaracija()
            else: raise var.krivi_tip(tip, pravi)
        rt.symtab[var] = tip
    return var.provjeri_tip()

class Program(AST):
    naredbe: 'naredba*'
    def provjeri_tipove(self):
        for naredba in self.naredbe:
            tip = naredba.provjeri_tip()
            if tip: print(tip)

class Pridruživanje(AST):
    varijabla: 'IME'
    tip: 'Tip?'
    vrijednost: 'izraz'
    def provjeri_tip(self):
        lijevo = self.varijabla.provjeri_tip()
        desno = self.vrijednost.provjeri_tip()
        if not desno <= lijevo: raise self.varijabla.krivi_tip(lijevo, desno)

class Op(AST):
    operator: 'T'
    lijevo: 'izraz'
    desno: 'izraz'
    def provjeri_tip(self):
        if self.lijevo is nenavedeno: prvi = Tip.N  # -x = 0 - x
        else: prvi = self.lijevo.provjeri_tip()
        o, drugi = self.operator, self.desno.provjeri_tip()
        if o ^ T.KROZ: return Tip.Q
        elif o ^ {T.PLUS, T.PUTA}: return max(prvi, drugi)
        elif o ^ T.MINUS: return max(prvi, drugi, Tip.Z)
        # semantika: a div b := floor(a/b), a mod b := a - a div b * b
        elif o ^ T.DIV: return Tip.N if prvi is drugi is Tip.N else Tip.Z
        elif o ^ T.MOD: return Tip.Q if prvi is Tip.Q else drugi
        elif o ^ T.NA:
            if drugi is Tip.N: return prvi
            elif drugi is Tip.Z: return Tip.Q 
            else: raise o.krivi_tip(prvi, drugi)
        else: assert False, f'nepokriveni slučaj operatora {o}!'


ast = P('''
    rat a = 6 / 2
    a = a + 4
    nat b = 8 + 1
    int c = 6 ^ 2
    rat d = 6
    d = d ^ 5
    ? b mod 1
    ? c div b
    ? 6 ^ -3 - 3
''')
prikaz(ast, 3)
ast.provjeri_tipove()


# DZ: Dodajte tipove R i C (u statičku analizu; računanje je druga stvar:)
