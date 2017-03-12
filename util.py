import random, itertools, operator, types, pprint, contextlib, collections
import textwrap, string, pdb, copy, abc

def djeljiv(m, n):
    """Je li m djeljiv s n?"""
    return not m % n

def ispiši(automat):
    """Relativno uredan ispis (nedeterminističkog) konačnog automata."""
    pprint.pprint(automat.komponente)

def Kartezijev_produkt(*skupovi):
    """Skup uređenih n-torki."""
    return set(itertools.product(*skupovi))

def funkcija(f, domena, kodomena):
    """Je li f:domena->kodomena?"""
    return f.keys() == domena and set(f.values()) <= kodomena

class fset(set):
    """Ponaša se kao frozenset, ispisuje se kao set."""
    
    def __repr__(self):
        return repr(set(self)) if self else '∅'

    def __or__(self, other):
        return fset(set(self) | set(other))

    def __and__(self, other):
        return fset(set(self) & set(other))

    def __sub__(self, other):
        return fset(set(self) - set(other))

    def __xor__(self, other):
        return fset(set(self) ^ set(other))

    __ror__, __rand__, __rsub__, __rxor__ = __or__, __and__, __sub__, __xor__

    def __hash__(self):
        return hash(frozenset(self))

    def __iand__(self, other):
        return NotImplemented

    def __ior__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return NotImplemented

    def __ixor__(self, other):
        return NotImplemented

    def add(self, value):
        raise TypeError('fset is immutable')

    def clear(self):
        raise TypeError('fset is immutable')

    def difference_update(self, other):
        raise TypeError('fset is immutable')

    def intersection_update(self, other):
        raise TypeError('fset is immutable')

    def discard(self, value):
        raise TypeError('fset is immutable')

    def pop(self):
        raise TypeError('fset is immutable')

    def remove(self, value):
        raise TypeError('fset is immutable')

    def symmetric_difference_update(self, other):
        raise TypeError('fset is immutable')

    def update(self, other):
        raise TypeError('fset is immutable')

    def difference(self, other):
        return self - other

    def intersection(self, other):
        return self & other

    def symmetric_difference(self, other):
        return self ^ other

    def union(self, other):
        return self | other

    def copy(self):
        return self

    def __dir__(self):
        return dir(frozenset)


def partitivni_skup(skup):
    """Skup svih podskupova zadanog skupa."""
    return {fset(itertools.compress(skup, χ))
            for χ in itertools.product({False, True}, repeat=len(skup))}


def relacija(R, *skupovi):
    """Je li R relacija među zadanim skupovima?"""
    return R <= Kartezijev_produkt(*skupovi)

def sažmi(vrijednost):
    """Sažimanje 1-torki u njihove elemente. Ostale n-torke ne dira."""
    with contextlib.suppress(TypeError, ValueError):
        komponenta, = vrijednost
        return komponenta
    return vrijednost

def naniži(vrijednost):
    """Pretvaranje vrijednosti koja nije n-torka u 1-torku."""
    return vrijednost if isinstance(vrijednost, tuple) else (vrijednost,)

def funkcija_iz_relacije(relacija, *domene):
    """Pretvara R⊆A×B×C×D×E (uz domene A, B) u f:A×B→℘(C×D×E)."""
    m = len(domene)
    funkcija = {sažmi(x): set() for x in Kartezijev_produkt(*domene)}
    for n_torka in relacija:
        assert len(n_torka) > m
        for x_i, domena_i in zip(n_torka, domene):
            assert x_i in domena_i
        x, y = n_torka[:m], n_torka[m:]
        if len(x) == 1: x, = x
        if len(y) == 1: y, = y
        funkcija[sažmi(x)].add(sažmi(y))
    return funkcija

def relacija_iz_funkcije(funkcija):
    """Pretvara f:A×B→℘(C×D×E) u R⊆A×B×C×D×E."""
    return {naniži(x) + naniži(y) for x, yi in funkcija.items() for y in yi}

def unija_familije(familija):
    """Unija familije skupova."""
    return fset(x for skup in familija for x in skup)

def disjunktna_unija(*skupovi):
    """Unija skupova, osiguravajući da su u parovima disjunktni."""
    for skup1, skup2 in itertools.combinations(skupovi, 2):
        assert skup1.isdisjoint(skup2)
    return set().union(*skupovi)

class Kontraprimjer(Exception):
    """Automat se ne slaže sa zadanom specifikacijom."""
    def __init__(self, test, spec):
        self.args = "Automat {}prihvaća {!r}".format('ne '*bool(spec), test),


class PrazanString(str):
    """Klasa koja određuje ponašanje objekta ε."""
    
    def __add__(self, other):
        return other

    def __mul__(self, n):
        return self

    def __len__(self):
        return 0

    def __repr__(self):
        return 'ε'

    __radd__, __rmul__, __str__ = __add__, __mul__, __repr__

ε = PrazanString()


