"""Interpreter za jednostavni fragment jezika C++: petlje, grananja, ispis.
    * petlje: for(var = broj; var < broj; var ++ ili var += broj) naredba
    * grananja: if(var == broj) naredba
    * ispis: cout << var1 << var2 << ..., s opcionalnim << endl na kraju

Tijelo petlje može biti i blok u vitičastim zagradama.
Podržana je i naredba break za izlaz iz unutarnje petlje:
    nelokalna kontrola toka realizirana je pomoću izuzetka Prekid."""


from vepar import *


class T(TipoviTokena):
    FOR, COUT, ENDL, IF = 'for', 'cout', 'endl', 'if'
    OOTV, OZATV, VOTV, VZATV, MANJE, JEDNAKO, TOČKAZ = '(){}<=;'
    PLUSP, PLUSJ, MMANJE, JJEDNAKO = '++', '+=', '<<', '=='
    class BREAK(Token):
        literal = 'break'
        def izvrši(self, mem): raise Prekid
    class BROJ(Token):
        def vrijednost(self, mem): return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self, mem): return mem[self]


def cpp(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '+':
            if lex >> '+': yield lex.token(T.PLUSP)
            elif lex >> '=': yield lex.token(T.PLUSJ)
            else: raise lex.greška('u ovom jeziku nema samostalnog +')
        elif znak == '<': yield lex.token(T.MMANJE if lex >> '<' else T.MANJE)
        elif znak=='=': yield lex.token(T.JJEDNAKO if lex >> '=' else T.JEDNAKO)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.literal(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


## Beskontekstna gramatika
# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | grananje | ispis TOČKAZ | BREAK TOČKAZ
# for -> FOR OOTV IME# JEDNAKO BROJ TOČKAZ IME# MANJE BROJ TOČKAZ
# 	     IME# inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSP | PLUSJ BROJ
# ispis -> COUT varijable | COUT varijable MMANJE ENDL
# varijable -> '' | MMANJE IME varijable
# grananje -> IF OOTV IME JJEDNAKO BROJ OZATV naredba

 


class P(Parser):
    lexer = cpp

    def start(self):
        naredbe = [self.naredba()]
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self > T.FOR: return self.petlja()
        elif self > T.COUT: return self.ispis()
        elif self > T.IF: return self.grananje()
        elif br := self >> T.BREAK:
            self >> T.TOČKAZ
            return br

    def petlja(self):
        kriva_varijabla = SemantičkaGreška(
            'Sva tri dijela for-petlje moraju imati istu varijablu.')
        self >> T.FOR, self >> T.OOTV
        i = self >> T.IME
        self >> T.JEDNAKO
        početak = self >> T.BROJ
        self >> T.TOČKAZ

        if (self >> T.IME) != i: raise kriva_varijabla
        self >> T.MANJE
        granica = self >> T.BROJ
        self >> T.TOČKAZ

        if (self >> T.IME) != i: raise kriva_varijabla
        if self >= T.PLUSP: inkrement = nenavedeno
        elif self >> T.PLUSJ: inkrement = self >> T.BROJ
        self >> T.OZATV

        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)
        
    def ispis(self):
        self >> T.COUT
        varijable, novired = [], nenavedeno
        while self >= T.MMANJE:
            if varijabla := self >= T.IME: varijable.append(varijabla)
            else:
                novired = self >> T.ENDL
                break
        self >> T.TOČKAZ
        return Ispis(varijable, novired)

    def grananje(self):
        self >> T.IF, self >> T.OOTV
        lijevo = self >> T.IME
        self >> T.JJEDNAKO
        desno = self >> T.BROJ
        self >> T.OZATV
        return Grananje(lijevo, desno, self.naredba())


class Prekid(NelokalnaKontrolaToka): """Signal koji šalje naredba break."""


## Apstraktna sintaksna stabla:
# Program: naredbe:[naredba]
# naredba: BREAK: Token
#          Petlja: varijabla:IME početak:BROJ granica:BROJ
#                      inkrement:BROJ? blok:[naredba]
#          Ispis: varijable:[IME] novired:ENDL?
#          Grananje: lijevo:IME desno:BROJ naredba:naredba

class Program(AST('naredbe')):
    def izvrši(self):
        mem = Memorija()
        try:  # break izvan petlje je zapravo sintaksna greška - kompliciranije
            for naredba in self.naredbe: naredba.izvrši(mem)
        except Prekid: raise SemantičkaGreška('nedozvoljen break izvan petlje')

class Petlja(AST('varijabla početak granica inkrement blok')):
    def izvrši(self, mem):
        kv = self.varijabla  # kontrolna varijabla petlje
        mem[kv] = self.početak.vrijednost(mem)
        while mem[kv] < self.granica.vrijednost(mem):
            try:
                for naredba in self.blok: naredba.izvrši(mem)
            except Prekid: break
            inkr = self.inkrement
            if inkr is nenavedeno: inkr = 1
            else: inkr = inkr.vrijednost(mem)
            mem[kv] += inkr 

class Ispis(AST('varijable novired')):
    def izvrši(self, mem):
        for var in self.varijable: print(var.vrijednost(mem), end=' ')
        if self.novired ^ T.ENDL: print()

class Grananje(AST('lijevo desno naredba')):
    def izvrši(self, mem):
        if self.lijevo.vrijednost(mem) == self.desno.vrijednost(mem):
            self.naredba.izvrši(mem)


def očekuj(greška, kôd):
    with očekivano(greška): P(kôd).izvrši()

cpp = P('''\
    for ( i = 8 ; i < 13 ; i += 2 )
        for(j=0; j<3; j++) {
            cout<<i<<j<<endl;
            if(i == 10) if (j == 1) break;
        }
''')
prikaz(cpp, 8)
cpp.izvrši()
prikaz(P('cout;'))
očekuj(SintaksnaGreška, '')
očekuj(SintaksnaGreška, 'for(c=1; c<3; c++);')
očekuj(LeksičkaGreška, '+1')
očekuj(SemantičkaGreška, 'for(a=1; b<3; c++);')
očekuj(SemantičkaGreška, 'break;')
očekuj(LeksičkaGreška, 'if(i == 07) cout;')


# DZ: implementirati naredbu continue
# DZ: implementirati praznu naredbu (for/if(...);)
# DZ: omogućiti i grananjima da imaju blokove - uvesti novo AST Blok
# DZ: omogućiti da parametri petlje budu varijable, ne samo brojevi
# DZ: omogućiti grananja s obzirom na relaciju <, ne samo ==
# DZ: dodati kontekstnu varijablu 'jesmo li u petlji' za dozvolu BREAK
# DZ: uvesti deklaracije varijabli i pratiti jesu li varijable deklarirane
