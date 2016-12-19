import collections, enum, types


class Buffer:
    MAX_BUFFER = 1
    
    def __init__(self, sequence):
        self.iterator = iter(sequence)
        self.buffer = []
        self.redni_broj = 0

    def čitaj(self):
        self.redni_broj += 1
        if self.buffer:
            self.zadnje = self.buffer.pop()
        else:
            self.zadnje = next(self.iterator, None)
        # print(self.zadnje)
        return self.zadnje

    def vrati(self):
        self.redni_broj -= 1
        assert len(self.buffer) < self.MAX_BUFFER
        self.buffer.append(self.zadnje)

    def pogledaj(self):
        znak = self.čitaj()
        self.vrati()
        return znak


class Tokenizer(Buffer):
    def praznine(self):
        pročitano = ''
        while True:
            znak = self.čitaj()
            if vrsta(znak) == 'praznina':
                pročitano += znak
            else:
                self.vrati()
                return pročitano

    def ime(self):
        pročitano = ''
        while True:
            znak = self.čitaj()
            if vrsta(znak) in {'slovo', 'znamenka'}:
                pročitano += znak
            else:
                self.vrati()
                return pročitano

    def broj(self):
        pročitano = ''
        while True:
            znak = self.čitaj()
            if vrsta(znak) == 'znamenka':
                pročitano += znak
            else:
                self.vrati()
                return pročitano


class Token(types.SimpleNamespace):
    def __init__(self, simbol, sadržaj):
        self.tip, self.sadržaj = simbol, sadržaj

    def __repr__(self):
        return self.tip.name + repr(self.sadržaj)


def vrsta(znak):
    if znak is None: return 'kraj'
    elif znak.isspace(): return 'praznina'
    elif znak.isalpha(): return 'slovo'
    elif znak.isdigit(): return 'znamenka'
    elif znak.isprintable(): return 'ostalo'
    else: return 'greška'


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

SQL_ključne_riječi = 'SELECT FROM CREATE TABLE'.upper().split()
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


class Parser(Buffer):
    def pročitaj(self, *simboli):
        sljedeći = self.čitaj()
        if sljedeći.tip in simboli:
            return sljedeći
        poruka = 'Token #{}: očekivano {}, pročitano {}'
        očekivani = ' ili '.join(simbol.name for simbol in simboli)
        raise SyntaxError(poruka.format(self.redni_broj, očekivani, sljedeći))

    def granaj(self, *simboli):
        sljedeći = self.pročitaj(*simboli)
        self.vrati()
        return sljedeći.tip


class AST(types.SimpleNamespace):
    def __repr__(self):
        atributi = vars(self).copy()
        ime = atributi.pop('stablo', type(self).__name__)
        stavke = ['{}={}'.format(k, v) for k, v in atributi.items()]
        return ime + ', '.join(stavke).join('()')


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
                naredba.stupci.append(self.pročitaj(SQL.IME))
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

m = sql_parse('   SELECT firstName, lastName FROM wherever;')


class LS(enum.Enum):
    PRAZNO, KRAJ, GREŠKA = range(3)
    PVAR, NEG, KON, DIS, KOND, BIKOND, OTV, ZATV = range(3, 11)

def ls_lex(kôd):
    lex = Tokenizer(kôd)
    while True:
        znak = lex.čitaj()
        if znak == 'P': yield Token(LS.PVAR, znak + lex.broj())
        elif znak == '!': yield Token(LS.NEG, znak)
        elif znak == '|': yield Token(LS.DIS, znak)
        elif znak == '&': yield Token(LS.KON, znak)
        elif znak == '(': yield Token(LS.OTV, znak)
        elif znak == ')': yield Token(LS.ZATV, znak)
        elif znak == '-':
            drugi = lex.čitaj()
            if drugi == '>': yield Token(LS.KOND, znak + drugi)
            else:
                poruka = 'Nakon - očekivano >, pročitano {}'
                raise LexError(poruka.format(drugi))
        elif znak == '<':
            drugi, treći = lex.čitaj(), lex.čitaj()
            if (drugi, treći) == ('-', '>'):
                yield Token(LS.BIKOND, znak + drugi + treći)
            else:
                poruka = 'Nakon < očekivano ->, pročitano {}{}'
                raise LexError(poruka.format(drugi, treći))
        elif znak is None: return
        else: yield Token(LS.GREŠKA, '')

print(*ls_lex('P5&(P3->P1)'), sep='\n')

class LSParser(Parser):    
    def formula(self):
        fo = AST(stablo='formula')
        početak = self.granaj(LS.NEG, LS.PVAR, LS.OTV)
        if početak == LS.PVAR:
            fo.varijabla = self.pročitaj(LS.PVAR)
        elif početak == LS.NEG:
            self.pročitaj(LS.NEG)
            fo.vrsta = 'negacija'
            fo.potformula = self.formula()
        elif početak == LS.OTV:
            self.pročitaj(LS.OTV)
            ...
