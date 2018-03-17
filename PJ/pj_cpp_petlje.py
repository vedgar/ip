from pj import *


class CPP(enum.Enum):
    FOR = 'for'
    COUT = 'cout'
    ENDL = 'endl'
    OOTV, OZATV, VOTV, VZATV = '(){}'
    MANJE, JEDNAKO, TOČKAZ = '<=;'
    PLUSP = '++'
    PLUSJ = '+='
    IZLAZ = '<<'
    BROJ = 34545
    IME = 'varijabla'

def cpp_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '+':
            sljedeći = lex.čitaj()
            if sljedeći == '+': yield lex.token(CPP.PLUSP)
            elif sljedeći == '=': yield lex.token(CPP.PLUSJ)
            else: lex.greška('nema samostalnog +')
        elif znak == '<':
            if lex.čitaj() == '<': yield lex.token(CPP.IZLAZ)
            else:
                lex.vrati()
                yield lex.token(CPP.MANJE)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.token(ključna_riječ(CPP, lex.sadržaj) or CPP.IME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            if lex.sadržaj == '0': yield lex.token(CPP.BROJ)
            elif lex.sadržaj[0] != '0': yield lex.token(CPP.BROJ)
            else: lex.greška('druge baze nisu podržane')
        else: yield lex.token(operator(CPP, znak) or lex.greška())


# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | izlaz TOČKAZ
# for -> FOR OOTV IME JEDNAKO BROJ TOČKAZ IME MANJE BROJ
# 	  TOČKAZ IME inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSPLUS | PLUSJEDNAKO BROJ
# izlaz -> COUT varijable | COUT varijable IZLAZ ENDL
# varijable -> '' | IZLAZ IME varijable

class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe:
            naredba.izvrši(memorija)
    
class Petlja(AST('varijabla početak granica inkrement blok')):
    def izvrši(self, mem):
        mem[self.varijabla.sadržaj] = int(self.početak.sadržaj)
        while mem[self.varijabla.sadržaj] < int(self.granica.sadržaj):
            for naredba in self.blok:
                naredba.izvrši(mem)
            inkr = self.inkrement
            if inkr is nenavedeno: inkr = 1
            else: inkr = int(inkr.sadržaj)
            mem[self.varijabla.sadržaj] += inkr 
    
class Izlaz(AST('varijable novired')):
    def izvrši(self, mem):
        for varijabla in self.varijable:
            if varijabla.sadržaj in mem:
                print(mem[varijabla.sadržaj], end=' ')
            else:
                varijabla.nedeklaracija()
        if self.novired:
            print()


class CPPParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> CPP.FOR:
            return self.petlja()
        elif self >> CPP.COUT:
            return self.izlaz()
        else:
            self.greška()

    def petlja(self):
        self.pročitaj(CPP.OOTV)
        i = self.pročitaj(CPP.IME)
        self.pročitaj(CPP.JEDNAKO)
        početak = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.TOČKAZ)
        i2 = self.pročitaj(CPP.IME)
        if i != i2: raise SemantičkaGreška('nisu podržane različite varijable')
        self.pročitaj(CPP.MANJE)
        granica = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.TOČKAZ)
        i3 = self.pročitaj(CPP.IME)
        if i != i3: raise SemantičkaGreška('nisu podržane različite varijable')
        if self >> CPP.PLUSP:
            inkrement = nenavedeno
        elif self >> CPP.PLUSJ:
            inkrement = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.OZATV)
        if self >> CPP.VOTV:
            blok = []
            while not self >> CPP.VZATV:
                blok.append(self.naredba())
        else:
            blok = [self.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)
        
    def izlaz(self):
        varijable = []
        novired = False
        while self >> CPP.IZLAZ:
            if self >> CPP.IME:
                varijable.append(self.zadnji)
            elif self >> CPP.ENDL:
                novired = True
                break
        self.pročitaj(CPP.TOČKAZ)
        return Izlaz(varijable, novired)


if __name__ == '__main__':
    CPPParser.parsiraj(cpp_lex('''
        for ( i = 8 ; i < 23 ; i += 2 )
            for(j=0; j<3; j++) cout<<i<<j<<endl;
    ''')).izvrši()
