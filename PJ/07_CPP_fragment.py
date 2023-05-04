"""Interpreter za jednostavni fragment jezika C++: petlje, grananja, ispis.
    Prema zadatku s kolokvija 16. veljače 2015. (Puljić).
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
        def izvrši(self): raise Prekid
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self): return rt.mem[self]

@lexer
def cpp(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: raise lex.greška('u ovom jeziku nema samostalnog +')
        elif znak == '<': yield lex.token(T.MMANJE if lex >= '<' else T.MANJE)
        elif znak == '=':
            yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak.isalpha() or znak == '_':
            lex * {str.isalnum, '_'}
            yield lex.literal_ili(T.IME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        else: yield lex.literal(T)


## Beskontekstna gramatika
# start -> naredbe naredba
# naredbe -> '' | naredbe naredba
# naredba -> petlja | grananje | ispis TOČKAZ | BREAK TOČKAZ
# for -> FOR OOTV IME# JEDNAKO BROJ TOČKAZ IME# MANJE BROJ TOČKAZ
# 	     IME# inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSP | PLUSJ BROJ
# ispis -> COUT varijable | COUT varijable MMANJE ENDL
# varijable -> '' | varijable MMANJE IME
# grananje -> IF OOTV IME JJEDNAKO BROJ OZATV naredba
 
class P(Parser):
    def start(p) -> 'Program':
        naredbe = [p.naredba()]
        while not p > KRAJ: naredbe.append(p.naredba())
        return Program(naredbe)

    def naredba(p) -> 'petlja|ispis|grananje|BREAK':
        if p > T.FOR: return p.petlja()
        elif p > T.COUT: return p.ispis()
        elif p > T.IF: return p.grananje()
        elif br := p >> T.BREAK:
            p >> T.TOČKAZ
            return br

    def petlja(p) -> 'Petlja':
        kriva_varijabla = SemantičkaGreška(
            'Sva tri dijela for-petlje moraju imati istu varijablu.')
        p >> T.FOR, p >> T.OOTV
        i = p >> T.IME
        p >> T.JEDNAKO
        početak = p >> T.BROJ
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        p >> T.MANJE
        granica = p >> T.BROJ
        p >> T.TOČKAZ

        if (p >> T.IME) != i: raise kriva_varijabla
        if p >= T.PLUSP: inkrement = nenavedeno
        elif p >> T.PLUSJ: inkrement = p >> T.BROJ
        p >> T.OZATV

        if p >= T.VOTV:
            blok = []
            while not p >= T.VZATV: blok.append(p.naredba())
        else: blok = [p.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)
        
    def ispis(p) -> 'Ispis':
        p >> T.COUT
        varijable, novired = [], nenavedeno
        while p >= T.MMANJE:
            if varijabla := p >= T.IME: varijable.append(varijabla)
            else:
                novired = p >> T.ENDL
                break
        p >> T.TOČKAZ
        return Ispis(varijable, novired)

    def grananje(p) -> 'Grananje':
        p >> T.IF, p >> T.OOTV
        lijevo = p >> T.IME
        p >> T.JJEDNAKO
        desno = p >> T.BROJ
        p >> T.OZATV
        return Grananje(lijevo, desno, p.naredba())


class Prekid(NelokalnaKontrolaToka): """Signal koji šalje naredba break."""


## Apstraktna sintaksna stabla:
# Program: naredbe:[naredba]
# naredba: BREAK: Token
#          Petlja: varijabla:IME početak:BROJ granica:BROJ
#                      inkrement:BROJ? blok:[naredba]
#          Ispis: varijable:[IME] novired:ENDL?
#          Grananje: lijevo:IME desno:BROJ onda:naredba

class Program(AST):
    naredbe: 'naredba*'

    def izvrši(program):
        rt.mem = Memorija()
        try:  # break izvan petlje je zapravo sintaksna greška - kompliciranije
            for naredba in program.naredbe: naredba.izvrši()
        except Prekid: raise SemantičkaGreška('nedozvoljen break izvan petlje')

class Petlja(AST):
    varijabla: 'IME'
    početak: 'BROJ'
    granica: 'BROJ'
    inkrement: 'BROJ?'
    blok: 'naredba*'

    def izvrši(petlja):
        kv = petlja.varijabla  # kontrolna varijabla petlje
        rt.mem[kv] = petlja.početak.vrijednost()
        while rt.mem[kv] < petlja.granica.vrijednost():
            try:
                for naredba in petlja.blok: naredba.izvrši()
            except Prekid: break
            inkr = petlja.inkrement
            rt.mem[kv] += inkr.vrijednost() if inkr else 1

class Ispis(AST):
    varijable: 'IME*'
    novired: 'ENDL?'

    def izvrši(ispis):
        for varijabla in ispis.varijable:
            print(varijabla.vrijednost(), end=' ')
        if ispis.novired ^ T.ENDL: print()

class Grananje(AST):
    lijevo: 'IME'
    desno: 'BROJ'
    onda: 'naredba'

    def izvrši(grananje):
        if grananje.lijevo.vrijednost() == grananje.desno.vrijednost():
            grananje.onda.izvrši()


def očekuj(greška, kôd):
    print('Testiram:', kôd)
    with greška: P(kôd).izvrši()

prikaz(kôd := P('''
    for ( i = 8 ; i < 13 ; i += 2 ) {
        for(j=0; j<5; j++) {
            cout<<i<<j;
            if(i == 10) if (j == 1) break;
        }
        cout<<i<<endl;
    }
'''), 8)
kôd.izvrši()
prikaz(P('cout;'))
očekuj(SintaksnaGreška, '')
očekuj(SintaksnaGreška, 'for(c=1; c<3; c++);')
očekuj(LeksičkaGreška, '+1')
očekuj(SemantičkaGreška, 'for(a=1; b<3; c++)break;')
očekuj(SemantičkaGreška, 'break;')
očekuj(LeksičkaGreška, 'if(i == 07) cout;')


# DZ: implementirajte naredbu continue
# DZ: implementirajte praznu naredbu (for/if(...);)
# DZ: omogućite i grananjima da imaju blokove -- uvedite novo AST Blok
# DZ: omogućite da parametri petlje budu varijable, ne samo brojevi
# DZ: omogućite grananja s obzirom na relaciju <, ne samo ==
# DZ: dodajte parseru kontekstnu varijablu 'jesmo li u petlji' za dozvolu BREAK
# DZ: uvedite deklaracije varijabli i pratite jesu li varijable deklarirane
