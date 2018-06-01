from pj import *

class PSK(enum.Enum):
    AKO, DOK, INAČE = 'ako', 'dok', 'inače'
    JE, NIJE, ILI = 'je', 'nije', 'ili'
    OTV, ZATV, ZAREZ = '(),'
    JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '=<+-*'
    class AIME(Token):
        """Aritmetičko ime (ime za broj), počinje malim slovom."""
        def vrijednost(self, mem):
            return mem[self.sadržaj]

    class LIME(Token):
        """Logičko ime (ime za logičku vrijednost), počinje velikim slovom."""
        def istina(self, mem):
            return mem[self.sadržaj]

    class BROJ(Token):
        """Aritmetička konstanta (prirodni broj)."""
        def vrijednost(self, mem):
            return int(self.sadržaj)

    class LKONST(Token):
        """Logička konstanta (istina ili laž)."""
        def istina(self, mem):
            return self.sadržaj == 'istina'

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
# disjunkt -> aritm (MANJE | JEDNAKO) aritm | LIME | LKONST
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OOTV aritm OZATV

class PseudokodParser(Parser):
    def naredba(self):
        if self >> {PSK.AKO, PSK.DOK}:
            petlja = self.zadnji ** PSK.DOK
            željeno = self.pročitaj(PSK.JE, PSK.NIJE) ** PSK.JE
            uvjet, naredba = self.log(), self.naredba()
            if petlja: return Petlja(uvjet, bool(željeno), naredba)
            if željeno and self >> PSK.INAČE: inače = self.naredba()
            else: inače = Blok([])
            return Grananje(uvjet, bool(željeno), naredba, inače)
        elif self >> PSK.OTV:
            if self >> PSK.ZATV: return Blok([])
            u_zagradi = self.naredbe()
            self.pročitaj(PSK.ZATV)
            return u_zagradi
        elif self >> {PSK.AIME, PSK.LIME}:
            ime = self.zadnji
            self.pročitaj(PSK.JEDNAKO)
            logički = ime ** PSK.LIME
            vrijednost = self.log() if logički else self.aritm()
            return Pridruživanje(ime, vrijednost, bool(logički))
        else:
            self.greška()

    def naredbe(self):
        naredbe = [self.naredba()]
        while self >> PSK.ZAREZ:
            if self >= PSK.ZATV: return Blok(naredbe)
            naredbe.append(self.naredba())
        return Blok(naredbe)

    def log(self):
        disjunkti = [self.disjunkt()]
        while self >> PSK.ILI: disjunkti.append(self.disjunkt())
        return disjunkti[0] if len(disjunkti) == 1 else Disjunkcija(disjunkti)

    def disjunkt(self):
        if self >> {PSK.LKONST, PSK.LIME}: return self.zadnji
        lijevo = self.aritm()
        manje = self.pročitaj(PSK.JEDNAKO, PSK.MANJE) ** PSK.MANJE
        desno = self.aritm()
        return Usporedba(bool(manje), lijevo, desno)
    
    def aritm(self):
        članovi = [self.član()]
        while self >> {PSK.PLUS, PSK.MINUS}:
            operator = self.zadnji
            dalje = self.član()
            članovi.append(dalje if operator ** PSK.PLUS else Suprotan(dalje))
        return članovi[0] if len(članovi) == 1 else Zbroj(članovi)

    def član(self):
        if self >> PSK.MINUS: return Suprotan(self.faktor())
        faktori = [self.faktor()]
        while self >> PSK.ZVJEZDICA: faktori.append(self.faktor())
        return faktori[0] if len(faktori) == 1 else Umnožak(faktori)

    def faktor(self):
        if self >> {PSK.BROJ, PSK.AIME}: return self.zadnji
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

faktorijela = PseudokodParser.parsiraj(pseudokod_lexer('''
f = 1,
J = laž,
dok nije x = 0 (
  f = f*x,
  x = x-1,
  ako je x = f
    J = istina,
)
'''))
print(faktorijela)
# Blok(naredbe=[
#   Pridruživanje(ime=AIME'f', pridruženo=BROJ'1', logički=False),
#   Petlja(uvjet=Usporedba(manje=False, lijevo=AIME'x', desno=BROJ'0'),
#     željeno=False, 
#     naredba=Blok(naredbe=[
#       Pridruživanje(ime=AIME'f', 
#                     pridruženo=Umnožak(faktori=[AIME'f', AIME'x']), 
#                     logički=False), 
#       Pridruživanje(ime=AIME'x', 
#                     pridruženo=Zbroj(pribrojnici=[AIME'x', Suprotan(od=BROJ'1')]), 
#                     logički=False)]
#     )
#   )
# ])


# print(faktorijela.rezultat(x=7).f)
print()
mem = {'x': 7}
faktorijela.izvrši(mem)
print(mem)
