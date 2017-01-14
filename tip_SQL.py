import enum
from tip import Parser, Tokenizer, vrsta, Token, AST


class SQL(enum.Enum):
    PRAZNO = ' \t\n'
    KRAJ = None
    GREŠKA = '\x00'
    IME = 'ime'
    ZVJEZDICA = '*'
    ZAREZ = ','
    SELECT = 'SELECT'
    FROM = 'FROM'
    CREATE = 'CREATE'
    TABLE = 'TABLE'
    OTVORENA = '('
    ZATVORENA = ')'
    BROJ = '10'
    TOČKAZAREZ = ';'

    def __repr__(self):
        return self.name

SQL_ključne_riječi = 'SELECT FROM CREATE TABLE'.split()
SQL_operatori = list('*,();')

def sql_lex(kôd):
    lex = Tokenizer(kôd)
    while True:
        znak = lex.pogledaj()
        vr = vrsta(znak)
        if vr == 'kraj': yield Token(SQL.KRAJ, ''); return
        elif vr == 'praznina': Token(SQL.PRAZNO, lex.praznine())
        elif vr == 'znamenka': yield Token(SQL.BROJ, lex.broj())
        elif vr == 'slovo':
            pročitano = lex.ime()
            kw = pročitano.upper()
            simbol = SQL[kw] if kw in SQL_ključne_riječi else SQL.IME
            yield Token(simbol, pročitano)
        elif vr == 'ostalo' and znak in SQL_operatori:
            yield Token(SQL(znak), lex.čitaj())
        else: yield Token(SQL.GREŠKA, lex.čitaj())


class SQLParser(Parser):
    def select(self):
        naredba = AST(stablo='naredba', vrsta=SQL.SELECT)
        self.pročitaj(SQL.SELECT)
        što = self.granaj(SQL.ZVJEZDICA, SQL.IME)
        if što == SQL.ZVJEZDICA:
            self.pročitaj(SQL.ZVJEZDICA)
            naredba.sve = True
        elif što == SQL.IME:
            naredba.stupci = []
            while True:
                stupac = self.pročitaj(SQL.IME)
                naredba.stupci.append(stupac)
                if self.granaj(SQL.ZAREZ, SQL.FROM) == SQL.FROM: break
                self.pročitaj(SQL.ZAREZ)
        self.pročitaj(SQL.FROM)
        naredba.tablica = self.pročitaj(SQL.IME)
        return naredba

    def spec_stupac(self):
        stupac = AST(stablo='stupac')
        stupac.ime = self.pročitaj(SQL.IME)
        stupac.tip = self.pročitaj(SQL.IME)
        sljedeći = self.granaj(SQL.ZAREZ, SQL.OTVORENA, SQL.ZATVORENA)
        if sljedeći == SQL.OTVORENA:
            self.pročitaj(SQL.OTVORENA)
            stupac.veličina = self.pročitaj(SQL.BROJ)
            self.pročitaj(SQL.ZATVORENA)
            sljedeći = self.granaj(SQL.ZAREZ, SQL.ZATVORENA)
        if sljedeći == SQL.ZAREZ:
            self.pročitaj(SQL.ZAREZ)
        return stupac

    def create(self):
        self.pročitaj(SQL.CREATE)
        self.pročitaj(SQL.TABLE)
        naredba = AST(stablo='naredba', vrsta=SQL.CREATE)
        naredba.tablica = self.pročitaj(SQL.IME)
        naredba.stupci = []
        self.pročitaj(SQL.OTVORENA)
        while True:
            stupac = self.spec_stupac()
            naredba.stupci.append(stupac)
            if self.granaj(SQL.ZATVORENA, SQL.IME) == SQL.ZATVORENA: break
        self.pročitaj(SQL.ZATVORENA)
        return naredba

    def naredba(self):
        početak = self.granaj(SQL.SELECT, SQL.CREATE)
        if početak == SQL.SELECT:
            rezultat = self.select()
        elif početak == SQL.CREATE:
            rezultat = self.create()
        self.pročitaj(SQL.TOČKAZAREZ)
        return rezultat


def sql_parse(kôd):
    parser = SQLParser(sql_lex(kôd))
    rezultat = parser.naredba()
    parser.pročitaj(SQL.KRAJ)
    return rezultat


if __name__ == '__main__':
    l = sql_parse('''
            CREATE TABLE Persons
            (
            PersonID int,
            LastName varchar(255),
            FirstName varchar(255),
            Address varchar(255),
            City varchar(255),
            );
    ''')
    print(l)
    m = sql_parse('   SELECT firstName, lastName FROM wherever;')
    print(m)
