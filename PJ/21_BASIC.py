"""Zadaća 2020. https://youtu.be/1JELGXoKSiI"""


from vepar import *
import fractions


class T(TipoviTokena):
    PLUS, MINUS, PUTA, KROZ = '+-×÷'
    MANJE, VEĆE, JEDNAKO, OTV, ZATV = '<>=()'
    UNOS, ISPIS, UBROJ, UTEKST = 'unos', 'ispis', 'broj', 'tekst$'
    ZA, DO, SLJEDEĆI = 'za', 'do', 'sljedeći'
    AKO, INAČE, NADALJE = 'ako', 'inače', 'nadalje'
    class BROJ(Token):
        def vrijednost(self, mem): return fractions.Fraction(self.sadržaj)
    class TEKST(Token):
        def vrijednost(self, mem): return self.sadržaj[1:-1]
    class BVAR(Token):
        def vrijednost(self, mem): return mem[self]
    class TVAR(Token):
        def vrijednost(self, mem): return mem[self]


def basic(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            default = T.TVAR if lex >= '$' else T.BVAR
            yield lex.literal(default, case=False)
        elif znak == ',':
            lex.pročitaj_do("'")
            yield lex.token(T.TEKST)
        elif znak == "'":
            lex.pročitaj_do("'")
            lex.zanemari()
        else: yield lex.literal(T)


### BKG
# start = naredbe -> naredba*
# naredba -> pridruživanje | petlja | unos | ispis | grananje
# pridruživanje -> BVAR JEDNAKO broj | TVAR JEDNAKO tekst
# broj -> račun usporedba+ račun | račun | tekst JEDNAKO tekst
# usporedba -> MANJE | VEĆE | JEDNAKO
# račun -> član | račun PLUS član | račun MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | BVAR | OTV broj ZATV | UBROJ OTV tekst ZATV
# tekst -> TEKST | TVAR | tekst PLUS tekst | UTEKST OTV broj ZATV
# petlja -> ZA BVAR# JEDNAKO broj DO broj naredbe SLJEDEĆI BVAR#
# unos -> UNOS BVAR | UNOS TVAR
# ispis -> ISPIS broj | ISPIS tekst | ISPIS SLJEDEĆI
# grananje -> AKO broj naredbe (INAČE naredbe)? NADALJE?


class P(Parser):
    lexer = basic
    def start(self): return Program(self.naredbe())

    def naredbe(self):
        lista = []
        while True:
            if self > {T.BVAR, T.TVAR}: lista.append(self.pridruživanje())
            elif self > T.ZA: lista.append(self.petlja())
            elif self > T.UNOS: lista.append(self.unos())
            elif self > T.ISPIS: lista.append(self.ispis())
            elif self > T.AKO: lista.append(self.grananje())
            else: return lista

    def pridruživanje(self):
        varijabla = self >> {T.BVAR, T.TVAR}
        self >> T.JEDNAKO
        if varijabla ^ T.BVAR: pridruženo = self.broj()
        elif varijabla ^ T.TVAR: pridruženo = self.tekst()
        return Pridruživanje(varijabla, pridruženo)

    def petlja(self):
        self >> T.ZA
        varijabla = self >> T.BVAR
        self >> T.JEDNAKO
        početak = self.broj()
        self >> T.DO
        kraj = self.broj()
        tijelo = self.naredbe()
        self >> T.SLJEDEĆI
        if varijabla != (self >> T.BVAR):
            raise SemantičkaGreška('Varijable u petlji se ne podudaraju')
        return Petlja(varijabla, početak, kraj, tijelo)

    def unos(self):
        self >> T.UNOS
        return Unos(self >> {T.BVAR, T.TVAR})

    def ispis(self):
        self >> T.ISPIS
        if self > {T.BROJ, T.BVAR, T.OTV, T.UBROJ}: što = self.broj()
        elif self > {T.TEKST, T.TVAR, T.UTEKST}: što = self.tekst()
        else: što = self >> T.SLJEDEĆI
        return Ispis(što)
    
    def grananje(self):
        self >> T.AKO
        uvjet = self.broj()
        onda = self.naredbe()
        inače = []
        if self >= T.INAČE: inače = self.naredbe()
        self >> {T.NADALJE, KRAJ}
        return Grananje(uvjet, onda, inače)

    def broj(self):
        if self > {T.BROJ, T.BVAR, T.OTV, T.UBROJ}:
            prvi = self.račun()
            usporedba = {T.MANJE, T.VEĆE, T.JEDNAKO}
            manje = veće = jednako = nenavedeno
            if self > usporedba:
                while u := self >= usporedba:
                    if u ^ T.MANJE: manje = u
                    elif u ^ T.VEĆE: veće = u
                    elif u ^ T.JEDNAKO: jednako = u
                return Usporedba(prvi, self.račun(), manje, veće, jednako)
            else: return prvi
        else:
            prvi = self.tekst()
            self >> T.JEDNAKO
            drugi = self.tekst()
            return JednakTekst(prvi, drugi)

    def račun(self):
        t = self.član()
        while op := self >= {T.PLUS, T.MINUS}: t = Osnovna(op, t, self.član())
        return t

    def član(self):
        t = self.faktor()
        while op := self >= {T.PUTA, T.KROZ}: t = Osnovna(op, t, self.faktor())
        return t

    def faktor(self):
        if self >= T.OTV:
            u_zagradi = self.broj()
            self >> T.ZATV
            return u_zagradi
        elif self >= T.UBROJ:
            self >> T.OTV
            argument = self.tekst()
            self >> T.ZATV
            return TekstUBroj(argument)
        else: return self >> {T.BROJ, T.BVAR}

    def tekst(self):
        if self >= T.UTEKST:
            self >> T.OTV
            trenutni = BrojUTekst(self.broj())
            self >> T.ZATV
        else: trenutni = self >> {T.TEKST, T.TVAR}
        if self >= T.PLUS: return Konkatenacija(trenutni, self.tekst())
        else: return trenutni


### AST
# Program: naredbe:[naredba]
# naredba: Unos: varijabla:BVAR|TVAR
#          Ispis: što:broj|tekst|SLJEDEĆI
#          Pridruživanje: varijabla:BVAR|!TVAR što:broj|!tekst
#          Petlja: varijabla:BVAR početak:broj kraj:broj tijelo:[naredba]
#          Grananje: uvjet:broj onda:[naredba] inače:[naredba]
# broj: JednakTekst: lijevo:tekst desno:tekst
#       Usporedba: lijevo:broj desno:broj 
#                  manje:MANJE? veće:VEĆE? jednako:JEDNAKO?
#       Osnovna: operacija:PLUS|MINUS|PUTA|KROZ lijevo:broj desno:broj
#       TekstUBroj: tekst:tekst
#       BROJ: Token
#       BVAR: Token
# tekst: BrojUTekst: broj:broj
#        Konkatenacija: lijevo:tekst desno:tekst
#        TEKST: Token
#        TVAR: Token

class Program(AST):
    naredbe: 'naredba*'
    def izvrši(self):
        mem = Memorija()
        for naredba in self.naredbe: naredba.izvrši(mem)

class Unos(AST):
    varijabla: 'BVAR|TVAR'
    def izvrši(self, mem):
        v = self.varijabla
        prompt = f'\t{v.sadržaj}? '
        if v ^ T.TVAR: mem[v] = input(prompt)
        elif v ^ T.BVAR:
            while True:
                t = input(prompt)
                try: mem[v] = fractions.Fraction(t.replace('÷', '/'))
                except ValueError: print(end='To nije racionalni broj! ')
                else: break
        else: assert False, f'Nepoznat tip varijable {v}'

class Ispis(AST):
    što: 'broj|tekst|SLJEDEĆI'
    def izvrši(self, mem):
        if self.što ^ T.SLJEDEĆI: print()
        else: 
            t = self.što.vrijednost(mem)
            if isinstance(t, fractions.Fraction): t = str(t).replace('/', '÷')
            print(t, end=' ')

class Pridruživanje(AST):
    varijabla: 'BVAR|!TVAR'
    što: 'broj|!tekst'
    def izvrši(self, mem): mem[self.varijabla] = self.što.vrijednost(mem)

class Petlja(AST):
    varijabla: 'BVAR'
    početak: 'broj'
    kraj: 'broj'
    tijelo: 'naredba*'
    def izvrši(self, mem):
        kv = self.varijabla
        p, k = self.početak.vrijednost(mem), self.kraj.vrijednost(mem)
        korak = 1 if p <= k else -1
        mem[kv] = p
        while (mem[kv] - k) * korak <= 0:
            for naredba in self.tijelo: naredba.izvrši(mem)
            mem[kv] += korak

class Grananje(AST):
    uvjet: 'broj'
    onda: 'naredba*'
    inače: 'naredba*'
    def izvrši(self, mem):
        b = self.uvjet.vrijednost(mem)
        if b == ~0: sljedeći = self.onda
        elif b == 0: sljedeći = self.inače
        else: raise GreškaIzvođenja(f'Tertium ({b}) non datur!')
        for naredba in sljedeći: naredba.izvrši(mem)

class JednakTekst(AST):
    lijevo: 'tekst'
    desno: 'tekst'
    def vrijednost(self, mem):
        return -(self.lijevo.vrijednost(mem) == self.desno.vrijednost(mem))

class Usporedba(AST):
    lijevo: 'broj'
    desno: 'broj'
    manje: 'MANJE?'
    veće: 'VEĆE?'
    jednako: 'JEDNAKO?'
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        return -((self.manje and l < d) or (self.jednako and l == d) \
                   or (self.veće and l > d) or False)

class Osnovna(AST):
    operacija: 'T'
    lijevo: 'broj'
    desno: 'broj'
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        o = self.operacija
        if o ^ T.PLUS: return l + d
        elif o ^ T.MINUS: return l - d
        elif o ^ T.PUTA: return l * d
        elif o ^ T.KROZ:
            if d: return fractions.Fraction(l, d)
            else: raise o.iznimka('Nazivnik ne smije biti nula!')
        else: assert False, f'Nepokrivena binarna operacija {o}'

class TekstUBroj(AST):
    tekst: 'tekst'
    def vrijednost(self, mem):
        arg = self.tekst.vrijednost(mem)
        try: return fractions.Fraction(arg.replace('÷', '/'))
        except ValueError: raise GreškaIzvođenja(f'{arg!r} nije broj')

class BrojUTekst(AST):
    broj: 'broj'
    def vrijednost(self, mem): 
        return str(self.broj.vrijednost(mem)).replace('/', '÷')

class Konkatenacija(AST):
    lijevo: 'tekst'
    desno: 'tekst'
    def vrijednost(self, mem):
        return self.lijevo.vrijednost(mem) + self.desno.vrijednost(mem)


ast = P('''\
    ispis sljedeći ispis ,Gaußova dosjetka' ispis sljedeći
    crtice$ = ,'
    za i=1 do 16
      crtice$ = crtice$ + ,-'
    sljedeći i
    ispis crtice$ ispis sljedeći 
    ispis ,Prirodni broj'
    unos n
    ako n = < 0 
      ispis ,To nije prirodni broj! Više sreće drugi put.'
      ispis sljedeći inače 'ovaj "inače" se odnosi na čitav ostatak programa'
    rješenje =
                                 n×(n+1) ÷ 2

    ispis ,Zbroj prvih' ispis n ispis ,prirodnih brojeva' 
    ispis ,iznosi' ispis tekst$(rješenje) + ,,' ispis sljedeći
    ispis ,što se može provjeriti i ručno:' ispis sljedeći
    zbroj = 0
    za pribrojnik=1 do n
      ako pribrojnik > 1 ispis ,+'
      nadalje
      ispis pribrojnik
      zbroj = zbroj + pribrojnik
    sljedeći pribrojnik
    ispis ,=' ispis zbroj ispis sljedeći
    ako zbroj = rješenje 
      ispis ,Kao što vidimo, Gaußova dosjetka funkcionira.' ispis sljedeći
    inače ispis ,Hm, nešto nije u redu. Obratite se administratoru Svemira.'
    ispis sljedeći
''')
prikaz(ast)
ast.izvrši()
