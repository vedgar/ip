from pj import *

class PSK(enum.Enum):
    AKO, DOK, INAČE = 'ako', 'dok', 'inače'
    JE, NIJE, ILI = 'je', 'nije', 'ili'
    OTV, ZATV, ZAREZ = '(),'
    JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '=<+-*'
    class AIME(Token):
        def vrijednost(self, mem): return mem[self.sadržaj]
    class LIME(Token):
        def istina(self, mem): return mem[self.sadržaj]
    class BROJ(Token):
        def vrijednost(self, mem): return int(self.sadržaj)
    class LKONST(Token):
        def istina(self, mem): return self.sadržaj == 'istina'

def pseudokod_lexer(program):
    lex = Tokenizer(program)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.islower():
            lex.zvijezda(str.isalpha)
            if lex.sadržaj in {'istina', 'laž'}: yield lex.token(PSK.LKONST)
            else: yield lex.token(ključna_riječ(PSK, lex.sadržaj) or PSK.AIME)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.token(PSK.LIME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(PSK.BROJ)
        else:
            yield lex.token(operator(PSK, znak) or lex.greška())

# naredba -> (AKO | DOK) (JE | NIJE) log naredba |
#            AKO JE log naredba INAČE naredba | pridruži | OTV naredbe? ZATV
# naredbe -> naredba ZAREZ naredbe | naredba
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm MANJE aritm | aritm JEDNAKO aritm | LIME | ISTINA | LAŽ
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OOTV aritm OZATV

class PseudokodParser(Parser):
    def naredba(self):
        if self.slijedi(PSK.AKO, PSK.DOK):
            petlja = self.zadnji.je(PSK.DOK)
            željeno = self.pročitaj(PSK.JE, PSK.NIJE).je(PSK.JE)
            uvjet, naredba = self.log(), self.naredba()
            if petlja: return Petlja(uvjet, bool(željeno), naredba)
            if željeno and self.slijedi(PSK.INAČE): inače = self.naredba()
            else: inače = Blok([])
            return Grananje(uvjet, bool(željeno), naredba, inače)
        elif self.slijedi(PSK.OTV):
            if self.slijedi(PSK.ZATV): return Blok([])
            u_zagradi = self.naredbe()
            self.pročitaj(PSK.ZATV)
            return u_zagradi
        else:
            ime = self.pročitaj(PSK.AIME, PSK.LIME)
            _, logički = self.pročitaj(PSK.JEDNAKO), ime.je(PSK.LIME)
            vrijednost = self.log() if logički else self.aritm()
            return Pridruživanje(ime, vrijednost, bool(logički))

    def naredbe(self):
        naredbe = [self.naredba()]
        while self.slijedi(PSK.ZAREZ):
            if self.vidi(PSK.ZATV): return Blok(naredbe)
            naredbe.append(self.naredba())
        return Blok(naredbe)

    def log(self):
        disjunkti = [self.disjunkt()]
        while self.slijedi(PSK.ILI): disjunkti.append(self.disjunkt())
        return disjunkti[0] if len(disjunkti) == 1 else Disjunkcija(disjunkti)

    def disjunkt(self):
        if self.slijedi(PSK.LKONST, PSK.LIME): return self.zadnji
        lijevo = self.aritm()
        manje = self.pročitaj(PSK.JEDNAKO, PSK.MANJE).je(PSK.MANJE)
        desno = self.aritm()
        return Usporedba(bool(manje), lijevo, desno)
    
    def aritm(self):
        članovi = [self.član()]
        while self.slijedi(PSK.PLUS, PSK.MINUS):
            operator = self.zadnji
            dalje = self.član()
            članovi.append(dalje if operator.je(PSK.PLUS) else Suprotan(dalje))
        return članovi[0] if len(članovi) == 1 else Zbroj(članovi)

    def član(self):
        if self.slijedi(PSK.MINUS): return Suprotan(self.faktor())
        faktori = [self.faktor()]
        while self.slijedi(PSK.ZVJEZDICA): faktori.append(self.faktor())
        return faktori[0] if len(faktori) == 1 else Umnožak(faktori)

    def faktor(self):
        if self.slijedi(PSK.BROJ, PSK.AIME): return self.zadnji
        self.pročitaj(PSK.OTV)
        u_zagradi = self.aritm()
        self.pročitaj(PSK.ZATV)
        return u_zagradi

    start = naredbe


class Grananje(AST('uvjet željeno naredba inače')):
    def izvrši(self, mem):
        if self.uvjet.istina(mem) == self.željeno: self.naredba.izvrši(mem)
        else: self.inače.izvrši(mem)

class Petlja(AST('uvjet željeno naredba')):
    def izvrši(self, mem):
        while self.uvjet.istina(mem) == self.željeno:
            self.naredba.izvrši(mem)

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)

    def rezultat(self, **init):
        self.izvrši(init)
        return types.SimpleNamespace(**init)

class Pridruživanje(AST('ime pridruženo logički')):
    def izvrši(self, mem):
        if self.logički: mem[self.ime.sadržaj] = self.pridruženo.istina(mem)
        else: mem[self.ime.sadržaj] = self.pridruženo.vrijednost(mem)
    
class Disjunkcija(AST('disjunkti')):
    def istina(self, mem):
        return any(d.istina(mem) for d in self.disjunkti)
    
class Usporedba(AST('manje lijevo desno')):
    def istina(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        return l < d if self.manje else l == d

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem):
        return sum(p.vrijednost(mem) for p in self.pribrojnici)
    
class Suprotan(AST('od')):
    def vrijednost(self, mem): return -self.od.vrijednost(mem)
    
class Umnožak(AST('faktori')):
    def vrijednost(self, mem):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem)
        return p

faktorijela = PseudokodParser.parsiraj(pseudokod_lexer('''\
    f = 1,
    starix = x,
    dok nije x = 0 (
        f = f * x,
        x = x - 1
    ),
    Jednaki = f=starix
'''))
print(faktorijela.rezultat(x=1))
