from pj import *


class LOOP(enum.Enum):
    INC, DEC = 'INC', 'DEC'
    TOČKAZ, VOTV, VZATV = ';{}'
    
    class REG(Token):
        @property
        def broj(self): return int(self.sadržaj[1:])


def loop_lex(prog):
    lex = Tokenizer(prog)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak in 'ID':
            lex.čitaj()
            lex.čitaj()
            yield lex.literal(LOOP)
        elif znak == 'R':
            lex.plus(str.isdigit)
            yield lex.token(LOOP.REG)
        else: yield lex.literal(LOOP)


### Beskontekstna gramatika:
# program -> naredba | naredba program
# naredba -> opkod R TOČKAZ | R VOTV program VZATV
# opkod -> INC | DEC

### Apstraktna sintaksna stabla:
# Petlja: registar:R, tijelo:Program
# Inkrement: registar:R
# Dekrement: registar:R
# Program: naredbe:List[Petlja|Inkrement|Dekrement]


class LOOPParser(Parser):
    def program(self):
        naredbe = [self.naredba()]
        while not self >= {E.KRAJ, LOOP.VZATV}: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> {LOOP.INC, LOOP.DEC}:
            opkod = Inkrement if self.zadnji ^ LOOP.INC else Dekrement
            reg = self.pročitaj(LOOP.REG)
            self.pročitaj(LOOP.TOČKAZ)
            return opkod(reg)
        else:
            reg = self.pročitaj(LOOP.REG)
            self.pročitaj(LOOP.VOTV)
            tijelo = self.program()
            self.pročitaj(LOOP.VZATV)
            return Petlja(reg, tijelo)

    start = program


class Program(AST('naredbe')):
    def izvrši(self, registri):
        for naredba in self.naredbe: naredba.izvrši(registri)

class Inkrement(AST('registar')):
    def izvrši(self, registri): registri[self.registar.broj] += 1

class Dekrement(AST('registar')):
    def izvrši(self, registri):
        if registri[self.registar.broj]: registri[self.registar.broj] -= 1
        
class Petlja(AST('registar tijelo')):
    def izvrši(self, registri):
        for ponavljanje in range(registri[self.registar.broj]):
            self.tijelo.izvrši(registri)


def računaj(program, *ulazi):
    registri = collections.Counter(dict(enumerate(ulazi, 1)))
    program.izvrši(registri)
    return registri[0]


if __name__ == '__main__':
    power = LOOPParser.parsiraj(loop_lex('''
        INC R0;
        R2{
            R0{
                R1{INCR3;}
                DECR0;
            }
            R3{DECR3;INCR0;}
        }
    '''))
    print(power)
    print(računaj(power, 3, 6))
