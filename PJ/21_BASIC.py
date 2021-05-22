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
        def vrijednost(t, mem): return fractions.Fraction(t.sadržaj)
    class TEKST(Token):
        def vrijednost(t, mem): return t.sadržaj[1:-1]
    class BVAR(Token):
        def vrijednost(t, mem): return mem[t]
    class TVAR(Token):
        def vrijednost(t, mem): return mem[t]


def basic(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak.isalpha():
            lex * str.isalnum
            default = T.TVAR if lex >= '$' else T.BVAR
            yield lex.literal(default, case=False)
        elif znak == ',':
            lex - "'"
            yield lex.token(T.TEKST)
        elif znak == "'":
            lex - "'"
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
    def start(p): return Program(p.naredbe())

    def naredbe(p):
        lista = []
        while ...:
            if p > {T.BVAR, T.TVAR}: lista.append(p.pridruživanje())
            elif p > T.ZA: lista.append(p.petlja())
            elif p > T.UNOS: lista.append(p.unos())
            elif p > T.ISPIS: lista.append(p.ispis())
            elif p > T.AKO: lista.append(p.grananje())
            else: return lista

    def pridruživanje(p):
        varijabla = p >> {T.BVAR, T.TVAR}
        p >> T.JEDNAKO
        if varijabla ^ T.BVAR: pridruženo = p.broj()
        elif varijabla ^ T.TVAR: pridruženo = p.tekst()
        return Pridruživanje(varijabla, pridruženo)

    def petlja(p):
        p >> T.ZA
        varijabla = p >> T.BVAR
        p >> T.JEDNAKO
        početak = p.broj()
        p >> T.DO
        kraj = p.broj()
        tijelo = p.naredbe()
        p >> T.SLJEDEĆI
        if varijabla != (p >> T.BVAR):
            raise SemantičkaGreška('Varijable u petlji se ne podudaraju')
        return Petlja(varijabla, početak, kraj, tijelo)

    def unos(p):
        p >> T.UNOS
        return Unos(p >> {T.BVAR, T.TVAR})

    def ispis(p):
        p >> T.ISPIS
        if p > {T.BROJ, T.BVAR, T.OTV, T.UBROJ}: što = p.broj()
        elif p > {T.TEKST, T.TVAR, T.UTEKST}: što = p.tekst()
        else: što = p >> T.SLJEDEĆI
        return Ispis(što)
    
    def grananje(p):
        p >> T.AKO
        uvjet = p.broj()
        onda = p.naredbe()
        inače = []
        if p >= T.INAČE: inače = p.naredbe()
        p >> {T.NADALJE, KRAJ}
        return Grananje(uvjet, onda, inače)

    def broj(p):
        if p > {T.BROJ, T.BVAR, T.OTV, T.UBROJ}:
            prvi = p.račun()
            usporedba = {T.MANJE, T.VEĆE, T.JEDNAKO}
            manje = veće = jednako = nenavedeno
            if p > usporedba:
                while u := p >= usporedba:
                    if u ^ T.MANJE: manje = u
                    elif u ^ T.VEĆE: veće = u
                    elif u ^ T.JEDNAKO: jednako = u
                return Usporedba(prvi, p.račun(), manje, veće, jednako)
            else: return prvi
        else:
            prvi = p.tekst()
            p >> T.JEDNAKO
            drugi = p.tekst()
            return JednakTekst(prvi, drugi)

    def račun(p):
        t = p.član()
        while op := p >= {T.PLUS, T.MINUS}: t = Osnovna(op, t, p.član())
        return t

    def član(p):
        t = p.faktor()
        while op := p >= {T.PUTA, T.KROZ}: t = Osnovna(op, t, p.faktor())
        return t

    def faktor(p):
        if p >= T.OTV:
            u_zagradi = p.broj()
            p >> T.ZATV
            return u_zagradi
        elif p >= T.UBROJ:
            p >> T.OTV
            argument = p.tekst()
            p >> T.ZATV
            return TekstUBroj(argument)
        else: return p >> {T.BROJ, T.BVAR}

    def tekst(p):
        if p >= T.UTEKST:
            p >> T.OTV
            trenutni = BrojUTekst(p.broj())
            p >> T.ZATV
        else: trenutni = p >> {T.TEKST, T.TVAR}
        if p >= T.PLUS: return Konkatenacija(trenutni, p.tekst())
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
    def izvrši(program):
        mem = Memorija()
        for naredba in program.naredbe: naredba.izvrši(mem)

class Unos(AST):
    varijabla: 'BVAR|TVAR'
    def izvrši(unos, mem):
        v = unos.varijabla
        prompt = f'\t{v.sadržaj}? '
        if v ^ T.TVAR: mem[v] = input(prompt)
        elif v ^ T.BVAR:
            while ...:
                t = input(prompt)
                try: mem[v] = fractions.Fraction(t.replace('÷', '/'))
                except ValueError: print(end='To nije racionalni broj! ')
                else: break
        else: assert False, f'Nepoznat tip varijable {v}'

class Ispis(AST):
    što: 'broj|tekst|SLJEDEĆI'
    def izvrši(ispis, mem):
        if ispis.što ^ T.SLJEDEĆI: print()
        else: 
            t = ispis.što.vrijednost(mem)
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
    def izvrši(petlja, mem):
        kv = petlja.varijabla
        p, k = petlja.početak.vrijednost(mem), petlja.kraj.vrijednost(mem)
        korak = 1 if p <= k else -1
        mem[kv] = p
        while (mem[kv] - k) * korak <= 0:
            for naredba in petlja.tijelo: naredba.izvrši(mem)
            mem[kv] += korak

class Grananje(AST):
    uvjet: 'broj'
    onda: 'naredba*'
    inače: 'naredba*'
    def izvrši(grananje, mem):
        b = grananje.uvjet.vrijednost(mem)
        if b == ~0: sljedeći = grananje.onda
        elif b == 0: sljedeći = grananje.inače
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
        return -((self.manje and l < d) or (self.jednako and l == d)
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


ast = P('''
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
