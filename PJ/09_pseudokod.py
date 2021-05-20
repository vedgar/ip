"""Interpreter za pseudokod, s funkcijskim pozivima i dva tipa podataka.

Podržane naredbe:
    ako je Uvjet naredba inače naredba      ime = izraz
    ako je Uvjet naredba                    Ime = Uvjet
    ako nije Uvjet naredba                  vrati izraz
    dok je Uvjet naredba                    vrati Uvjet
    dok nije Uvjet naredba                  (naredba1, naredba2, ...)
Podržani aritmetički izrazi:            Podržani logički uvjeti:
    cijeli_broj                             Istina
    ime                                     Laž
    ime(argumenti)                          Ime
    izraz + izraz                           Ime(argumenti)
    izraz - izraz                           Uvjet Ili Uvjet
    izraz * izraz                           izraz < izraz
    -izraz                                  izraz = izraz
    (izraz)                                 (Uvjet)

Program se sastoji od jedne ili više deklaracija funkcija, s ili bez parametara.
    Jedna od njih mora biti program(parametri), od nje počinje izvršavanje.
Tipovi varijabli (i povratni tipovi funkcija) se reprezentiraju leksički:
    * veliko početno slovo označava logički tip (u Pythonu bool)
    * malo početno slovo označava aritmetički tip (u Pythonu int)
Minimalni kontekst je potreban da bismo zapamtili jesmo li trenutno u definiciji
    aritmetičke ili logičke funkcije, kako bi naredba "vrati" znala što očekuje.
Dozvoljeni su i (ne uzajamno) rekurzivni pozivi, tako da se za vrijeme 
    parsiranja i izvršavanja prati u kojoj smo funkciji."""


from vepar import *
from math import prod


class T(TipoviTokena):
    AKO, DOK, INAČE, VRATI = 'ako', 'dok', 'inače', 'vrati'
    JE, NIJE, ILI = 'je', 'nije', 'Ili'
    OTV, ZATV, ZAREZ, JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '(),=<+-*'

    class AIME(Token):
        def vrijednost(self, mem, unutar): return mem[self]

    class LIME(AIME): pass

    class BROJ(Token):
        def vrijednost(self, mem, unutar): return int(self.sadržaj)

    class ISTINA(Token):
        literal = 'Istina'
        def vrijednost(self, mem, unutar): return True

    class LAŽ(Token):
        literal = 'Laž'
        def vrijednost(self, mem, unutar): return False


