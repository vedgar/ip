from pj import *


class LS(enum.Enum):
    NEG = '!'
    KONJ = '&'
    DISJ = '|'
    KOND = '->'
    BIKOND = '<->'
    OTV = '('
    ZATV = ')'
    class PVAR(Token):
        def makni_neg(var): return var, True
        def vrijednost(var, **I): return pogledaj(I, var)
        def ispis(var): return var.sadržaj.translate(
            str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))


def ls_lex(kod):
    lex = Tokenizer(kod)
    while True:
        znak = lex.čitaj()
        if not znak: return  # kraj ulaza
        elif znak == '!': yield lex.token(LS.NEG)
        elif znak == '&': yield lex.token(LS.KONJ)
        elif znak == '|': yield lex.token(LS.DISJ)
        elif znak == '(': yield lex.token(LS.OTV)
        elif znak == ')': yield lex.token(LS.ZATV)
        elif znak == '-':
            if lex.čitaj() == '>': yield lex.token(LS.KOND)
            else: raise lex.greška('Nepotpuna strelica')
        elif znak == '<':
            if lex.čitaj() == '-' and lex.čitaj() == '>':
                yield lex.token(LS.BIKOND)
            else: raise lex.greška('Nepotpuna strelica')
        elif znak == 'P':
            prvo = lex.čitaj()
            if prvo == '0': yield lex.token(LS.PVAR)
            elif prvo.isdigit():
                while lex.čitaj().isdigit(): pass
                lex.vrati()  # pročitali smo jedan previše
                yield lex.token(LS.PVAR)
            else: raise lex.greška('Nema znamenke nakon P')
        else: raise lex.greška()


class LSParser(Parser):
    def formula(pars):
        if pars >= LS.PVAR: return pars.čitaj()
        if pars >> LS.NEG: return Negacija(ispod=pars.formula())
        pars.pročitaj(LS.OTV)  # 
        l, klasa, d = pars.formula(), pars.binvez(), pars.formula()
        pars.pročitaj(LS.ZATV)
        return klasa(l, d)

    def binvez(pars):
        if pars >> LS.KONJ: return Konjunkcija
        if pars >> LS.DISJ: return Disjunkcija
        if pars >> LS.KOND: return Kondicional
        pars.pročitaj(LS.BIKOND)
        return Bikondicional

    start = formula


class Negacija(AST('ispod')):
    veznik = '¬'

    def vrijednost(self, **I): return not self.ispod.vrijednost(**I)

    def makni_neg(self):
        bez_neg, pozitivna = self.ispod.makni_neg()
        return bez_neg, not pozitivna

    def ispis(self): return self.veznik + self.ispod.ispis()


class Binarna(AST('lijevo desno')):
    def vrijednost(self, **I):
        klasa = type(self)
        l, d = self.lijevo.vrijednost(**I), self.desno.vrijednost(**I)
        return klasa.istina(l, d)

    def makni_neg(self):
        klasa = type(self)
        l, lp = self.lijevo.makni_neg()
        d, dp = self.desno.makni_neg()
        return klasa.xform(l, d, lp, dp), klasa.istina(lp, dp)

    def ispis(self): return '(' + self.lijevo.ispis() + \
            self.veznik + self.desno.ispis() + ')'


class Disjunkcija(Binarna):
    veznik = '∨'

    def istina(l, d): return l or d

    def xform(l, d, lp, dp):
        if lp and dp: return Disjunkcija(l, d)
        if not lp and dp: return Kondicional(l, d)
        if lp and not dp: return Kondicional(d, l)
        return Konjunkcija(l, d)


class Konjunkcija(Binarna):
    veznik = '∧'

    def istina(l, d): return l and d

    def xform(l, d, lp, dp): return Disjunkcija.xform(l,d,not lp,not dp)


class Kondicional(Binarna):
    veznik = '→'

    def istina(l, d):
        if l: return d
        return True
    
    def xform(l, d, lp, dp): return Disjunkcija.xform(l, d, not lp, dp)


class Bikondicional(Binarna):
    veznik = '↔'

    def istina(l, d): return l == d

    def xform(l, d, lp, dp): return Bikondicional(l, d)


def optim(formula):
    """Pretvara formulu (AST) u oblik s najviše jednom negacijom."""
    bez_neg, pozitivna = formula.makni_neg()
    if pozitivna: return bez_neg
    else: return Negacija(bez_neg)


kod = '(!P0&(!P1<->!P5))'
fo = LSParser.parsiraj(ls_lex(kod))
for token in ls_lex(kod):
    print(token.tip, token.sadržaj, token.početak, token.kraj)
print(kod)
print(fo.ispis())
prikaz(fo, 5)
print('-' * 60)
fo = optim(fo)
print(fo.ispis())
prikaz(fo, 4)
print('-' * 60)
for krivo in 'P00', 'P1\nP2', 'P34<>P56':
    with očekivano(LeksičkaGreška): print(*ls_lex(krivo))
