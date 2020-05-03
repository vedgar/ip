from pj import *
from backend import PristupLog
import pprint


class SQL(enum.Enum):
    SELECT = 'select'
    FROM = 'from'
    CREATE = 'create'
    TABLE = 'table'
    OTVORENA = '('
    ZATVORENA = ')'
    ZVJEZDICA = '*'
    ZAREZ = ','
    TOČKAZAREZ = ';'
    IME = enum.auto()
    BROJ = enum.auto()


def sql_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isalnum():
            lex.zvijezda(str.isalnum)
            if lex.sadržaj.isdigit(): yield lex.token(SQL.BROJ)
            else: yield lex.literal(SQL.IME, case=False)
        elif znak == '-':
            lex.pročitaj('-')
            while lex.čitaj() != '\n': pass
        else: yield lex.literal(SQL)


### Beskontekstna gramatika:
# start -> naredba start | naredba
# naredba -> select TOČKAZAREZ | create TOČKAZAREZ
# select -> SELECT ZVJEZDICA FROM IME | SELECT stupci FROM IME
# stupci -> IME ZAREZ stupci | IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac ZAREZ spec_stupci | spec_stupac
# spec_stupac -> IME IME | IME IME OTVORENA BROJ ZATVORENA

### Apstraktna sintaksna stabla:
# Skripta: naredbe:[Create|Select]
# Select: tablica:IME, stupci:[IME]?
# Create: tablica:IME, specifikacije:[Stupac]
# Stupac: ime:IME, tip:IME, veličina:BROJ?


class SQLParser(Parser):
    def select(self):
        self.pročitaj(SQL.SELECT)
        if self >> SQL.ZVJEZDICA: stupci = nenavedeno
        elif self >= SQL.IME:
            prvi = self.pročitaj(SQL.IME)
            stupci = [prvi]
            while self >> SQL.ZAREZ:
                sljedeći = self.pročitaj(SQL.IME)
                stupci.append(sljedeći)
        else: raise self.greška()
        self.pročitaj(SQL.FROM)
        tablica = self.pročitaj(SQL.IME)
        return Select(tablica, stupci)

    def spec_stupac(self):
        ime = self.pročitaj(SQL.IME)
        tip = self.pročitaj(SQL.IME)
        if self >= SQL.OTVORENA:
            self.pročitaj(SQL.OTVORENA)
            veličina = self.pročitaj(SQL.BROJ)
            self.pročitaj(SQL.ZATVORENA)
        else: veličina = nenavedeno
        return Stupac(ime, tip, veličina)

    def create(self):
        self.pročitaj(SQL.CREATE)
        self.pročitaj(SQL.TABLE)
        tablica = self.pročitaj(SQL.IME)
        self.pročitaj(SQL.OTVORENA)
        prvi = self.spec_stupac()
        stupci = [prvi]
        while self >> SQL.ZAREZ:
            sljedeći = self.spec_stupac()
            stupci.append(sljedeći)
        self.pročitaj(SQL.ZATVORENA)
        return Create(tablica, stupci)

    def naredba(self):
        if self >= SQL.SELECT: rezultat = self.select()
        elif self >= SQL.CREATE: rezultat = self.create()
        else: raise self.greška()
        self.pročitaj(SQL.TOČKAZAREZ)
        return rezultat

    def start(self):
        prva = self.naredba()
        naredbe = [prva]
        while self >= {SQL.CREATE, SQL.SELECT}:
            sljedeća = self.naredba()
            naredbe.append(sljedeća)
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
        t = imena[self.tablica.sadržaj] = {}
        for stupac in self.specifikacije:
            t[stupac.ime.sadržaj] = PristupLog(stupac.tip)
        
class Select(AST('tablica stupci')):
    """SELECT naredba."""
    def razriješi(self, imena):
        t = pogledaj(imena, self.tablica)
        if self.stupci is nenavedeno:
            for log in t.values(): log.pristupi()
        else:
            for c in self.stupci: pogledaj(t, c).pristupi()

class Stupac(AST('ime tip veličina')):
    """Specifikacija stupca u tablici."""


def za_indeks(skripta):
    logovi = skripta.razriješi()
    for tablica, stupaclogovi in logovi.items():
        pristupi = {}
        for stupac, stupaclog in stupaclogovi.items():
            pristupi[stupac] = stupaclog.pristup
        prosjek = sum(pristupi.values()) / len(pristupi)
        for stupac, p in pristupi.items():
            if p > prosjek: yield tablica, stupac


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
        CREATE TABLE 2E (s t, s2 t); CREATE TABLE 2E3 (s t);
        SELECT*FROM 2E; -- između simbola i riječi ne mora ići razmak
        SELECT s FROM 2E; -- ali između dvije riječi mora, naravno
        SELECT Name, Married FROM Persons;
        SELECT Name from Persons;
    '''))
    prikaz(skripta, 4)
    pprint.pprint(skripta.razriješi())
    for i, (tablica, stupac) in enumerate(za_indeks(skripta), 1):
        print('CREATE INDEX idx{} ON {} ({});'.format(i, tablica, stupac))

    with očekivano(SemantičkaGreška):
        SQLParser.parsiraj(sql_lex('SELECT * FROM nema;')).razriješi()
    with očekivano(SemantičkaGreška):
        sql = 'CREATE TABLE mala (stupac int); SELECT drugi FROM mala;'
        SQLParser.parsiraj(sql_lex(sql)).razriješi()
    with očekivano(SintaksnaGreška):
        SQLParser.parsiraj(sql_lex('CREATE TABLE 2000 (s t);'))
