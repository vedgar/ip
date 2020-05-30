from pj import *
import fractions

class B(enum.Enum):
    ZA, DO, SLJEDEĆI = 'za', 'do', 'sljedeći'
    PLUS, MINUS, PUTA, KROZ = '+-×÷'
    UNOS, ISPIS, UBROJ, UTEKST = 'unos', 'ispis', 'broj', 'tekst$'
    MANJE, VEĆE, JEDNAKO, OTV, ZATV = '<>=()'
    AKO, INAČE, NADALJE = 'ako', 'inače', 'nadalje'
    class BROJ(Token):
        def vrijednost(self, mem): return fractions.Fraction(self.sadržaj)
    class BVAR(Token):
        def vrijednost(self, mem): return pogledaj(mem, self)
    class TEKST(Token):
        def vrijednost(self, mem): return self.sadržaj[1:-1]
    class TVAR(Token):
        def vrijednost(self, mem): return pogledaj(mem, self)

def blex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            if znak != '0': lex.zvijezda(str.isdecimal)
            yield lex.token(B.BROJ)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            default = B.TVAR if lex.slijedi('$') else B.BVAR
            yield lex.literal(default, case=False)
        elif znak == ',':
            lex.pročitaj_do("'")
            yield lex.token(B.TEKST)
        elif znak == "'":
            lex.pročitaj_do("'")
            lex.zanemari()
        else: yield lex.literal(B)

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


class BASICParser(Parser):
    def start(self): return Program(self.naredbe())

    def naredbe(self):
        lista = []
        while True:
            if self >= {B.BVAR, B.TVAR}: lista.append(self.pridruživanje())
            elif self >= B.ZA: lista.append(self.petlja())
            elif self >= B.UNOS: lista.append(self.unos())
            elif self >= B.ISPIS: lista.append(self.ispis())
            elif self >= B.AKO: lista.append(self.grananje())
            else: break
        return lista

    def pridruživanje(self):
        varijabla = self.pročitaj(B.BVAR, B.TVAR)
        self.pročitaj(B.JEDNAKO)
        if varijabla ^ B.BVAR: pridruženo = self.broj()
        elif varijabla ^ B.TVAR: pridruženo = self.tekst()
        return Pridruživanje(varijabla, pridruženo)

    def petlja(self):
        self.pročitaj(B.ZA)
        varijabla = self.pročitaj(B.BVAR)
        self.pročitaj(B.JEDNAKO)
        početak = self.broj()
        self.pročitaj(B.DO)
        kraj = self.broj()
        tijelo = self.naredbe()
        self.pročitaj(B.SLJEDEĆI)
        varijabla2 = self.pročitaj(B.BVAR)
        if varijabla != varijabla2:
            raise SemantičkaGreška('Varijable u petlji se ne podudaraju')
        return Petlja(varijabla, početak, kraj, tijelo)

    def unos(self):
        self.pročitaj(B.UNOS)
        return Unos(self.pročitaj(B.BVAR, B.TVAR))

    def ispis(self):
        self.pročitaj(B.ISPIS)
        if self >> B.SLJEDEĆI: što = self.zadnji
        elif self >= {B.BROJ, B.BVAR, B.OTV, B.UBROJ}: što = self.broj()
        elif self >= {B.TEKST, B.TVAR, B.UTEKST}: što = self.tekst()
        else: raise self.greška()
        return Ispis(što)
    
    def grananje(self):
        self.pročitaj(B.AKO)
        uvjet = self.broj()
        onda = self.naredbe()
        inače = []
        if self >> B.INAČE: inače = self.naredbe()
        self.pročitaj(B.NADALJE, E.KRAJ)
        return Grananje(uvjet, onda, inače)

    def broj(self):
        if self >= {B.BROJ, B.BVAR, B.OTV, B.UBROJ}:
            prvi = self.račun()
            usporedba = {B.MANJE, B.VEĆE, B.JEDNAKO}
            manje = veće = jednako = nenavedeno
            if self >= usporedba:
                while self >> usporedba:
                    u = self.zadnji
                    if u ^ B.MANJE: manje = u
                    elif u ^ B.VEĆE: veće = u
                    elif u ^ B.JEDNAKO: jednako = u
                return Usporedba(prvi, self.račun(), manje, veće, jednako)
            else: return prvi
        else:
            prvi = self.tekst()
            self.pročitaj(B.JEDNAKO)
            drugi = self.tekst()
            return JednakTekst(prvi, drugi)

    def račun(self):
        trenutni = self.član()
        while self >> {B.PLUS, B.MINUS}:
            trenutni = Osnovna(self.zadnji, trenutni, self.član())
        return trenutni

    def član(self):
        trenutni = self.faktor()
        while self >> {B.PUTA, B.KROZ}:
            trenutni = Osnovna(self.zadnji, trenutni, self.faktor())
        return trenutni

    def faktor(self):
        if self >> {B.BROJ, B.BVAR}: return self.zadnji
        elif self >> B.OTV:
            u_zagradi = self.broj()
            self.pročitaj(B.ZATV)
            return u_zagradi
        elif self >> B.UBROJ:
            self.pročitaj(B.OTV)
            argument = self.tekst()
            self.pročitaj(B.ZATV)
            return TekstUBroj(argument)
        else: raise self.greška()

    def tekst(self):
        if self >> {B.TEKST, B.TVAR}: trenutni = self.zadnji
        elif self >> B.UTEKST:
            self.pročitaj(B.OTV)
            trenutni = BrojUTekst(self.broj())
            self.pročitaj(B.ZATV)
        if self >> B.PLUS: return Konkatenacija(trenutni, self.tekst())
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

