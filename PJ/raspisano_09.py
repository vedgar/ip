from pj import *


class PK(enum.Enum):
    AKO = 'ako'
    DOK = 'dok'
    INAČE = 'inače'
    VRATI = 'vrati'
    JE = 'je'
    NIJE = 'nije'
    ILI = 'Ili'
    OTV = '('
    ZATV = ')'
    ZAREZ = ','
    JEDNAKO = '='
    MANJE = '<'
    PLUS = '+'
    MINUS = '-'
    ZVJEZDICA = '*'

    class AIME(Token):
        def vrijednost(self, mem): return pogledaj(mem, self)

    class LIME(AIME): pass

    class BROJ(Token):
        def vrijednost(self, _): return int(self.sadržaj)

    class ISTINA(Token):
        literal = 'Istina'
        def vrijednost(self, _): return True

    class LAŽ(Token):
        literal = 'Laž'
        def vrijednost(self, _): return False


def pseudokod_lexer(program):
    lex = Tokenizer(program)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.islower():
            lex.zvijezda(str.isalpha)
            yield lex.literal(PK.AIME)
        elif znak.isupper():
            lex.zvijezda(str.isalpha)
            yield lex.literal(PK.LIME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(PK.BROJ)
        elif znak == '#':
            lex.pročitaj_do('\n')
            lex.zanemari()
        else: yield lex.literal(PK)


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
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | AIME poziv | OTV aritm ZATV
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argument ZAREZ argumenti
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

    def ime(self): return self.pročitaj(PK.AIME, PK.LIME)

    def naredba(self):
        if self >= PK.AKO: return self.grananje()
        elif self >= PK.DOK: return self.petlja()
        elif self >= PK.OTV: return self.blok()
        elif self >> PK.VRATI: 
            vrijednost = self.tipa(self.imef)
            return Vrati(vrijednost)
        else:
            ime = self.ime()
            self.pročitaj(PK.JEDNAKO)
            vrijednost = self.tipa(ime)
            return Pridruživanje(ime, vrijednost)

    def blok(self):
        self.pročitaj(PK.OTV)
        if self >> PK.ZATV: return Blok([])
        else:
            naredbe = [self.naredba()]
            while self >> PK.ZAREZ and not self >= PK.ZATV:
                naredbe.append(self.naredba())
            self.pročitaj(PK.ZATV)
            return Blok.ili_samo(naredbe)

    def petlja(self):
        self.pročitaj(PK.DOK)
        istinitost = self.pročitaj(PK.JE, PK.NIJE)
        uvjet = self.log()
        naredba = self.naredba()
        return Petlja(istinitost, uvjet, naredba)

    def grananje(self):
        self.pročitaj(PK.AKO)
        istinitost = self.pročitaj(PK.JE, PK.NIJE)
        uvjet = self.log()
        naredba = self.naredba()
        if istinitost ^ PK.JE and self >> PK.INAČE: inače = self.naredba()
        else: inače = Blok([])
        return Grananje(istinitost, uvjet, naredba, inače)

    def funkcija(self):
        self.imef = ime = self.pročitaj(PK.LIME, PK.AIME)
        self.pročitaj(PK.OTV)
        if self >> PK.ZATV: parametri = []
        elif self >> {PK.LIME, PK.AIME}:
            parametri = [self.zadnji]
            while self >> PK.ZAREZ:
                parametri.append(self.pročitaj(PK.LIME, PK.AIME))
            self.pročitaj(PK.ZATV)
        else: raise self.greška()
        self.pročitaj(PK.JEDNAKO)
        naredba = self.naredba()
        return Funkcija(ime, parametri, naredba)

    def parametri(self):
        self.pročitaj(PK.OTV)
        if self >> PK.ZATV: return []
        else:
            par = [self.ime()]
            while self >> PK.ZAREZ: par.append(self.ime())
            self.pročitaj(PK.ZATV)
            return par

    def log(self):
        disjunkti = [self.disjunkt()]
        while self >> PK.ILI: disjunkti.append(self.disjunkt())
        return Disjunkcija.ili_samo(disjunkti)

    def disjunkt(self):
        if self >> {PK.ISTINA, PK.LAŽ, PK.LIME}: return self.možda_poziv()
        else:
            lijevo = self.aritm()
            relacija = self.pročitaj(PK.JEDNAKO, PK.MANJE)
            desno = self.aritm()
            return Usporedba(lijevo, relacija, desno)

    def možda_poziv(self):
        ime = self.zadnji
        if ime in self.funkcije:
            funkcija = pogledaj(self.funkcije, ime)
            return Poziv(funkcija, self.argumenti(funkcija.parametri))
        else: return ime

    def argumenti(self, parametri):
        arg = []
        self.pročitaj(PK.OTV)
        for i, parametar in enumerate(parametri):
            if i: self.pročitaj(PK.ZAREZ)
            arg.append(self.tipa(parametar))
        self.pročitaj(PK.ZATV)
        return arg
    
    def tipa(self, ime):
        if ime ^ PK.AIME: return self.aritm()
        elif ime ^ PK.LIME: return self.log()
        else: assert False, 'Nepoznat tip od {}'.format(ime)
        
    def aritm(self):
        prvi = self.član()
        članovi = [prvi]
        while True:
            if self >> PK.PLUS:
                sljedeći = self.član()
                članovi.append(sljedeći)
            elif self >> PK.MINUS:
                sljedeći = self.član()
                članovi.append(Suprotan(sljedeći))
            else: return Zbroj.ili_samo(članovi)

    def član(self):
        if self >> PK.MINUS: return Suprotan(self.faktor())
        faktori = [self.faktor()]
        while self >> PK.ZVJEZDICA: faktori.append(self.faktor())
        return Umnožak.ili_samo(faktori)

    def faktor(self):
        if self >> {PK.BROJ, PK.AIME}: return self.možda_poziv()
        else:
            self.pročitaj(PK.OTV)
            u_zagradi = self.aritm()
            self.pročitaj(PK.ZATV)
            return u_zagradi

    start = program


def izvrši(funkcije, *argv):
    program = Token(PK.AIME, 'program')
    if program in funkcije:
        izlazna_vrijednost = funkcije[program].pozovi(argv)
        print('Program je vratio:', izlazna_vrijednost)
    else: raise SemantičkaGreška('Nema glavne funkcije "program"')


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
        lokalni = dict(zip(self.parametri, argumenti))
        try: self.naredba.izvrši(lokalni)
        except Povratak as exc: return exc.preneseno
        else: raise GreškaIzvođenja('{} nije ništa vratila'.format(self.ime))

class Poziv(AST('funkcija argumenti')):
    def vrijednost(self, mem):
        argumenti = [argument.vrijednost(mem) for argument in self.argumenti]
        return self.funkcija.pozovi(argumenti)

    def _asdict(self):  # samo za ispis, da se ne ispiše čitava funkcija
        return {'*ime': self.funkcija.ime, 'argumenti': self.argumenti}

def ispunjen(ast, mem):
    if ast.istinitost ^ PK.JE: traženo = True
    elif ast.istinitost ^ PK.NIJE: traženo = False
    else: assert False, 'Nema trećeg.'
    return ast.uvjet.vrijednost(mem) == traženo

class Grananje(AST('istinitost uvjet onda inače')):
    def izvrši(self, mem):
        if ispunjen(self, mem): self.onda.izvrši(mem)
        else: self.inače.izvrši(mem)

class Petlja(AST('istinitost uvjet tijelo')):
    def izvrši(self, mem):
        while ispunjen(self, mem): self.tijelo.izvrši(mem)

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime] = self.pridruženo.vrijednost(mem)