def pseudokod_lexer(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.islower():
            lex.zvijezda(str.isalnum)
            yield lex.literal(T.AIME)
        elif znak.isupper():
            lex.zvijezda(str.isalnum)
            yield lex.literal(T.LIME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '#':
            lex.pročitaj_do('\n')
            lex.zanemari()
        else: yield lex.literal(T)


### ne sasvim BKG
# program -> funkcija | funkcija program
# funkcija -> ime OTV parametri? ZATV JEDNAKO naredba
# parametri -> ime | IME ZAREZ parametri
# ime -> AIME | LIME
# naredba -> pridruži | OTV ZATV | OTV naredbe ZATV | VRATI argument
#            | DOK JE log naredba | DOK NIJE log naredba
#            | AKO JE log naredba | AKO NIJE log naredba
#            | AKO JE log naredba INAČE naredba
# naredbe -> naredba | naredba ZAREZ naredbe
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm MANJE aritm | aritm JEDNAKO aritm 
#             | ISTINA | LAŽ | LIME | LIME poziv | OTV log ZATV
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor
# faktor -> BROJ | AIME | AIME poziv | OTV aritm ZATV | MINUS faktor
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argument ZAREZ argumenti
# argument -> aritm |! log  [KONTEKST!]

class P(Parser):
    def program(self):
        self.funkcije = Memorija(redefinicija=False)
        while not self > KRAJ:
            funkcija = self.funkcija()
            self.funkcije[funkcija.ime] = funkcija
        return self.funkcije

    def ime(self): return self >> {T.AIME, T.LIME}

    def naredba(self):
        if self > T.AKO: return self.grananje()
        elif self > T.DOK: return self.petlja()
        elif self > T.OTV: return self.blok()
        elif self >= T.VRATI: return Vrati(self.tipa(self.imef))
        else:
            ime = self.ime()
            self >> T.JEDNAKO
            return Pridruživanje(ime, self.tipa(ime))

    def blok(self):
        self >> T.OTV
        if self >= T.ZATV: return Blok([])
        n = [self.naredba()]
        while self >= T.ZAREZ and not self > T.ZATV: n.append(self.naredba())
        self >> T.ZATV
        return Blok.ili_samo(n)

    def petlja(self):
        self >> T.DOK
        return Petlja(self >> {T.JE, T.NIJE}, self.log(), self.naredba())

    def grananje(self):
        self >> T.AKO
        je = self > T.JE
        atributi = self >> {T.JE, T.NIJE}, self.log(), self.naredba()
        if je and self >= T.INAČE: inače = self.naredba()
        else: inače = Blok([])
        return Grananje(*atributi, inače)

    def funkcija(self):
        atributi = self.imef, self.parametrif = self.ime(), self.parametri()
        self >> T.JEDNAKO
        return Funkcija(*atributi, self.naredba())

    def parametri(self):
        self >> T.OTV
        if self >= T.ZATV: return []
        param = [self.ime()]
        while self >= T.ZAREZ: param.append(self.ime())
        self >> T.ZATV
        return param

    def log(self):
        disjunkti = [self.disjunkt()]
        while self >= T.ILI: disjunkti.append(self.disjunkt())
        return Disjunkcija.ili_samo(disjunkti)

    def disjunkt(self):
        if log := self >= {T.ISTINA,T.LAŽ,T.LIME}: return self.možda_poziv(log)
        return Usporedba(self.aritm(), self>>{T.JEDNAKO,T.MANJE}, self.aritm())

    def možda_poziv(self, ime):
        if ime in self.funkcije:
            funkcija = self.funkcije[ime]
            return Poziv(funkcija, self.argumenti(funkcija.parametri))
        elif ime == self.imef:
            return Poziv(nenavedeno, self.argumenti(self.parametrif))
        else: return ime

    def argumenti(self, parametri):
        arg = []
        self >> T.OTV
        for i, parametar in enumerate(parametri):
            if i: self >> T.ZAREZ
            arg.append(self.tipa(parametar))
        self >> T.ZATV
        return arg
    
    def tipa(self, ime):
        if ime ^ T.AIME: return self.aritm()
        elif ime ^ T.LIME: return self.log()
        else: assert False, f'Nepoznat tip od {ime}'
        
    def aritm(self):
        članovi = [self.član()]
        while True:
            if self >= T.PLUS: članovi.append(self.član())
            elif self >= T.MINUS: članovi.append(Suprotan(self.član()))
            else: return Zbroj.ili_samo(članovi)

    def član(self):
        faktori = [self.faktor()]
        while self >= T.ZVJEZDICA: faktori.append(self.faktor())
        return Umnožak.ili_samo(faktori)

    def faktor(self):
        if self >= T.MINUS: return Suprotan(self.faktor())
        elif aritm := self >= T.AIME: return self.možda_poziv(aritm)
        elif self >= T.OTV:
            u_zagradi = self.aritm()
            self >> T.ZATV
            return u_zagradi
        else: return self >> T.BROJ

    start = program
    lexer = pseudokod_lexer


def izvrši(funkcije, *argv):
    print('Program je vratio:', funkcije['program'].pozovi(argv))


### AST
# Funkcija: ime:IME parametri:[IME] naredba:naredba
# naredba: Grananje: istinitost:JE|NIJE uvjet:log onda:naredba inače:naredba
#          Petlja: istinitost:JE|NIJE uvjet:log tijelo:naredba
#          Blok: naredbe:[naredba]
#          Pridruživanje: ime:IME pridruženo:izraz
#          Vrati: što:izraz
# izraz: log: Disjunkcija: disjunkti:[log]
#             Usporedba: lijevo:aritm relacija:MANJE|JEDNAKO desno:aritm
#        aritm: Zbroj: pribrojnici:[aritm]
#               Suprotan: od:aritm
#               Umnožak: faktori:[aritm]
#        Poziv: funkcija:Funkcija argumenti:[izraz]

class Funkcija(AST('ime parametri naredba')):
    def pozovi(self, argumenti):
        lokalni = Memorija(dict(zip(self.parametri, argumenti)))
        try: self.naredba.izvrši(mem=lokalni, unutar=self)
        except Povratak as exc: return exc.preneseno
        else: raise GreškaIzvođenja(f'{self.ime} nije ništa vratila')

class Poziv(AST('funkcija argumenti')):
    def vrijednost(self, mem, unutar):
        pozvana = self.funkcija
        if pozvana is nenavedeno: pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in self.argumenti]
        return pozvana.pozovi(argumenti)

    def _asdict(self):  # samo za ispis, da se ne ispiše čitava funkcija
        za_ispis = {'argumenti': self.argumenti}
        if self.funkcija is nenavedeno: za_ispis['*rekurzivni'] = True
        else: za_ispis['*ime'] = self.funkcija.ime
        return za_ispis

def ispunjen(ast, mem, unutar):
    traženo = {T.JE: True, T.NIJE: False}[ast.istinitost.tip]
    return ast.uvjet.vrijednost(mem, unutar) == traženo

class Grananje(AST('istinitost uvjet onda inače')):
    def izvrši(self, mem, unutar):
        if ispunjen(self, mem, unutar): self.onda.izvrši(mem, unutar)
        else: self.inače.izvrši(mem, unutar)

class Petlja(AST('istinitost uvjet tijelo')):
    def izvrši(self, mem, unutar):
        while ispunjen(self, mem, unutar): self.tijelo.izvrši(mem, unutar)

class Blok(AST('naredbe')):
    def izvrši(self, mem, unutar):
        for naredba in self.naredbe: naredba.izvrši(mem, unutar)

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem, unutar):
        mem[self.ime] = self.pridruženo.vrijednost(mem, unutar)