def parsiraj_tablicu_KA(tablica):
    """Parsiranje tabličnog zapisa konačnog automata (Sipser page 36).
    Prvo stanje je početno, završna su označena znakom # na kraju reda."""
    prva, *ostale = tablica.strip().splitlines()
    znakovi = prva.split()
    assert all(len(znak) == 1 for znak in znakovi)
    abeceda = set(znakovi)
    stanja, završna = set(), set()
    prijelaz, početno = {}, None
    for linija in ostale:
        stanje, *dolazna = linija.split()
        if početno is None: početno = stanje
        extra = len(dolazna) - len(znakovi)
        assert extra in {0, 1}
        if extra == 1:
            assert dolazna.pop() == '#'
            završna.add(stanje)
        for znak, dolazno in zip(znakovi, dolazna):
            prijelaz[stanje, znak] = dolazno
        stanja.add(stanje)
    return stanja, abeceda, prijelaz, početno, završna

def parsiraj_tablicu_NKA(tablica):
    """Parsiranje tabličnog zapisa nedeterminističkog KA (Sipser page 54).
    Prvo stanje je početno, završna su označena znakom # na kraju reda.
    ε-prijelazi su nakon svih znak-prijelaza (stupac čije zaglavlje nema znaka).
    Izostanak prijelaza označava se znakom / na odgovarajućem mjestu.
    Višestruki prijelazi za isto stanje i znak razdvojeni su znakom /."""
    prva, *ostale = tablica.strip().splitlines()
    znakovi = prva.split()
    assert all(len(znak) == 1 for znak in znakovi)
    abeceda = set(znakovi)
    stanja, završna = set(), set()
    prijelaz, početno = set(), None
    for linija in ostale:
        stanje, *dolazna = linija.split()
        if početno is None: početno = stanje
        extra = len(dolazna) - len(znakovi)
        assert extra >= 0
        if extra > 0 and dolazna[~0] == '#':
            del dolazna[~0]
            završna.add(stanje)
        for znak, dolazno in zip(znakovi, dolazna):
            for dolazno1 in filter(None, dolazno.split('/')):
                prijelaz.add((stanje, znak, dolazno1))
        for dolazno in dolazna[len(znakovi):]:
            for dolazno2 in dolazno.split('/'):
                prijelaz.add((stanje, ε, dolazno2))
        stanja.add(stanje)
    return stanja, abeceda, prijelaz, početno, završna


def slučajni_testovi(automat, koliko=None, maxduljina=None):
    """Generator slučajno odabranih riječi nad abecedom automata."""
    znakovi = list(automat.abeceda)
    yield ε
    for znak in znakovi:
        yield znak,
    if maxduljina is None: maxduljina = max(len(automat.stanja), 5)
    if koliko is None: koliko = min(max(len(znakovi) ** maxduljina, 99), 9999)
    for _ in range(koliko):
        duljina = random.randint(2, maxduljina)
        yield tuple(random.choice(znakovi) for _ in range(duljina))

def provjeri(automat, specifikacija, koliko=None, maxduljina=None):
    """Osigurava da se automat drži specifikacije, slučajnim testiranjem."""
    import RI
    if isinstance(automat, RI.RegularanIzraz):
        automat = automat.NKA()
        if koliko is None:
            koliko = 99
    for test in slučajni_testovi(automat, koliko, maxduljina):
        lijevo = automat.prihvaća(test)
        if isinstance(test, tuple) and all(
            isinstance(znak, str) and len(znak) == 1 for znak in test):
                test = ''.join(test)
        desno = specifikacija(test)
        if lijevo != bool(desno):
            raise Kontraprimjer(test, desno)

def označi1(stanje, *ls):
    """Dodaje oznaci stanja dodatne oznake u ls."""
    return naniži(stanje) + ls

def novo(prefiks, iskorišteni):
    """Novi element koji počinje prefiksom i ne pripada skupu iskorišteni."""
    if prefiks in iskorišteni:
        for broj in itertools.count():
            kandidat = prefiks + str(broj)
            if kandidat not in iskorišteni:
                return kandidat
    return prefiks


def DOT_NKA(nka):
    """Dijagram danog NKA u DOT formatu. ε se piše kao e.""" 
    Q, Σ, Δ, q0, F = nka.komponente
    r = {q:i for i, q in enumerate(Q, 1)}
    obrazac = [
        'digraph {',
        'rankdir = LR',
        'node [ style = invis ] 0',
        'node [ style = solid ]',
    ]
    for oznaka, broj in r.items():
        obrazac.append('node [ peripheries={}, label="{}" ] {}'
            .format(2 if oznaka in F else 1, oznaka, broj))
    obrazac.append('0 -> ' + str(r[q0]))
    brid = collections.defaultdict(set)
    for p, α, q in Δ:
        brid[p, q].add(α)
    for (p, q), znakovi in brid.items():
        obrazac.append('{} -> {} [ label="{}" ]'
            .format(r[p], r[q], ','.join(map(str, znakovi))))
    obrazac.append('}')
    return '\n'.join(obrazac).replace('ε', 'e')
