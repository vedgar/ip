from pj import *


class CPP(enum.Enum):
    FOR = 'for'
    COUT = 'cout'
    ENDL = 'endl'
    IF = 'if'
    OOTV, OZATV, VOTV, VZATV = '(){}'
    MANJE, JEDNAKO, TOČKAZ = '<=;'
    PLUSP = '++'
    PLUSJ = '+='
    IZLAZ = '<<'
    JJEDNAKO = '=='
    class BREAK(Token):
        def izvrši(self, mem):
            raise BreakException

    class BROJ(Token):
        def vrijednost(self, mem):
            return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self, mem):
            return mem[self.sadržaj]

def cpp_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '+':
            sljedeći = lex.čitaj()
            if sljedeći == '+': yield lex.token(CPP.PLUSP)
            elif sljedeći == '=': yield lex.token(CPP.PLUSJ)
            else: lex.greška('u ovom jeziku nema samostalnog +')
        elif znak == '<':
            if lex.čitaj() == '<': yield lex.token(CPP.IZLAZ)
            else:
                lex.vrati()
                yield lex.token(CPP.MANJE)
        elif znak == '=':
            if lex.čitaj() == '=': yield lex.token(CPP.JJEDNAKO)
            else:
                lex.vrati()
                yield lex.token(CPP.JEDNAKO)
        elif znak.islower():
            lex.zvijezda(str.islower)
            if lex.sadržaj == 'break': yield lex.token(CPP.BREAK)
            else: yield lex.token(ključna_riječ(CPP, lex.sadržaj) or CPP.IME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            if lex.sadržaj == '0' or lex.sadržaj[0] != '0':
                yield lex.token(CPP.BROJ)
            else: lex.greška('druge baze nisu podržane')
        else: yield lex.token(operator(CPP, znak) or lex.greška())


# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | izlaz TOČKAZ | BREAK TOČKAZ | grananje
# for -> FOR OOTV IME JEDNAKO BROJ TOČKAZ IME MANJE BROJ
# 	  TOČKAZ IME inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSP | PLUSJ BROJ
# izlaz -> COUT varijable | COUT varijable IZLAZ ENDL
# varijable -> '' | IZLAZ IME varijable
# grananje -> IF OOTV IME JJEDNAKO BROJ OZATV naredba

class CPPParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> CPP.FOR: return self.petlja()
        elif self >> CPP.COUT: return self.izlaz()
        elif self >> CPP.IF: return self.grananje()
        elif self >> CPP.BREAK:
            br = self.zadnji
            self.pročitaj(CPP.TOČKAZ)
            return br
        else: self.greška()

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
        if self >> CPP.PLUSP: inkrement = nenavedeno
        elif self >> CPP.PLUSJ: inkrement = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.OZATV)
        if self >> CPP.VOTV:
            blok = []
            while not self >> CPP.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)
        
    def izlaz(self):
        varijable = []
        novired = False
        while self >> CPP.IZLAZ:
            if self >> CPP.IME: varijable.append(self.zadnji)
            elif self >> CPP.ENDL:
                novired = True
                break
        self.pročitaj(CPP.TOČKAZ)
        return Izlaz(varijable, novired)

    def grananje(self):
        self.pročitaj(CPP.OOTV)
        lijevo = self.pročitaj(CPP.IME)
        self.pročitaj(CPP.JJEDNAKO)
        desno = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.OZATV)
        naredba = self.naredba()
        return Grananje(lijevo, desno, naredba)


class BreakException(Exception): pass

class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe:
            naredba.izvrši(memorija)
    
class Petlja(AST('varijabla početak granica inkrement blok')):
    def izvrši(self, mem):
        kv = self.varijabla.sadržaj
        mem[kv] = self.početak.vrijednost(mem)
        while mem[kv] < self.granica.vrijednost(mem):
            try:
                for naredba in self.blok:
                    naredba.izvrši(mem)
            except BreakException: break
            inkr = self.inkrement
            if inkr is nenavedeno: inkr = 1
            else: inkr = inkr.vrijednost(mem)
            mem[kv] += inkr 

class Izlaz(AST('varijable novired')):
    def izvrši(self, mem):
        for varijabla in self.varijable:
            if varijabla.sadržaj in mem: print(mem[varijabla.sadržaj], end=' ')
            else: varijabla.nedeklaracija()
        if self.novired: print()

class Grananje(AST('lijevo desno naredba')):
    def izvrši(self, mem):
        l = self.lijevo.vrijednost(mem)
        d = self.desno.vrijednost(mem)
        if l == d: self.naredba.izvrši(mem)


if __name__ == '__main__':
    cpp = CPPParser.parsiraj(cpp_lex('''
        for ( i = 8 ; i < 23 ; i += 2 )
            for(j=0; j<3; j++) {
                cout<<i<<j<<endl;
                if(i == 14) if (j == 1) break;
            }
    '''))
    print(cpp)
    # Program(naredbe=[
    #   Petlja(varijabla=IME'i',
    #          početak=BROJ'8',
    #          granica=BROJ'23',
    #          inkrement=BROJ'2',
    #          blok=[Petlja(varijabla=IME'j',
    #                       početak=BROJ'0',
    #                       granica=BROJ'3',
    #                       inkrement=nenavedeno,
    #                       blok=[Izlaz(varijable=[IME'i', IME'j'],
    #                                   novired=True)]
    #                )]
    # )])
    cpp.izvrši()
