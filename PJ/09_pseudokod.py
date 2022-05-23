"""Interpreter za pseudokod, s funkcijskim pozivima i dva tipa podataka.

Podržane naredbe:
    ako je Uvjet naredba inače naredba      ime = izraz
    ako je Uvjet naredba                    Ime = Uvjet
    ako nije Uvjet naredba                  vrati izraz
    dok je Uvjet naredba                    vrati Uvjet
    dok nije Uvjet naredba                  (naredba1, naredba2, ...)
Podržani aritmetički izrazi:            Podržani logički uvjeti:
    cijeli_broj                             Istina
    ime                                     Laž
    ime(argumenti)                          Ime
    izraz + izraz                           Ime(argumenti)
    izraz - izraz                           Uvjet Ili Uvjet
    izraz * izraz                           izraz < izraz
    -izraz                                  izraz = izraz
    (izraz)

Program se sastoji od jedne ili više deklaracija funkcija, s ili bez parametara.
    Jedna od njih mora biti program(parametri), od nje počinje izvršavanje.
Tipovi varijabli (i povratni tipovi funkcija) se reprezentiraju leksički:
    * veliko početno slovo označava logički tip (u Pythonu bool)
    * malo početno slovo označava aritmetički tip (u Pythonu int)
Minimalni kontekst je potreban da bismo zapamtili jesmo li trenutno u definiciji
    aritmetičke ili logičke funkcije, kako bi naredba "vrati" znala što očekuje.
Dozvoljeni su i (ne uzajamno!) rekurzivni pozivi, tako da se za vrijeme 
    parsiranja i izvršavanja prati u kojoj smo funkciji.
Memorija se također dinamički preoblikuje: svaka funkcija ima svoj prostor."""


from vepar import *


class T(TipoviTokena):
    AKO, DOK, INAČE, VRATI = 'ako', 'dok', 'inače', 'vrati'
    JE, NIJE, ILI = 'je', 'nije', 'Ili'
    OTV, ZATV, ZAREZ, JEDNAKO, MANJE, PLUS, MINUS, ZVJEZDICA = '(),=<+-*'

    class AIME(Token):
        def vrijednost(self, mem, unutar): return mem[self]

    class LIME(AIME): pass

    class BROJ(Token):
        def vrijednost(self, mem, unutar): return int(self.sadržaj)

    class ISTINA(Token):
        literal = 'Istina'
        def vrijednost(self, mem, unutar): return True

    class LAŽ(Token):
        literal = 'Laž'
        def vrijednost(self, mem, unutar): return False

