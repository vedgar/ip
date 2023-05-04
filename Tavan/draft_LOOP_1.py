# nedovršeno i vjerojatno nepotrebno

from pj import *


class LOOP(enum.Enum):
    INC, DEC, MACRO = 'INC', 'DEC', 'macro'
    TOČKAZ, VOTV, VZATV = ';{}'

    class IME(Token): pass

    class R(Token):
        @property
        def broj(self): return int(self.sadržaj[1:])


def loop_lex(prog):
    lex = Tokenizer(prog)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            ime = lex.sadržaj
            if ime.startswith('R') and ime[1:].isdigit():
                yield lex.token(LOOP.R)
            else: yield lex.token(ključna_riječ(LOOP, ime) or LOOP.IME)
        else: yield lex.token(operator(LOOP, znak) or lex.greška())


### Beskontekstna gramatika:
# start -> makro_dekl* program
# makro_dekl -> MACRO IME+ p_zagr
# p_zagr -> VOTV program VZATV
# program -> naredba*
# naredba -> opkod arg TOČKAZ | IME arg+ TOČKAZ | arg p_zagr
# opkod -> INC | DEC
# arg -> R | IME

### Apstraktna sintaksna stabla:
# Kôd: makroi:Dict[IME->Program], parametri:Dict[IME->List[IME]], main:Program
# Petlja: registar:R|IME, tijelo:Program
# Inkrement|Dekrement: registar:R|IME
# Program: naredbe:List[Petlja|Inkrement|Dekrement|MakroPoziv]
# MakroPoziv: makro:IME, argumenti:List[R|IME]


class LOOPParser(Parser):
    def start(self):
        makroi, parametri = {}, {}
        while self >> LOOP.MACRO:
            ime = self.pročitaj(LOOP.IME)
            parametri[ime] = []
            while self >> LOOP.IME: parametri[ime].append(self.zadnji)
            makroi[ime] = self.program_u_zagradi()
        return Kôd(makroi, parametri, self.program())
    
    def program_u_zagradi(self):
        self.pročitaj(LOOP.VOTV)
        u_zagradi = self.program()
        self.pročitaj(LOOP.VZATV)
        return u_zagradi

    def program(self):
        naredbe = [self.naredba()]
        while not self >= {E.KRAJ, LOOP.VZATV}: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> {LOOP.INC, LOOP.DEC}:
            opkod = Inkrement if self.zadnji ** LOOP.INC else Dekrement
            reg = self.pročitaj(LOOP.R, LOOP.IME)
            self.pročitaj(LOOP.TOČKAZ)
            return opkod(reg)
        početak = self.pročitaj(LOOP.R, LOOP.IME)
        if self >= LOOP.VOTV: return Petlja(početak, self.program_u_zagradi())
        argumenti = []
        while self >> {LOOP.R, LOOP.IME}: argumenti.append(self.zadnji)
        self.pročitaj(LOOP.TOČKAZ)
        return MakroPoziv(početak, argumenti)


class Kôd(AST('makroi parametri main')):
    def izvrši(self, registri):
        self.main.izvrši(registri)

class Program(AST('naredbe')):
    def izvrši(self, registri):
        for naredba in self.naredbe:
            naredba.izvrši(registri)

class Inkrement(AST('registar')):
    def izvrši(self, registri):
        registri[self.registar.broj] += 1

class Dekrement(AST('registar')):
    def izvrši(self, registri):
        if registri[self.registar.broj]:
            registri[self.registar.broj] -= 1
        
class Petlja(AST('registar tijelo')):
    def izvrši(self, registri):
        for ponavljanje in range(registri[self.registar.broj]):
            self.tijelo.izvrši(registri)

class MakroPoziv(AST('makro argumenti')):
    pass


def računaj(program, *ulazi):
    registri = collections.Counter()
    for indeks, ulaz in enumerate(ulazi, 1):
        assert isinstance(ulaz, int) and ulaz >= 0
        registri[indeks] = ulaz
    program.izvrši(registri)
    return registri[0]


if __name__ == '__main__':
    program = LOOPParser.parsiraj(loop_lex('''
        macro ZERO Rj { Rj { DEC Rj; } }
        macro MOVE from to { ZERO to; from { INC to; } }
        macro REMOVE from to { MOVE from to; ZERO from; }

        ZERO R0; INC R0; INC R0;
    '''))
    print(program)
