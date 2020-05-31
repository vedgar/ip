"""Jednostavni parser SQLa, samo za nizove naredbi CREATE i SELECT.

Ovaj fragment SQLa je zapravo regularan -- nigdje nema ugnježđivanja!
Napisan je semantički analizator u obliku name resolvera:
    provjerava jesu li svi selektirani stupci prisutni, te broji pristupe."""


from vepar import *


class T(TipoviTokena):
    SELECT, FROM, CREATE, TABLE = 'select', 'from', 'create', 'table'
    OTVORENA, ZATVORENA, ZVJEZDICA, ZAREZ, TOČKAZAREZ = '()*,;'
    IME, BROJ = TipTokena(), TipTokena()


### Beskontekstna gramatika:
# start -> naredba start | naredba
# naredba -> select TOČKAZAREZ | create TOČKAZAREZ
# select -> SELECT ZVJEZDICA FROM IME | SELECT stupci FROM IME
# stupci -> IME ZAREZ stupci | IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac ZAREZ spec_stupci | spec_stupac
# spec_stupac -> IME IME | IME IME OTVORENA BROJ ZATVORENA

### Apstraktna sintaksna stabla:
# Skripta: naredbe:[naredba]
# naredba: Select: tablica:IME stupci:[IME]?
#          Create: tablica:IME specifikacije:[Stupac]
# Stupac: ime:IME tip:IME veličina:BROJ?


class P(Parser):
    def lexer(lex):
        for znak in lex:
            if znak.isspace(): lex.zanemari()
            elif znak.isalnum():
                lex.zvijezda(str.isalnum)
                if lex.sadržaj.isdigit(): yield lex.token(T.BROJ)
                else: yield lex.literal(T.IME, case=False)
            elif znak == '-':
                lex.pročitaj('-'), lex.pročitaj_do('\n'), lex.zanemari()
            else: yield lex.literal(T)

    def start(self):
        naredbe = [self.naredba()]
        while not self > KRAJ: naredbe.append(self.naredba())
        return Skripta(naredbe)

    def select(self):
        self >> T.SELECT
        if self >= T.ZVJEZDICA: stupci = nenavedeno
        elif stupac := self >> T.IME:
            stupci = [stupac]
            while self >= T.ZAREZ: stupci.append(self >> T.IME)
        self >> T.FROM
        return Select(self >> T.IME, stupci)

    def spec_stupac(self):
        ime, tip = self >> T.IME, self >> T.IME
        if self >= T.OTVORENA:
            veličina = self >> T.BROJ
            self >> T.ZATVORENA
        else: veličina = nenavedeno
        return Stupac(ime, tip, veličina)

    def create(self):
        self >> T.CREATE, self >> T.TABLE
        tablica = self >> T.IME
        self >> T.OTVORENA
        stupci = [self.spec_stupac()]
        while self >= T.ZAREZ: stupci.append(self.spec_stupac())
        self >> T.ZATVORENA
        return Create(tablica, stupci)

    def naredba(self):
        if self > T.SELECT: rezultat = self.select()
        elif self > T.CREATE: rezultat = self.create()
        else: raise self.greška()
        self >> T.TOČKAZAREZ
        return rezultat


class Skripta(AST('naredbe')):
    """Niz naredbi SQLa, svaka završava točkazarezom."""
    def razriješi(self):
        imena = Memorija(redefinicija=False)
        for naredba in self.naredbe: naredba.razriješi(imena)
        return imena

class Create(AST('tablica specifikacije')):
    """Naredba CREATE TABLE."""
    def razriješi(self, imena):
        t = imena[self.tablica] = Memorija(redefinicija=True)
        for stupac in self.specifikacije:
            t[stupac.ime] = 0
        
class Select(AST('tablica stupci')):
    """Naredba SELECT."""
    def razriješi(self, imena):
        t = imena[self.tablica]
        dohvaćeni = self.stupci
        if dohvaćeni is nenavedeno: dohvaćeni = t.imena()
        for stupac in dohvaćeni: t[stupac] += 1

class Stupac(AST('ime tip veličina')): """Specifikacija stupca u tablici."""


def za_indeks(skripta):
    for tablica, log in skripta.razriješi():
        ukupni = brojač = 0
        for stupac, pristup in log:
            ukupni += pristup
            brojač += 1
        if not brojač: continue
        prosjek = ukupni / brojač
        for stupac, pristup in log:
            if pristup > prosjek: yield tablica, stupac


skripta = P('''\
    CREATE TABLE Persons
    (
        PersonID int,
        Name varchar(255),  -- neki stupci imaju zadanu veličinu
        Birthday date,      -- a neki nemaju...
        Married bool,
        City varchar(9)     -- zadnji nema zarez!
    );  -- Sada krenimo nešto selektirati
    SELECT Name, City FROM Persons;
    SELECT * FROM Persons;
    CREATE TABLE 2E3 (s t, s2 t);
    SELECT*FROM 2E3; -- između simbola i riječi ne mora ići razmak
    SELECT s FROM 2E3; -- ali između dvije riječi mora, naravno
    SELECT Name, Married FROM Persons;
    SELECT Name from Persons;
''')
prikaz(skripta, 4)
for tablica, log in skripta.razriješi():
    print('Tablica', tablica, '- stupci:')
    for stupac, pristup in log: print('\t', stupac, pristup)
i = 1
for tablica, stupac in za_indeks(skripta):
    t = tablica.sadržaj
    s = stupac.sadržaj
    print('CREATE INDEX idx{} ON {} ({});'.format(i, t, s))
    i += 1

with očekivano(SemantičkaGreška): P('SELECT * FROM nema;').razriješi()
with očekivano(SemantičkaGreška):
    P('CREATE TABLE mala (stupac int); SELECT drugi FROM mala;').razriješi()
with očekivano(SintaksnaGreška): P('CREATE TABLE 2000 (s t);')

# ideje za dalji razvoj:
# * pristup stupcu umjesto samog broja može biti lista brojeva linija \
#     skripte u kojima počinju SELECTovi koji pristupaju pojedinom stupcu
# * optimizacija: brisanje iz CREATE stupaca kojima nismo uopće pristupili
# * implementirati INSERT INTO, da možemo doista nešto i raditi s podacima
# * povratni tip za SELECT (npr. (varchar(255), bool) za predzadnji)
# * interaktivni način rada (online - analizirati naredbu po naredbu)
