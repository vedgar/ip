from pj import *

class PSK(enum.Enum):
    AKO, DOK, INAČE = 'ako', 'dok', 'inače'
    JE, NIJE, ILI = 'je', 'nije', 'ili'
    VRATI = 'vrati'
    OTV, ZATV, ZAREZ = '(),'
    JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '=<+-*'
    
    class AIME(Token):
        """Aritmetičko ime (ime za broj), počinje malim slovom."""
        def vrijednost(self, mem): return mem[self]

    class LIME(Token):
        """Logičko ime (ime za logičku vrijednost), počinje velikim slovom."""
        def vrijednost(self, mem): return mem[self]

    class BROJ(Token):
        """Aritmetička konstanta (prirodni broj)."""
        def vrijednost(self, mem): return int(self.sadržaj)

    class LKONST(Token):
        """Logička konstanta (istina ili laž)."""
        def vrijednost(self, mem): return self.sadržaj == 'istina'

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
        else: yield lex.token(operator(PSK, znak) or lex.greška())


### BKG (ne sasvim BK:)
# naredba -> pridruži | OTV naredbe? ZATV | (AKO | DOK) (JE | NIJE) log naredba
#            | AKO JE log naredba INAČE naredba | VRATI izraz
# ime -> AIME | LIME
# parametri -> ime (ZAREZ parametri)?
# naredbe -> naredba (ZAREZ naredbe)?
# program -> ime OTV parametri? ZATV JEDNAKO naredba program?
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm (MANJE | JEDNAKO) aritm | LIME | LKONST |
#             LIME OTV argumenti ZATV
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OTV aritm ZATV | AIME OTV argumenti ZATV
# argumenti -> izraz (ZAREZ argumenti)?
# izraz -> aritm |! log [KONTEKST!]

class PseudokodParser(Parser):
    def program(self):
        self.funkcije = {}
        while not self >> E.KRAJ:
            funkcija = self.funkcija()
            imef = funkcija.ime
            if imef in self.funkcije: raise SemantičkaGreška(
                'Dvaput definirana funkcija ' + imef.sadržaj)
            self.funkcije[imef] = funkcija
        return self.funkcije

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
            vrijednost = self.log() if ime ** PSK.LIME else self.aritm()
            return Pridruživanje(ime, vrijednost)
        elif self >> PSK.VRATI:
            return Vrati(self.log() if self.logička else self.aritm())
        else: self.greška()

    def funkcija(self):
        ime = self.pročitaj(PSK.LIME, PSK.AIME)
        self.logička = bool(ime ** PSK.LIME)
        self.pročitaj(PSK.OTV)
        if self >> PSK.ZATV: parametri = []
        elif self >> {PSK.LIME, PSK.AIME}:
            parametri = [self.zadnji]
            while self >> PSK.ZAREZ:
                parametri.append(self.pročitaj(PSK.LIME, PSK.AIME))
            self.pročitaj(PSK.ZATV)
        else: self.greška()
        self.pročitaj(PSK.JEDNAKO)
        naredba = self.naredba()
        return Funkcija(ime, parametri, naredba)

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
        if self >> PSK.LKONST: return self.zadnji
        elif self >> PSK.LIME:
            ime = self.zadnji
            if self >= PSK.OTV: return self.poziv(ime)
            else: return ime
        lijevo = self.aritm()
        manje = self.pročitaj(PSK.JEDNAKO, PSK.MANJE) ** PSK.MANJE
        desno = self.aritm()
        return Usporedba(bool(manje), lijevo, desno)

    def poziv(self, ime):
        if ime in self.funkcije: funkcija = self.funkcije[ime]
        else: raise SemantičkaGreška(
            'Nedeklarirana funkcija ' + ime.sadržaj)
        return Poziv(funkcija, self.argumenti(funkcija.parametri))

    def argumenti(self, parametri):
        arg = []
        prvi = True
        for parametar in parametri:
            self.pročitaj(PSK.OTV if prvi else PSK.ZAREZ)
            prvi = False
            if parametar ** PSK.LIME: arg.append(self.log())
            else: arg.append(self.aritm())
        self.pročitaj(PSK.ZATV)
        return arg
    
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
        if self >> PSK.BROJ: return self.zadnji
        elif self >> PSK.AIME:
            ime = self.zadnji
            if self >= PSK.OTV: return self.poziv(ime)
            else: return ime
        else:
            self.pročitaj(PSK.OTV)
            u_zagradi = self.aritm()
            self.pročitaj(PSK.ZATV)
            return u_zagradi

    start = program


def izvrši(funkcije, *argv):
    program = Token(PSK.AIME, 'program')
    if program in funkcije:
        izlazna_vrijednost = funkcije[program].pozovi(argv)
        print('Program je vratio: ', izlazna_vrijednost)
    else: raise SemantičkaGreška('Nema glavne funkcije "program"')


class Funkcija(AST('ime parametri naredba')):
    def pozovi(self, argumenti):
        lokalni = dict(zip(self.parametri, argumenti))
        try: self.naredba.izvrši(lokalni)
        except Povratak as exc: return exc.povratna_vrijednost

class Poziv(AST('funkcija argumenti')):
    def vrijednost(self, mem):
        arg = [argument.vrijednost(mem) for argument in self.argumenti]
        return self.funkcija.pozovi(arg)

class Grananje(AST('uvjet željeno naredba inače')):
    def izvrši(self, mem):
        if self.uvjet.vrijednost(mem) == self.željeno: self.naredba.izvrši(mem)
        else: self.inače.izvrši(mem)

class Petlja(AST('uvjet željeno naredba')):
    def izvrši(self, mem):
        while self.uvjet.vrijednost(mem) == self.željeno:
            self.naredba.izvrši(mem)

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem): mem[self.ime] = self.pridruženo.vrijednost(mem)

class Vrati(AST('što')):
    def izvrši(self, mem): raise Povratak(self.što.vrijednost(mem))

class Disjunkcija(AST('disjunkti')):
    def vrijednost(self, mem):
        return any(disjunkt.vrijednost(mem) for disjunkt in self.disjunkti)
    
class Usporedba(AST('manje lijevo desno')):
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        return l < d if self.manje else l == d

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem):
        return sum(pribroj.vrijednost(mem) for pribroj in self.pribrojnici)
    
class Suprotan(AST('od')):
    def vrijednost(self, mem): return -self.od.vrijednost(mem)
    
class Umnožak(AST('faktori')):
    def vrijednost(self, mem):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem)
        return p


class Povratak(Exception):
    @property
    def povratna_vrijednost(self): return self.args[0]


faktorijela = PseudokodParser.parsiraj(pseudokod_lexer('''
fakt(x) = (
    f = 1,
    dok nije x = 0 (
        f = f*x,
        x = x-1
    ),
    vrati f
)
Neparan(x) = (
    N = laž,
    dok nije x = 0 (
        x = x - 1,
        ako je N N = laž inače N = istina
    ),
    vrati N
)
program() = (
    s = 0,
    t = 0,
    dok je t < 9 (
        ako je Neparan(t) s = s + fakt(t),
        t = t + 1
    ),
    vrati s
)
'''))
print(faktorijela)
print()
izvrši(faktorijela, {})
