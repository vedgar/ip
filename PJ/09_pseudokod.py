"""Interpreter za pseudokod, s funkcijskim pozivima i dva tipa podataka.

Podržane naredbe:
    ako je uvjet naredba inače naredba      ime = izraz
    ako je uvjet naredba                    Ime = uvjet
    ako nije uvjet naredba                  vrati izraz
    dok je uvjet naredba                    vrati uvjet
    dok nije uvjet naredba                  (naredba1, naredba2, ...)

Podržani aritmetički izrazi:            Podržani logički uvjeti:
    cijeli_broj                             Istina
    ime                                     Laž
    ime(argumenti)                          Ime
    izraz + izraz                           Ime(argumenti)
    izraz - izraz                           uvjet Ili uvjet
    izraz * izraz                           izraz < izraz
    -izraz                                  izraz = izraz
    (izraz)                                 (uvjet)

Program se sastoji od jedne ili više deklaracija funkcija, s ili bez parametara.
    Jedna od njih mora biti program(parametri), od nje počinje izvršavanje.
Tipovi varijabli (i povratni tipovi funkcija) se reprezentiraju leksički:
    veliko početno slovo označava logički tip (bool)
    malo početno slovo označava aritmetički tip (int)

Minimalni kontekst je potreban da bismo zapamtili jesmo li trenutno u definiciji
    aritmetičke ili logičke funkcije, kako bi naredba "vrati" znala što očekuje.
"""


from pj import *

class PSK(enum.Enum):
    AKO, DOK, INAČE, VRATI = 'ako', 'dok', 'inače', 'vrati'
    JE, NIJE, ILI = 'je', 'nije', 'Ili'
    OTV, ZATV, ZAREZ, JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '(),=<+-*'
    
    class AIME(Token):
        """Aritmetičko ime (ime za broj), počinje malim slovom."""
        def vrijednost(self, mem): return pogledaj(mem, self)

    class LIME(Token):
        """Logičko ime (ime za logičku vrijednost), počinje velikim slovom."""
        def vrijednost(self, mem): return pogledaj(mem, self)

    class BROJ(Token):
        """Aritmetička konstanta (prirodni broj)."""
        def vrijednost(self, mem): return int(self.sadržaj)

    class LKONST(Token):
        """Logička konstanta (istina ili laž)."""
        def vrijednost(self, mem): return self.sadržaj == 'Istina'

