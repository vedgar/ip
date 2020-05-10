"""Jednostavni SQL parser, samo za nizove CREATE i SELECT naredbi.

Ovaj fragment SQLa je zapravo regularan -- nigdje nema ugnježđivanja!
Semantički analizator u obliku name resolvera:
    provjerava jesu li svi selektirani stupci prisutni, te broji pristupe.
Na dnu je lista ideja za dalji razvoj.
"""


from pj import *
from backend import PristupLog
import pprint


class SQL(enum.Enum):
    class IME(Token): pass
    class BROJ(Token): pass
    SELECT, FROM, CREATE, TABLE = 'select', 'from', 'create', 'table'
    OTVORENA, ZATVORENA, ZVJEZDICA, ZAREZ, TOČKAZAREZ = '()*,;'


def sql_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(SQL.BROJ)
        elif znak == '-':
            lex.pročitaj('-')
            lex.pročitaj_do('\n')
            lex.zanemari()
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.literal(SQL.IME, case=False)
        else: yield lex.literal(SQL)


### Beskontekstna gramatika:
# start -> naredba | naredba start
# naredba -> ( select | create ) TOČKAZAREZ
# select -> SELECT ( ZVJEZDICA | stupci ) FROM IME
# stupci -> IME ZAREZ stupci | IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac ZAREZ spec_stupci | spec_stupac
# spec_stupac -> IME IME (OTVORENA BROJ ZATVORENA)?

### Apstraktna sintaksna stabla:
# Skripta: naredbe - niz SQL naredbi, svaka završava znakom ';'
# Create: tablica, specifikacije - CREATE TABLE naredba
# Select: tablica, stupci - SELECT naredba; stupci == nenavedeno za SELECT *
# Stupac: ime, tip, veličina - specifikacija stupca u tablici (za Create)


class SQLParser(Parser):
    def select(self):
        if self >> SQL.ZVJEZDICA: stupci = nenavedeno
        elif self >> SQL.IME:
            stupci = [self.zadnji]
            while self >> SQL.ZAREZ: stupci.append(self.pročitaj(SQL.IME))
        else: raise self.greška()
        self.pročitaj(SQL.FROM)        
        return Select(self.pročitaj(SQL.IME), stupci)

    def spec_stupac(self):
        ime, tip = self.pročitaj(SQL.IME), self.pročitaj(SQL.IME)
        if self >> SQL.OTVORENA:
            veličina = self.pročitaj(SQL.BROJ)
            self.pročitaj(SQL.ZATVORENA)
        else: veličina = nenavedeno
        return Stupac(ime, tip, veličina)

    def create(self):
        self.pročitaj(SQL.TABLE)
        tablica = self.pročitaj(SQL.IME)
        self.pročitaj(SQL.OTVORENA)
        stupci = [self.spec_stupac()]
        while self >> SQL.ZAREZ: stupci.append(self.spec_stupac())
        self.pročitaj(SQL.ZATVORENA)
        return Create(tablica, stupci)

    def naredba(self):
        if self >> SQL.SELECT: rezultat = self.select()
        elif self >> SQL.CREATE: rezultat = self.create()
        else: raise self.greška()
        self.pročitaj(SQL.TOČKAZAREZ)
        return rezultat

    def start(self):
        naredbe = [self.naredba()]
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Skripta(naredbe)


class Skripta(AST('naredbe')):
    """Niz SQL naredbi, svaka završava znakom ';'."""
    def razriješi(self):
        imena = {}
        for naredba in self.naredbe: naredba.razriješi(imena)
        return imena

class Create(AST('tablica specifikacije')):
    """CREATE TABLE naredba."""
    def razriješi(self, imena):
        tb = imena[self.tablica.sadržaj] = {}
        for stupac in self.specifikacije:
            tb[stupac.ime.sadržaj] = PristupLog(stupac.tip)
        
class Select(AST('tablica stupci')):
    """SELECT naredba."""
    def razriješi(self, imena):
        tn = self.tablica.sadržaj
        if tn not in imena: raise self.tablica.nedeklaracija('nema tablice')
        tb = imena[tn]
        if self.stupci is nenavedeno:
            for sl in tb.values(): sl.pristupi()
        else:
            for st in self.stupci:
                sn = st.sadržaj
                if sn not in tb:
                    raise st.nedeklaracija('stupca nema u {}'.format(tn))
                tb[sn].pristupi()

class Stupac(AST('ime tip veličina')): """Specifikacija stupca u tablici."""


if __name__ == '__main__':
    skripta = SQLParser.parsiraj(sql_lex('''\
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
            CREATE TABLE Trivial (ID void(0));  -- još jedna tablica
            SELECT*FROM Trivial;  -- između simbola i riječi ne mora ići razmak
            SELECT Name, Married FROM Persons;
            SELECT Name from Persons;
    '''))
    prikaz(skripta, 4)
    # Skripta(naredbe=[
    #   Create(tablica=IME'Persons', specifikacije=[
    #     Stupac(ime=IME'PersonID', tip=IME'int', veličina=nenavedeno), 
    #     Stupac(ime=IME'Name', tip=IME'varchar', veličina=BROJ'255'),
    #     Stupac(ime=IME'Birthday', tip=IME'date', veličina=nenavedeno),
    #     Stupac(ime=IME'Married', tip=IME'bool', veličina=nenavedeno),
    #     Stupac(ime=IME'City', tip=IME'varchar', veličina=BROJ'9')
    #   ]),
    #   Select(tablica=IME'Persons', stupci=[IME'Name', IME'City']),
    #   Select(tablica=IME'Persons', stupci=nenavedeno),
    #   Create(tablica=IME'Trivial', specifikacije=
    #     [Stupac(ime=IME'ID', tip=IME'void', veličina=BROJ'0')]),
    #   Select(tablica=IME'Trivial', stupci=nenavedeno),
    #   Select(tablica=IME'Persons', stupci=[IME'Name', IME'Married']),
    #   Select(tablica=IME'Persons', stupci=[IME'Name'])
    # ])

    #raise SystemExit
    pprint.pprint(skripta.razriješi())

# ideje za dalji razvoj:
    # PristupLog.pristup umjesto samog broja može biti lista brojeva linija \
    # skripte u kojima počinju SELECT naredbe koje pristupaju pojedinom stupcu
    # za_indeks(skripta): lista natprosječno dohvaćivanih tablica/stupaca
    # optimizacija: brisanje iz CREATE stupaca kojima nismo uopće pristupili
    # implementirati INSERT INTO, da možemo doista nešto i raditi s podacima
    # povratni tip za SELECT (npr. (varchar(255), bool) za predzadnji)
    # interaktivni način rada (online - naredbu po naredbu analizirati)