@lexer
def pseudokod(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.islower():
            lex * str.isalnum
            yield lex.literal_ili(T.AIME)
        elif znak.isupper():
            lex * str.isalnum
            yield lex.literal_ili(T.LIME)
        elif znak.isdecimal():
            lex.prirodni_broj(znak)
            yield lex.token(T.BROJ)
        elif znak == '#':
            lex - '\n'
            lex.zanemari()
        else: yield lex.literal(T)


### ne sasvim BKG
# program -> funkcija | funkcija program
# funkcija -> ime OTV parametri? ZATV JEDNAKO naredba
# parametri -> ime | parametri ZAREZ ime
# ime -> AIME | LIME
# naredba -> pridruži | OTV ZATV | OTV naredbe ZATV | VRATI argument
#         | (AKO|DOK) (JE|NIJE) log naredba | AKO JE log naredba INAČE naredba
# naredbe -> naredba | naredbe ZAREZ naredba
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> disjunkt | log ILI disjunkt
# disjunkt -> aritm MANJE aritm | aritm JEDNAKO aritm 
#         | ISTINA | LAŽ | LIME | LIME poziv
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član ZVJEZDICA faktor
# faktor -> BROJ | AIME | AIME poziv | OTV aritm ZATV | MINUS faktor
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> aritm |! log  [!KONTEKST]

class P(Parser):
    def program(p) -> 'Memorija':
        p.funkcije = Memorija(redefinicija=False)
        while not p > KRAJ:
            funkcija = p.funkcija()
            p.funkcije[funkcija.ime] = funkcija
        return p.funkcije

    def funkcija(p) -> 'Funkcija':
        atributi = p.imef, p.parametrif = p.ime(), p.parametri()
        p >> T.JEDNAKO
        return Funkcija(*atributi, p.naredba())

    def ime(p) -> 'AIME|LIME': return p >> {T.AIME, T.LIME}

    def parametri(p) -> 'ime*':
        p >> T.OTV
        if p >= T.ZATV: return []
        param = [p.ime()]
        while p >= T.ZAREZ: param.append(p.ime())
        p >> T.ZATV
        return param

    def naredba(p) -> 'grananje|petlja|blok|Vrati|Pridruživanje':
        if p > T.AKO: return p.grananje()
        elif p > T.DOK: return p.petlja()
        elif p > T.OTV: return p.blok()
        elif p >= T.VRATI: return Vrati(p.tipa(p.imef))
        else:
            ime = p.ime()
            p >> T.JEDNAKO
            return Pridruživanje(ime, p.tipa(ime))

    def tipa(p, ime) -> 'aritm|log':
        if ime ^ T.AIME: return p.aritm()
        elif ime ^ T.LIME: return p.log()
        else: assert False, f'Nepoznat tip od {ime}'
        
    def grananje(p) -> 'Grananje':
        p >> T.AKO
        je = p > T.JE
        atributi = p >> {T.JE, T.NIJE}, p.log(), p.naredba()
        if je and p >= T.INAČE: inače = p.naredba()
        else: inače = Blok([])
        return Grananje(*atributi, inače)

    def petlja(p) -> 'Petlja':
        p >> T.DOK
        return Petlja(p >> {T.JE, T.NIJE}, p.log(), p.naredba())

    def blok(p) -> 'Blok|naredba':
        p >> T.OTV
        if p >= T.ZATV: return Blok([])
        n = [p.naredba()]
        while p >= T.ZAREZ and not p > T.ZATV: n.append(p.naredba())
        p >> T.ZATV
        return Blok.ili_samo(n)

    def log(p) -> 'Disjunkcija|disjunkt':
        disjunkti = [p.disjunkt()]
        while p >= T.ILI: disjunkti.append(p.disjunkt())
        return Disjunkcija.ili_samo(disjunkti)

    def disjunkt(p) -> 'možda_poziv|Usporedba':
        if log := p >= {T.ISTINA, T.LAŽ, T.LIME}: return p.možda_poziv(log)
        return Usporedba(p.aritm(), p >> {T.JEDNAKO, T.MANJE}, p.aritm())

    def možda_poziv(p, ime) -> 'Poziv|ime':
        if ime in p.funkcije:
            funkcija = p.funkcije[ime]
            return Poziv(funkcija, p.argumenti(funkcija.parametri))
        elif ime == p.imef:
            return Poziv(nenavedeno, p.argumenti(p.parametrif))
        else: return ime

    def argumenti(p, parametri) -> 'tipa*':
        arg = []
        p >> T.OTV
        for i, parametar in enumerate(parametri):
            if i: p >> T.ZAREZ
            arg.append(p.tipa(parametar))
        p >> T.ZATV
        return arg
    
    def aritm(p) -> 'Zbroj|član':
        članovi = [p.član()]
        while ...:
            if p >= T.PLUS: članovi.append(p.član())
            elif p >= T.MINUS: članovi.append(Suprotan(p.član()))
            else: return Zbroj.ili_samo(članovi)

    def član(p) -> 'Umnožak|faktor':
        faktori = [p.faktor()]
        while p >= T.ZVJEZDICA: faktori.append(p.faktor())
        return Umnožak.ili_samo(faktori)

    def faktor(p) -> 'Suprotan|možda_poziv|aritm|BROJ':
        if p >= T.MINUS: return Suprotan(p.faktor())
        elif aritm := p >= T.AIME: return p.možda_poziv(aritm)
        elif p >= T.OTV:
            u_zagradi = p.aritm()
            p >> T.ZATV
            return u_zagradi
        else: return p >> T.BROJ


def izvrši(funkcije, *argv):
    print('Program je vratio:', funkcije['program'].pozovi(argv))


### AST
# Funkcija: ime:AIME|LIME parametri:[IME] tijelo:naredba
# naredba: Grananje: istinitost:JE|NIJE uvjet:log onda:naredba inače:naredba
#          Petlja: istinitost:JE|NIJE uvjet:log tijelo:naredba
#          Blok: naredbe:[naredba]
#          Pridruživanje: ime:AIME|LIME pridruženo:izraz
#          Vrati: što:izraz
# izraz: log: Disjunkcija: disjunkti:[log]
#             Usporedba: lijevo:aritm relacija:MANJE|JEDNAKO desno:aritm
#        aritm: Zbroj: pribrojnici:[aritm]
#               Suprotan: od:aritm
#               Umnožak: faktori:[aritm]
#        Poziv: funkcija:Funkcija? argumenti:[izraz]

class Funkcija(AST):
    ime: 'IME'
    parametri: 'IME*'
    tijelo: 'naredba'
    def pozovi(funkcija, argumenti):
        lokalni = Memorija(zip(funkcija.parametri, argumenti))
        try: funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
        except Povratak as exc: return exc.preneseno
        else: raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')

class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'
    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno: pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        return pozvana.pozovi(argumenti)

    def za_prikaz(poziv):  # samo za ispis, da se ne ispiše čitava funkcija
        r = {'argumenti': poziv.argumenti}
        if poziv.funkcija is nenavedeno: r['*rekurzivni'] = True
        else: r['*ime'] = poziv.funkcija.ime
        return r

def ispunjen(ast, mem, unutar):
    u = ast.uvjet.vrijednost(mem, unutar)
    if ast.istinitost ^ T.JE: return u
    elif ast.istinitost ^ T.NIJE: return not u
    else: assert False, f'Tertium non datur! {ast.istinitost}'

class Grananje(AST):
    istinitost: 'JE|NIJE'
    uvjet: 'log'
    onda: 'naredba'
    inače: 'naredba'
    def izvrši(grananje, mem, unutar):
        if ispunjen(grananje, mem, unutar): grananje.onda.izvrši(mem, unutar)
        else: grananje.inače.izvrši(mem, unutar)

class Petlja(AST):
    istinitost: 'JE|NIJE'
    uvjet: 'log'
    tijelo: 'naredba'
    def izvrši(petlja, mem, unutar):
        while ispunjen(petlja, mem, unutar): petlja.tijelo.izvrši(mem, unutar)

class Blok(AST):
    naredbe: 'naredba*'
    def izvrši(blok, mem, unutar):
        for naredba in blok.naredbe: naredba.izvrši(mem, unutar)

class Pridruživanje(AST):
    ime: 'IME'
    pridruženo: 'izraz'
    def izvrši(self, mem, unutar):
        mem[self.ime] = self.pridruženo.vrijednost(mem, unutar)

class Vrati(AST):
    što: 'izraz'
    def izvrši(self, mem, unutar):
        raise Povratak(self.što.vrijednost(mem, unutar))

class Disjunkcija(AST):
    disjunkti: 'log*'
    def vrijednost(disjunkcija, mem, unutar):
        return any(disjunkt.vrijednost(mem, unutar)
                for disjunkt in disjunkcija.disjunkti)
    
class Usporedba(AST):
    lijevo: 'aritm'
    relacija: 'MANJE|JEDNAKO'
    desno: 'aritm'
    def vrijednost(usporedba, mem, unutar):
        l = usporedba.lijevo.vrijednost(mem, unutar)
        d = usporedba.desno.vrijednost(mem, unutar)
        if usporedba.relacija ^ T.JEDNAKO: return l == d
        elif usporedba.relacija ^ T.MANJE: return l < d
        else: assert False, f'Nepoznata relacija {usporedba.relacija}'

class Zbroj(AST):
    pribrojnici: 'aritm*'
    def vrijednost(zbroj, mem, unutar):
        return sum(p.vrijednost(mem, unutar) for p in zbroj.pribrojnici)
    
class Suprotan(AST):
    od: 'aritm'
    def vrijednost(self, mem, unutar): return -self.od.vrijednost(mem, unutar)
    
class Umnožak(AST):
    faktori: 'aritm*'
    def vrijednost(umnožak, mem, unutar):
        return math.prod(f.vrijednost(mem, unutar) for f in umnožak.faktori)


class Povratak(NelokalnaKontrolaToka): """Signal koji šalje naredba vrati."""


proba = P('program() = ako je Istina vrati 1 inače vrati 2')
prikaz(proba, 5)
izvrši(proba)

with SemantičkaGreška: P('f(x)=() f(x)=()')
with SintaksnaGreška:
    P('f(x) = vrati 7    program() = vrati f(Laž)')
with SintaksnaGreška: izvrši(P('program() = vrati2'))
with LeksičkaGreška: P('program() = vrati 007')

modul = '''
Negacija(V) = ako je V vrati Laž inače vrati Istina
Neparan(x) = (
    N = Laž,
    dok nije x = 0 (
        x = x - 1,
        N = Negacija(N),
    ),
    vrati N
)
'''
suma_faktorijela = P(modul + '''
fakt(x) = (
    f = 1,
    dok nije x = 0 (
        f = f*x,
        x = x-1
    ),
    vrati f
)
program() = (
    s = 0,
    t = 0,
    dok je t < 9 (
        ako je Neparan(t) s = s + fakt(t),
        t = t + 1
    ),
    vrati s
)
''')
prikaz(suma_faktorijela)
izvrši(suma_faktorijela)

tablice_istinitosti = P(modul + '''
Konjunkcija(P, Q) = ako je P vrati Q inače vrati P
Disjunkcija(P, Q) = ako je P vrati P inače vrati Q
Kondicional(P, Q) = vrati Disjunkcija(Negacija(P), Q)
Bikondicional(P, Q) = vrati Konjunkcija(Kondicional(P, Q), Kondicional(Q, P))
Multiplex(m, P, Q) =  # rudimentarni switch/case
    ako je m = 1 vrati Konjunkcija(P, Q)   inače
    ako je m = 2 vrati Disjunkcija(P, Q)   inače
    ako je m = 3 vrati Kondicional(P, Q)   inače
    ako je m = 4 vrati Bikondicional(P, Q) inače
    ako je m = 5 vrati Negacija(P)         inače
                 vrati Laž
broj(Bool) = ako je Bool vrati 1 inače vrati 0
dodaj(lista, Bool) = (
    bit = broj(Bool),
    lista = lista * 10 + bit,
    lista = lista * 10 + 8,
    vrati lista
)
program(m) = (
    lista = 6,
    b = 0,
    dok je b < 4 (
        Prvi = Negacija(b < 2),
        Drugi = Neparan(b),
        Rezultat = Multiplex(m, Prvi, Drugi),
        lista = dodaj(lista, Rezultat),
        b = b + 1
    ),
    vrati lista + 1
)
''')
print()
prikaz(tablice_istinitosti)
izvrši(tablice_istinitosti, 3)  # poziv iz komandne linije, prijenos m=3
print()

rekurzivna = P('''
    fakt(n) = ako je n = 0 vrati 1 inače vrati n*fakt(n-1)
    program() = vrati fakt(7)
''')
prikaz(rekurzivna)
izvrši(rekurzivna)


# DZ: dodajte određenu petlju: za ime = izraz .. izraz naredba
# DZ*: dodajte late binding, da se modul i program mogu zasebno kompajlirati