def pseudokod_lexer(program):
    lex = Tokenizer(program)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.islower():
            lex.zvijezda(str.isalpha)
            yield lex.literal(PSK.AIME)
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            if lex.sadržaj in {'Istina', 'Laž'}: yield lex.token(PSK.LKONST)
            else: yield lex.literal(PSK.LIME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(PSK.BROJ)
        elif znak == '#':
            lex.pročitaj_do('\n')
            lex.zanemari()
        else: yield lex.literal(PSK)


### BKG (ne sasvim BK:)
# naredba -> pridruži | OTV naredbe? ZATV | (AKO | DOK) (JE | NIJE) log naredba
#            | AKO JE log naredba INAČE naredba | VRATI argument
# ime -> AIME | LIME
# parametri -> ime (ZAREZ parametri)?
# naredbe -> naredba (ZAREZ naredbe)?
# program -> ime OTV parametri? ZATV JEDNAKO naredba program?
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm (MANJE | JEDNAKO) aritm | LIME | LKONST |
#             LIME OTV argumenti ZATV | OTV log ZATV
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OTV aritm ZATV | AIME OTV argumenti ZATV
# argumenti -> argument (ZAREZ argumenti)?
# argument -> aritm |! log  [KONTEKST!]

class PseudokodParser(Parser):
    def program(self):
        self.funkcije = {}
        while not self >> E.KRAJ:
            funkcija = self.funkcija()
            imef = funkcija.ime
            if imef in self.funkcije: raise SemantičkaGreška(
                'Dvaput definirana funkcija {}'.format(imef))
            self.funkcije[imef] = funkcija
        return self.funkcije

    def naredba(self):
        if self >> {PSK.AKO, PSK.DOK}:
            petlja = self.zadnji ^ PSK.DOK
            istina = bool(self.pročitaj(PSK.JE, PSK.NIJE) ^ PSK.JE)
            uvjet, naredba = self.log(), self.naredba()
            if petlja: return Petlja(uvjet, istina, naredba)
            inače = self.naredba() if istina and self >> PSK.INAČE else Blok([])
            return Grananje(uvjet, istina, naredba, inače)
        elif self >> PSK.OTV:
            if self >> PSK.ZATV: return Blok([])
            u_zagradi = self.naredbe()
            self.pročitaj(PSK.ZATV)
            return u_zagradi
        elif self >> {PSK.AIME, PSK.LIME}:
            ime = self.zadnji
            self.pročitaj(PSK.JEDNAKO)
            vrijednost = self.log() if ime ^ PSK.LIME else self.aritm()
            return Pridruživanje(ime, vrijednost)
        elif self >> PSK.VRATI:
            return Vrati(self.log() if self.logička else self.aritm())
        else: raise self.greška()

    def funkcija(self):
        ime = self.pročitaj(PSK.LIME, PSK.AIME)
        self.logička = bool(ime ^ PSK.LIME)
        self.pročitaj(PSK.OTV)
        if self >> PSK.ZATV: parametri = []
        elif self >> {PSK.LIME, PSK.AIME}:
            parametri = [self.zadnji]
            while self >> PSK.ZAREZ:
                parametri.append(self.pročitaj(PSK.LIME, PSK.AIME))
            self.pročitaj(PSK.ZATV)
        else: raise self.greška()
        self.pročitaj(PSK.JEDNAKO)
        return Funkcija(ime, parametri, self.naredba())

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
        manje = bool(self.pročitaj(PSK.JEDNAKO, PSK.MANJE) ^ PSK.MANJE)
        desno = self.aritm()
        return Usporedba(manje, lijevo, desno)

    def poziv(self, ime):
        if ime in self.funkcije: funkcija = self.funkcije[ime]
        else: raise ime.nedeklaracija()
        return Poziv(funkcija, self.argumenti(funkcija.parametri))

    def argumenti(self, parametri):
        arg = []
        prvi = True
        for parametar in parametri:
            self.pročitaj(PSK.OTV if prvi else PSK.ZAREZ)
            prvi = False
            arg.append(self.log() if parametar ^ PSK.LIME else self.aritm())
        self.pročitaj(PSK.ZATV)
        return arg
    
    def aritm(self):
        članovi = [self.član()]
        while self >> {PSK.PLUS, PSK.MINUS}:
            operator = self.zadnji
            dalje = self.član()
            članovi.append(dalje if operator ^ PSK.PLUS else Suprotan(dalje))
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
        print('Program je vratio:', izlazna_vrijednost)
    else: raise SemantičkaGreška('Nema glavne funkcije "program"')


class Funkcija(AST('ime parametri naredba')):
    def pozovi(self, argumenti):
        lokalni = {p.sadržaj: arg for p, arg in zip(self.parametri, argumenti)}
        try: self.naredba.izvrši(lokalni)
        except Povratak as exc: return exc.povratna_vrijednost
        else: raise GreškaIzvođenja('{} nije ništa vratila'.format(self.ime))

class Poziv(AST('funkcija argumenti')):
    """Izraz koji predstavlja funkcijski poziv sa zadanim argumentima."""
    def vrijednost(self, mem):
        argumenti = [argument.vrijednost(mem) for argument in self.argumenti]
        return self.funkcija.pozovi(argumenti)

    def _asdict(self):  # samo za ispis, da se ne ispiše čitava funkcija
        return {'*ime': self.funkcija.ime, 'argumenti': self.argumenti}

class Grananje(AST('uvjet istina naredba inače')):
    def izvrši(self, mem):
        if self.uvjet.vrijednost(mem) == self.istina: self.naredba.izvrši(mem)
        else: self.inače.izvrši(mem)

class Petlja(AST('uvjet istina naredba')):
    def izvrši(self, mem):
        while self.uvjet.vrijednost(mem) == self.istina:
            self.naredba.izvrši(mem)

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime.sadržaj] = self.pridruženo.vrijednost(mem)

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
    def vrijednost(self, mem): return sum(pribrojnik.vrijednost(mem)
                                          for pribrojnik in self.pribrojnici)
    
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