class Vrati(AST('što')):
    def izvrši(self, mem): raise Povratak(self.što.vrijednost(mem))

class Disjunkcija(AST('disjunkti')):
    def vrijednost(self, mem):
        return any(disjunkt.vrijednost(mem) for disjunkt in self.disjunkti)
    
class Usporedba(AST('lijevo relacija desno')):
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        if self.relacija ^ PK.JEDNAKO: return l == d
        elif self.relacija ^ PK.MANJE: return l < d
        else: assert False, 'Nepoznata relacija {}'.format(self.relacija)

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

class Povratak(NelokalnaKontrolaToka): pass


proba = PseudokodParser.parsiraj(pseudokod_lexer(
    'program()= ako je Istina vrati 1 inače vrati 2'))
prikaz(proba, 5)
izvrši(proba)

with očekivano(SemantičkaGreška):
    PseudokodParser.parsiraj(pseudokod_lexer('f(x)=() f(x)=()'))
with očekivano(SintaksnaGreška):
    PseudokodParser.parsiraj(pseudokod_lexer(
        'f(x) = vrati 7    program() = vrati f(Laž)'))

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

suma_faktorijela = PseudokodParser.parsiraj(pseudokod_lexer(modul + '''\
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
'''))
print()
prikaz(tablice_istinitosti, 13)
izvrši(tablice_istinitosti, 3)  # poziv iz komandne linije, prijenos m=3

# DZ: dodajte određenu petlju: za ime = izraz .. izraz naredba
# DZ*: dodajte late binding, da se modul i program mogu zasebno kompajlirati
