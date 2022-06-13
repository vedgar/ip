"""Kulinarski recepti: po uzoru na kolokvij 6. srpnja 2021.
https://web.math.pmf.unizg.hr/~veky/B/IP.k2.21-07-06.pdf"""

from vepar import *

class T(TipoviTokena):
    IMA, G, SASTOJCI, PRIPREMA = '--ima--', 'g', '-SASTOJCI-', '-PRIPREMA-'
    class SASTOJCIOSOBE(Token):
        def vrijednost(self):
            return int(''.join(filter(str.isdigit, self.sadržaj)))
    class BROJ(Token):
        def vrijednost(self):
            return int(self.sadržaj)
    class RIJEČ(Token): pass 
    class KOMENTAR(Token): pass 

@lexer
def rec(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '-':
            if lex >= '-':
                lex.pročitaj_do('-', više_redova=True)
                lex >> '-'
                yield lex.literal_ili(T.KOMENTAR)
            elif lex >= 'S': 
                lex - 'I'
                if lex.sadržaj == '-SASTOJCI':
                    if lex >= '-': yield lex.token(T.SASTOJCI)
                    else:
                        for znak in ' ZA ': lex >> znak
                        lex.prirodni_broj('', nula = False)
                        lex >> '-'
                        yield lex.token(T.SASTOJCIOSOBE)
                else: raise lex.greška('nepostojeće zaglavlje')
            else:
                lex - '-'
                yield lex.literal(T)
        elif znak.isdigit():
            lex.prirodni_broj(znak, nula = False)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * str.isalpha
            if lex.sadržaj == 'ml' : yield lex.token(T.G)
            else: yield lex.literal_ili(T.RIJEČ)
        else: raise lex.greška()

### Beskontekstna gramatika:
# recept -> KOMENTAR (SASTOJCI | SASTOJCIOSOBE) podrecept
# podrecept -> sastojak+ priprema
# sastojak -> (BROJ G)? RIJEČ (SASTOJCI podrecept | IMA? KOMENTAR?)?
# priprema -> PRIPREMA RIJEČ BROJ RIJEČ KOMENTAR?

class P(Parser):
    def recept(self): return Recept(self >> T.KOMENTAR,
                                    self >> {T.SASTOJCI, T.SASTOJCIOSOBE},
                                    self.sastojci(), self.priprema())

    def sastojci(self):
        sastojci = []
        while self > {T.BROJ, T.RIJEČ}: sastojci.append(self.sastojak())
        return sastojci

    def sastojak(self):
        if količina := self >= T.BROJ: mjera = self >> T.G
        ime = self >> T.RIJEČ
        if self >= T.SASTOJCI: return Podrecept(količina, mjera, ime,
                                          self.sastojci(), self.priprema())
        elif ima := self >= T.IMA: self >= T.KOMENTAR
        elif self >= T.KOMENTAR: pass
       
        if količina: return Sastojak(količina, mjera, ime, ima)
        else: return SastojakZanemariveMase(ime, ima)

    def priprema(self):
        self >> T.PRIPREMA, self >> T.RIJEČ
        minute = self >> T.BROJ
        self >> T.RIJEČ, self >= T.KOMENTAR
        return minute

### AST
# Recept: naslov:KOMENTAR broj_osoba:SASTOJCIOSOBE
#         sastojci:[sastojak] minute:BROJ
# sastojak: Podrecept: količina:BROJ? mjera:G? ime:RIJEČ
#                      sastojci:[sastojak] minute:BROJ
#           Sastojak: količina:BROJ? mjera:G? ime:RIJEČ ima:IMA?
#           SastojakZanemariveMase: ime:RIJEČ ima:IMA?

class Recept(AST):
    naslov: 'KOMENTAR'
    broj_osoba: 'SASTOJCIOSOBE'
    sastojci: 'sastojak+'
    minute: 'BROJ'

    def provjera(self): return all(s.provjera() for s in self.sastojci)

    def popis(self):
        rt.popis=Memorija()
        for s in self.sastojci: s.popis(self.broj_osoba.vrijednost())
        return rt.popis

    def vrijeme(self): return sum((s.vrijeme() for s in self.sastojci),
                                  self.minute.vrijednost())

class Podrecept(AST):
    količina: 'BROJ?'
    mjera: 'G?'
    ime: 'RIJEČ'
    sastojci: 'sastojak+'
    minute: 'BROJ'

    def provjera(self):
        return self.količina.vrijednost() == sum(s.masa() for s in self.sastojci)

    def popis(self, broj_osoba):
        for s in self.sastojci: s.popis(broj_osoba)

    vrijeme = Recept.vrijeme

class Sastojak(AST):
    količina: 'BROJ?'
    mjera: 'G?'
    ime: 'RIJEČ'
    ima: 'IMA?'

    def masa(self):
        return self.količina.vrijednost()

    def popis(self, broj_osoba):
        if not self.ima:
            if self.ime not in rt.popis: rt.popis[self.ime] = 0
            rt.popis[self.ime] += self.masa() / broj_osoba

    def provjera(self): return True

    def vrijeme(self): return 0

class SastojakZanemariveMase(AST):
    ime: 'RIJEČ'
    ima: 'IMA?'

    def masa(self): return 0

    def popis(self, broj_osoba):
        if not self.ima: rt.popis[self.ime] = ''

    def provjera(self): return True

    def vrijeme(self): return 0

ulaz = '''

--NAAAJBOLJA PIZZA NA SVIJETU!!!1--

-SASTOJCI ZA 2-

503 g tijesto

    -SASTOJCI-

    300 g brašno--ima--

    200 ml voda --pukla cijev pred
                 zgradom, kupiti--

    kvasac--ima-- sol --ima--3 g šećer

    -PRIPREMA-

    odležati 60 minuta --hmmm... ja ili tijesto?--

405 g umak

    -SASTOJCI-

    400 g pelati sol 5 g šećer

    bosiljak --ima----barem se nadam da je to u fridžu bosiljak--

    -PRIPREMA-

    krčkati 15 minuta

300 g sir   --ima--

-PRIPREMA-

peći 10 minuta

'''

rec(ulaz)
prikaz(P(ulaz))
if P(ulaz).provjera(): print('OK', end=' --- ') 
else: print('NOTOK', end=' --- ')
print(P(ulaz).vrijeme(), end=' --- ')
print(', '.join(f'{ime.sadržaj} {količina}'.rstrip()
                   for ime, količina in P(ulaz).popis()))

