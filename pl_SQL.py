from plutil import *
import pprint


class SQL(enum.Enum):
    IME = 'NekoIme'
    ZVJEZDICA = '*'
    ZAREZ = ','
    SELECT = 'SELECT'
    FROM = 'FROM'
    CREATE = 'CREATE'
    TABLE = 'TABLE'
    OTVORENA = '('
    ZATVORENA = ')'
    BROJ = 123
    TOČKAZAREZ = ';'
    KOMENTAR = '--'


def sql_lex(kôd):
    lex = Tokenizer(kôd)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace():
            lex.zvijezda(str.isspace)
            lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(SQL.BROJ)
        elif znak == '-':
            lex.očekuj('-')
            lex.zvijezda('\n'.__ne__)
            lex.očekuj('\n')
            lex.token(SQL.KOMENTAR)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)  # str.isidentifier (uključivo _)
            yield lex.token(ključna_riječ(SQL, lex.sadržaj.upper()) or SQL.IME)
        else: yield lex.token(operator(SQL, znak) or lex.greška())


### Beskontekstna gramatika:
# skripta -> naredba | naredba skripta
# naredba -> ( select | create ) TOČKAZAREZ
# select -> SELECT ( ZVJEZDICA | stupci ) FROM IME
# stupci -> IME ZAREZ stupci | IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac ZAREZ spec_stupci | spec_stupac
# spec_stupac -> IME IME | IME IME OTVORENA BROJ ZATVORENA

### Apstraktna sintaksna stabla:
# Skripta: naredbe - niz SQL naredbi, svaka završava znakom ';'
# Create: tablica, specifikacije - CREATE TABLE naredba
# Select: tablica, sve, stupci - SELECT naredba
# Stupac: ime, tip, veličina - specifikacija stupca u tablici (za Create)

class SQLParser(Parser):
    def select(self):
        self.pročitaj(SQL.SELECT)
        sve = self.granaj(SQL.ZVJEZDICA, SQL.IME) ** SQL.ZVJEZDICA
        if sve: self.pročitaj(SQL.ZVJEZDICA)
        else:
            stupci = []
            while True:
                stupci.append(self.pročitaj(SQL.IME))
                if self.granaj(SQL.ZAREZ, SQL.FROM) ** SQL.FROM: break
                self.pročitaj(SQL.ZAREZ)
        self.pročitaj(SQL.FROM)
        return Select(self.pročitaj(SQL.IME), sve, None if sve else stupci)

    def spec_stupac(self):
        ime = self.pročitaj(SQL.IME)
        tip = self.pročitaj(SQL.IME)
        veličina = None
        sljedeći = self.granaj(SQL.ZAREZ, SQL.OTVORENA, SQL.ZATVORENA)
        if sljedeći ** SQL.OTVORENA:
            self.pročitaj(SQL.OTVORENA)
            veličina = self.pročitaj(SQL.BROJ)
            self.pročitaj(SQL.ZATVORENA)
        return Stupac(ime, tip, veličina)

    def create(self):
        self.pročitaj(SQL.CREATE)
        self.pročitaj(SQL.TABLE)
        tablica = self.pročitaj(SQL.IME)
        stupci = []
        self.pročitaj(SQL.OTVORENA)
        while True:
            stupci.append(self.spec_stupac())
            if self.pročitaj(SQL.ZATVORENA, SQL.ZAREZ) ** SQL.ZATVORENA:
                return Create(tablica, stupci)

    def naredba(self):
        početak = self.granaj(SQL.SELECT, SQL.CREATE)
        if početak ** SQL.SELECT: rezultat = self.select()
        elif početak ** SQL.CREATE: rezultat = self.create()
        self.pročitaj(SQL.TOČKAZAREZ)
        return rezultat

    def skripta(self):
        naredbe = [self.naredba()]
        while not self.granaj(SQL.SELECT, SQL.CREATE, E.KRAJ) ** E.KRAJ:
            naredbe.append(self.naredba())
        return Skripta(naredbe)

def sql_parse(kôd):
    parser = SQLParser(sql_lex(kôd))
    rezultat = parser.skripta()
    parser.pročitaj(E.KRAJ)
    return rezultat


class Skripta(AST('naredbe')):
    """Niz SQL naredbi, svaka završava znakom ';'."""
    def razriješi(self):
        imena = {}
        for naredba in self.naredbe:
            naredba.razriješi(imena)
        return imena

class Create(AST('tablica specifikacije')):
    """CREATE TABLE naredba."""
    def razriješi(self, imena):
        tb = imena[self.tablica.sadržaj] = {}
        for stupac in self.specifikacije:
            tb[stupac.ime.sadržaj] = StupacLog(stupac)
        
class Select(AST('tablica sve stupci')):
    """SELECT naredba."""
    def razriješi(self, imena):
        tn = self.tablica.sadržaj
        if tn not in imena:
            lokacija = 'Redak {}, stupac {}: '.format(*self.tablica.početak)
            raise NameError(lokacija + 'Nema tablice {}.'.format(tn))
        tb = imena[tn]
        if self.sve:
            for log in tb.values(): log.pristup += 1
        else:
            for st in self.stupci:
                sn = st.sadržaj
                if sn not in tb:
                    lokacija = 'Redak {}, stupac {}: '.format(*st.početak)
                    poruka = 'Nema stupca {} u tablici {}.'.format(sn, tn)
                    raise NameError(lokacija + poruka)
                tb[sn].pristup += 1
        
class Stupac(AST('ime tip veličina')):
    """Specifikacija stupca u tablici."""

class StupacLog(types.SimpleNamespace):
    def __init__(self, specifikacija):
        self.tip = specifikacija.tip.sadržaj
        vel = specifikacija.veličina
        if vel is not None: self.veličina = int(vel.sadržaj)
        self.pristup = 0


if __name__ == '__main__':
    n1 = sql_parse('''
            CREATE TABLE Persons
            (
                PersonID int,
                Name varchar(255),
                Birthday date,
                Married bool,
                City varchar(9)
            );  -- Sada krenimo nešto selektirati
            SELECT Name, City FROM Persons;
            SELECT * FROM Persons;
            CREATE TABLE Trivial (ID void(0));  -- još jedna tablica
            SELECT * FROM Trivial;
            SELECT Name, Married FROM Persons;
    ''')
    pprint.pprint(n1.razriješi())

# ideje za dalji razvoj:
    # StupacLog.pristup umjesto broja može biti lista brojeva linija skripte
        # u kojima počinju SELECT naredbe koje pristupaju pojedinom stupcu
    # za_indeks(skripta): lista tablica/stupaca natprosječno dohvaćivanih
    # optimizacija: brisanje iz CREATE stupaca kojima nismo uopće pristupili
    # implementirati INSERT INTO, da možemo doista nešto i raditi s podacima
    # povratni tip za SELECT (npr. (varchar(255), bool) za ovaj zadnji)
    # interaktivni način rada (online - naredbu po naredbu analizirati)