class Program(AST('naredbe')):
    def izvrši(self):
        mem = {}
        for naredba in self.naredbe: naredba.izvrši(mem)

class Unos(AST('varijabla')):
    def izvrši(self, mem):
        v = self.varijabla
        if v ^ B.TVAR: mem[v] = input('\t' + v.sadržaj + '? ')
        elif v ^ B.BVAR:
            while True:
                t = input('\t' + v.sadržaj + '? ')
                try: mem[v] = fractions.Fraction(t.replace('÷', '/'))
                except ValueError: print(end='To nije racionalni broj!')
                else: break
        else: assert False, 'Nepoznat tip varijable {}'.format(v)

class Ispis(AST('što')):
    def izvrši(self, mem):
        if self.što ^ B.SLJEDEĆI: print()
        else: 
            t = self.što.vrijednost(mem)
            if isinstance(t, fractions.Fraction): t = str(t).replace('/', '÷')
            print(t, end=' ')

class Pridruživanje(AST('varijabla što')):
    def izvrši(self, mem): mem[self.varijabla] = self.što.vrijednost(mem)

class Petlja(AST('varijabla početak kraj tijelo')):
    def izvrši(self, mem):
        kv = self.varijabla
        p, k = self.početak.vrijednost(mem), self.kraj.vrijednost(mem)
        step = 1 if p <= k else -1
        mem[kv] = p
        while (mem[kv] - k) * step <= 0:
            for naredba in self.tijelo: naredba.izvrši(mem)
            mem[kv] += step

class Grananje(AST('uvjet onda inače')):
    def izvrši(self, mem):
        b = self.uvjet.vrijednost(mem)
        if b == 1: s = self.onda
        elif b == 0: s = self.inače
        else: raise GreškaIzvođenja('Tertium ({}) non datur!'.format(b))
        for naredba in s: naredba.izvrši(mem)

class JednakTekst(AST('lijevo desno')):
    def vrijednost(self, mem):
        return self.lijevo.vrijednost(mem) == self.desno.vrijednost(mem)

class Usporedba(AST('lijevo desno manje veće jednako')):
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        return (self.manje and l < d) or (self.jednako and l == d) \
                   or (self.veće and l > d) or False

class Osnovna(AST('operacija lijevo desno')):
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        o = self.operacija
        if o ^ B.PLUS: return l + d
        elif o ^ B.MINUS: return l - d
        elif o ^ B.PUTA: return l * d
        elif o ^ B.KROZ:
            if d: return fractions.Fraction(l, d)
            else: raise o.iznimka('Nazivnik ne smije biti nula!')
        else: assert False, 'Nepokrivena binarna operacija {}'.format(o)

class TekstUBroj(AST('tekst')):
    def vrijednost(self, mem):
        arg = self.tekst.vrijednost(mem)
        try: return fractions.Fraction(arg.replace('÷', '/'))
        except ValueError: raise GreškaIzvođenja('{!r} nije broj'.format(arg))

class BrojUTekst(AST('broj')):
    def vrijednost(self, mem): 
        return str(self.broj.vrijednost(mem)).replace('/', '÷')

class Konkatenacija(AST('lijevo desno')):
    def vrijednost(self, mem):
        return self.lijevo.vrijednost(mem) + self.desno.vrijednost(mem)


ast = BASICParser.parsiraj(blex('''\
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
'''))
prikaz(ast, 11)
ast.izvrši()