modul = '''\
Identiteta(V) = vrati V  # potrebno zbog dvoznačnosti: u "ako je V (...",
                         # ( se interpretira kao poziv a ne kao blok
                         # "ako je Identiteta(V) (..." nema taj problem
Negacija(V) = ako je V vrati Laž inače vrati Istina
Neparan(x) = (
    N = Laž,
    dok nije x = 0 (
        x = x - 1,
        N = Negacija(N),
    ),
    vrati N
)
'''
suma_faktorijela = PseudokodParser.parsiraj(pseudokod_lexer(modul + '''\
fakt(x) = (  # faktorijel, računamo iterativno (mora biti x>0)
    f = 1,
    dok nije x = 0 (
        f = f*x,
        x = x-1
    ),
    vrati f
)
program() = (  # suma faktorijelâ neparnih brojeva do isključivo 9
    s = 0,
    t = 0,
    dok je t < 9 (
        ako je Neparan(t) s = s + fakt(t),
        t = t + 1
    ),
    vrati s
)
'''))
prikaz(suma_faktorijela, dubina=22)
izvrši(suma_faktorijela)

tablice_istinitosti = PseudokodParser.parsiraj(pseudokod_lexer(modul + '''\
Konjunkcija(P, Q) = ako je P vrati Q inače vrati P
Disjunkcija(P, Q) = ako je P vrati P inače vrati Q
Kondicional(P, Q) = vrati Disjunkcija(Negacija(P), Q)
Bikondicional(P, Q) = vrati Konjunkcija(Kondicional(P, Q), Kondicional(Q, P))
Multiplex(m, P, Q) =  # rudimentarni switch/case
    ako je m = 1 vrati Konjunkcija(P, Q)   inače
    ako je m = 2 vrati Disjunkcija(P, Q)   inače
    ako je m = 3 vrati Kondicional(P, Q)   inače
    ako je m = 4 vrati Bikondicional(P, Q) inače
    ako je m = 5 vrati Negacija(P)         inače
                 vrati Laž

# Iako PSK 'nativno' radi samo s logičkim vrijednostima i cijelim brojevima,
# možemo raditi s raznim drugim tipovima podataka pomoću _kodiranja_.
# Primjer: listu malih brojeva (a,b,...,n) kodiramo u broj 6a8b8...8n9
# (mali brojevi su do 5; 6 i 9 su zagrade, 8 je zarez/separator).
# Naravno, logičke vrijednosti kodiramo kao male brojeve 0 odnosno 1.
# Može se činiti umjetnim, ali zapravo je sveprisutno pri funkcioniranju
# modernih računala: svaki objekt je predstavljen nizom bajtova.

broj(Bool) = ako je Bool vrati 1 inače vrati 0
dodaj(lista, Bool) = (
    bit = broj(Bool),
    lista = lista * 10 + bit,
    lista = lista * 10 + 8,
    vrati lista
)
program(m) = (  # rudimentarni prijenos argumenta preko "komandne linije"
    lista = 6,  # alokacija nove liste: počinje otvorenom zagradom
    b = 0,
    dok je b < 4 (
        Prvi = Negacija(b < 2),  # ekstrakcija bitova od b
        Drugi = Neparan(b),
        Rezultat = Multiplex(m, Prvi, Drugi),
        lista = dodaj(lista, Rezultat),  # lista.append(Rezultat)
        b = b + 1
    ),
    vrati lista + 1  # zatvaranje liste: zadnji 8 postaje zatvorena zagrada 9
)
'''))
print()
prikaz(tablice_istinitosti, 13)
izvrši(tablice_istinitosti, 3)  # poziv iz komandne linije, prijenos m=3

with očekivano(SemantičkaGreška):
    PseudokodParser.parsiraj(pseudokod_lexer('f(x)=() f(x)=()'))

# DZ: dodajte određenu petlju: za ime = izraz .. izraz naredba
# DZ*: dodajte late binding, da se modul i program mogu zasebno kompajlirati
