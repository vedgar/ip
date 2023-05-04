"""Jednostavni parser SQLa, samo za nizove naredbi CREATE i SELECT.

Ovaj fragment SQLa je zapravo regularan -- nigdje nema ugnježđivanja!
Napisan je semantički analizator u obliku name resolvera:
    provjerava jesu li svi selektirani stupci prisutni, te broji pristupe."""


from vepar import *
from backend import PristupLog


class T(TipoviTokena):
    SELECT, FROM, CREATE, TABLE = 'select', 'from', 'create', 'table'
    OTVORENA, ZATVORENA, ZVJEZDICA, ZAREZ, TOČKAZAREZ = '()*,;'
    class IME(Token): pass
    class BROJ(Token): pass

@lexer
def sql(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isalnum():
            lex * str.isalnum
            if lex.sadržaj.isdecimal(): yield lex.token(T.BROJ)
            else: yield lex.literal_ili(T.IME, case=False)
        elif znak == '-':
            lex >> '-'
            lex - '\n'
            lex.zanemari()
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# start -> naredba | start naredba
# naredba -> select TOČKAZAREZ | create TOČKAZAREZ
# select -> SELECT ZVJEZDICA FROM IME | SELECT stupci FROM IME
# stupci -> IME | stupci ZAREZ IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac | spec_stupci ZAREZ spec_stupac
# spec_stupac -> IME IME | IME IME OTVORENA BROJ ZATVORENA

class P(Parser):
    def start(p) -> 'Skripta':
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Skripta(naredbe)

    def select(p) -> 'Select':
        p >> T.SELECT
        if p >= T.ZVJEZDICA: stupci = nenavedeno
        elif stupac := p >> T.IME:
            stupci = [stupac]
            while p >= T.ZAREZ: stupci.append(p >> T.IME)
        p >> T.FROM
        return Select(p >> T.IME, stupci)

    def spec_stupac(p) -> 'Stupac':
        ime, tip = p >> T.IME, p >> T.IME
        if p >= T.OTVORENA:
            veličina = p >> T.BROJ
            p >> T.ZATVORENA
        else: veličina = nenavedeno
        return Stupac(ime, tip, veličina)

    def create(p) -> 'Create':
        p >> T.CREATE, p >> T.TABLE
        tablica = p >> T.IME
        p >> T.OTVORENA
        stupci = [p.spec_stupac()]
        while p >= T.ZAREZ: stupci.append(p.spec_stupac())
        p >> T.ZATVORENA
        return Create(tablica, stupci)

    def naredba(p) -> 'select|create':
        if p > T.SELECT: rezultat = p.select()
        elif p > T.CREATE: rezultat = p.create()
        else: raise p.greška()
        p >> T.TOČKAZAREZ
        return rezultat


### Apstraktna sintaksna stabla:
# Skripta: naredbe:[naredba]
# naredba: Select: tablica:IME stupci:[IME]?
#          Create: tablica:IME specifikacije:[Stupac]
# Stupac: ime:IME tip:IME veličina:BROJ?

class Skripta(AST):
    """Niz naredbi SQLa, svaka završava točkazarezom."""
    naredbe: 'naredba*'

    def razriješi(skripta):
        rt.imena = Memorija(redefinicija=False)
        for naredba in skripta.naredbe: naredba.razriješi()
        return rt.imena

class Stupac(AST):
    """Specifikacija stupca u tablici."""
    ime: 'IME'
    tip: 'IME'
    veličina: 'BROJ?'

class Create(AST):
    """Naredba CREATE TABLE."""
    tablica: 'IME'
    specifikacije: 'Stupac*'

    def razriješi(naredba):
        pristup = rt.imena[naredba.tablica] = Memorija(redefinicija=False)
        for stupac in naredba.specifikacije:
            pristup[stupac.ime] = PristupLog(stupac)
        
class Select(AST):
    """Naredba SELECT."""
    tablica: 'IME'
    stupci: 'IME*?'

    def razriješi(naredba):
        t = rt.imena[naredba.tablica]
        dohvaćeni = naredba.stupci
        if dohvaćeni is nenavedeno: dohvaćeni = dict(t)
        for stupac in dohvaćeni: t[stupac].pristupi()


def za_indeks(skripta):
    for tablica, logovi in skripta.razriješi():
        ukupni = brojač = 0
        for stupac, log in logovi:
            ukupni += log.pristup
            brojač += 1
        if not brojač: continue
        prosjek = ukupni / brojač
        for stupac, log in logovi:
            if log.pristup > prosjek: yield tablica, stupac


skripta = P('''
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
for i, (tablica, stupac) in enumerate(za_indeks(skripta), start=1):
    print(f'CREATE INDEX idx{i} ON {tablica.sadržaj} ({stupac.sadržaj});')

with SemantičkaGreška: P('SELECT * FROM nema;').razriješi()
with SemantičkaGreška:
    P('CREATE TABLE mala (stupac int); SELECT drugi FROM mala;').razriješi()
with SintaksnaGreška: P('CREATE TABLE 2000 (s t);')

# ideje za dalji razvoj:
# * pristup stupcu umjesto samog broja može biti lista brojeva linija \
#     skripte u kojima počinju SELECTovi koji pristupaju pojedinom stupcu
# * optimizacija: brisanje iz CREATE stupaca kojima nismo uopće pristupili
# * implementirati INSERT INTO, da možemo doista nešto i raditi s podacima
# * povratni tip za SELECT (npr. (varchar(255), bool) za predzadnji)
# * interaktivni način rada (online - analizirati naredbu po naredbu)