class Vrati(AST('što')):
    def izvrši(self, mem, unutar):
        raise Povratak(self.što.vrijednost(mem, unutar))

class Disjunkcija(AST('disjunkti')):
    def vrijednost(self, mem, unutar):
        return any(disjunkt.vrijednost(mem, unutar)
                for disjunkt in self.disjunkti)
    
class Usporedba(AST('lijevo relacija desno')):
    def vrijednost(self, mem, unutar):
        l = self.lijevo.vrijednost(mem, unutar)
        d = self.desno.vrijednost(mem, unutar)
        if self.relacija ^ T.JEDNAKO: return l == d
        elif self.relacija ^ T.MANJE: return l < d
        else: assert False, f'Nepoznata relacija {self.relacija}'

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem, unutar):
        return sum(p.vrijednost(mem, unutar) for p in self.pribrojnici)
    
class Suprotan(AST('od')):
    def vrijednost(self, mem, unutar): return -self.od.vrijednost(mem, unutar)
    
class Umnožak(AST('faktori')):
    def vrijednost(self, mem, unutar):
        return math.prod(f.vrijednost(mem, unutar) for f in self.faktori)

class Povratak(NelokalnaKontrolaToka): """Signal koji šalje naredba vrati."""


proba = P('program() = ako je Istina vrati 1 inače vrati 2')
prikaz(proba, 5)
izvrši(proba)

with SemantičkaGreška: P('f(x)=() f(x)=()')
with SintaksnaGreška:
    P('f(x) = vrati 7    program() = vrati f(Laž)')
with SintaksnaGreška: izvrši(P('program() = vrati2'))
with LeksičkaGreška: P('program() = vrati 007')

modul = '''\
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

suma_faktorijela = P(modul + '''\
fakt(x) = (
    f = 1,
    dok nije x = 0 (
        f = f*x,
        x = x-1
    ),
    vrati f
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
''')
prikaz(suma_faktorijela)
izvrši(suma_faktorijela)

tablice_istinitosti = P(modul + '''\
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
broj(Bool) = ako je Bool vrati 1 inače vrati 0
dodaj(lista, Bool) = (
    bit = broj(Bool),
    lista = lista * 10 + bit,
    lista = lista * 10 + 8,
    vrati lista
)
program(m) = (
    lista = 6,
    b = 0,
    dok je b < 4 (
        Prvi = Negacija(b < 2),
        Drugi = Neparan(b),
        Rezultat = Multiplex(m, Prvi, Drugi),
        lista = dodaj(lista, Rezultat),
        b = b + 1
    ),
    vrati lista + 1
)
''')
print()
prikaz(tablice_istinitosti)
izvrši(tablice_istinitosti, 3)  # poziv iz komandne linije, prijenos m=3
print()

rekurzivna = P('''\
    fakt(n) = ako je n = 0 vrati 1 inače vrati n*fakt(n-1)
    program() = vrati fakt(7)
''')
prikaz(rekurzivna)
izvrši(rekurzivna)


# DZ: dodajte određenu petlju: za ime = izraz .. izraz naredba
# DZ*: dodajte late binding, da se modul i program mogu zasebno kompajlirati
