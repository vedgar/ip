from util import *
from KA import NedeterminističniKonačniAutomat as NKA


class RegularniIzraz(types.SimpleNamespace, abc.ABC):
    """Svaki RegularniIzraz predstavlja neki regularni jezik,
    dobiven pomoću operacija unije, konkatenacije te Kleenejevih operatora
    iz inicijalnih jezika (∅, ε, te elementarnih jezika)."""

    @abc.abstractmethod
    def prazan(self): """Je li jezik jednak ∅?"""

    @abc.abstractmethod
    def trivijalan(self): """Je li jezik jednak ∅ ili ε?"""

    @abc.abstractmethod
    def konačan(self): """Je li jezik konačan?"""

    @abc.abstractmethod
    def korišteni_znakovi(self): """Skup znakova korištenih u izrazu."""

    @abc.abstractmethod
    def NKA(self, Σ=None):  # page 67 lemma 1.55
        """NKA (nad Σ ili korišteni_znakovi) koji prepoznaje regularni jezik."""

    @abc.abstractmethod
    def enumerator(self): """Generator riječi iz regularnog jezika."""

    def __iter__(self):
        """Omogućuje iteriranje kroz regularni jezik, primjerice for-petljom."""
        dosad = set()
        for riječ in self.enumerator():
            if riječ not in dosad: (yield riječ), dosad.add(riječ)

    def __mul__(self, other): return Konkatenacija(self, other)

    def __or__(self, other): return Unija(self, other)

    @property
    def p(self): return Plus(self)

    @property
    def z(self): return Zvijezda(self)

    @property
    def u(self): return Upitnik(self)

    def __pow__(self, n):
        """ri ** n je n-struka konkatenacija regularnog jezika."""
        assert n >= 0
        return self * self**(n-1) if n else epsilon

    def KA(self, Σ=None):
        """Konačni automat koji prepoznaje regularni jezik."""
        return self.NKA(Σ).optimizirana_partitivna_konstrukcija().prirodni()

    def početak(self, n=10):
        """Lista "prvih" n riječi u regularnom jeziku."""
        return list(itertools.islice(self, n))

    @property
    def abeceda(self):
        """Skup korištenih znakova, pod uvjetom da je neprazan."""
        znakovi = self.korišteni_znakovi()
        assert znakovi  # abeceda ne smije biti prazna
        return znakovi


class Inicijalni(RegularniIzraz, abc.ABC):
    """Inicijalni jezik: ∅, ε, ili elementarni jezik."""

    def konačan(self): return True


class Prazni(Inicijalni):
    """Prazni jezik: ne sadrži nijednu riječ."""

    def __str__(self): return '∅'

    def prazan(self): return True

    def trivijalan(self): return True

    def korišteni_znakovi(self): return set()

    def NKA(self, Σ):  # page 67 lemma 1.55.3
        return NKA.iz_komponenti({1}, Σ, set(), 1, set())

    def enumerator(self): yield from set()


class Epsilon(Inicijalni):
    """Jezik ε: sadrži točno jednu riječ, i to praznu."""

    def __str__(self): return 'ε'

    def prazan(self): return False

    def trivijalan(self): return True

    def korišteni_znakovi(self): return set()

    def NKA(self, Σ):  # page 67 lemma 1.55.2
        return NKA.iz_komponenti({1}, Σ, set(), 1, {1})

    def enumerator(self): yield ε


class Elementarni(Inicijalni):
    """Elementarni(α) je jezik od točno 1 riječi, koja ima točno 1 znak α."""

    def __init__(self, znak):
        assert isinstance(znak, str) and len(znak) == 1
        self.znak = znak

    def __str__(self): return self.znak

    def prazan(self): return False

    def trivijalan(self): return False

    def korišteni_znakovi(self): return {self.znak}

    def NKA(self, Σ=None):  # page 67 lemma 1.55.1
        if Σ is None: Σ = self.korišteni_znakovi()
        return NKA.iz_komponenti({1, 2}, Σ, {(1, self.znak, 2)}, 1, {2})

    def enumerator(self): yield self.znak


prazni, epsilon = Prazni(), Epsilon()
a, b, c = Elementarni('a'), Elementarni('b'), Elementarni('c')
nula, jedan = Elementarni('0'), Elementarni('1')


class Binarni(RegularniIzraz, abc.ABC):
    """Zajednička natklasa za binarne operacije: uniju i konkatenaciju."""

    def __init__(self, r1, r2):
        assert isinstance(r1, RegularniIzraz) and isinstance(r2, RegularniIzraz)
        self.lijevo, self.desno = r1, r2

    def korišteni_znakovi(self):
        return self.lijevo.korišteni_znakovi() | self.desno.korišteni_znakovi()

    def trivijalan(ri):
        return ri.prazan() or ri.lijevo.trivijalan() and ri.desno.trivijalan()


class Unija(Binarni):
    """L ∪ M = {w : w ∈ L ∨ w ∈ M}"""

    def __str__(self): return f'({self.lijevo}|{self.desno})'

    def prazan(self): return self.lijevo.prazan() and self.desno.prazan()

    def konačan(self): return self.lijevo.konačan() and self.desno.konačan()

    def NKA(self, Σ=None):
        if Σ is None: Σ = self.korišteni_znakovi()
        return self.lijevo.NKA(Σ).unija(self.desno.NKA(Σ))

    def enumerator(self):
        if self.lijevo.konačan():
            yield from self.lijevo
            yield from self.desno
        elif self.desno.konačan():
            yield from self.desno
            yield from self.lijevo
        else:
            for lijevo, desno in zip(self.lijevo, self.desno):
                yield lijevo
                yield desno


class Konkatenacija(Binarni):
    """LM = {uv : u ∈ L ∧ v ∈ M}"""

    def __str__(self): return f'({self.lijevo}{self.desno})'

    def prazan(self): return self.lijevo.prazan() or self.desno.prazan()

    def konačan(self):
        if self.prazan(): return True
        return self.lijevo.konačan() and self.desno.konačan()

    def NKA(self, Σ=None):
        if Σ is None: Σ = self.korišteni_znakovi()
        return self.lijevo.NKA(Σ).konkatenacija(self.desno.NKA(Σ))

    def enumerator(self):
        if self.desno.konačan():
            for lijevo in self.lijevo:
                for desno in self.desno: yield lijevo + desno
        elif self.lijevo.konačan():
            for desno in self.desno:
                for lijevo in self.lijevo: yield lijevo + desno
        else:  # enumeracija po sporednim dijagonalama
            dosad = []
            for lijevo in self.lijevo:
                dosad.append(lijevo)
                for lijevo, desno in zip(reversed(dosad), self.desno):
                    yield lijevo + desno


class Zvijezda(RegularniIzraz):
    """L* := ε ∪ L ∪ LL ∪ LLL ∪ ...."""

    def __init__(self, ri):
        assert isinstance(ri, RegularniIzraz)
        self.ispod = ri

    def __str__(self): return f'{self.ispod}*'

    def prazan(self): return False

    def trivijalan(self): return self.ispod.trivijalan()

    def konačan(self): return self.trivijalan()

    def korišteni_znakovi(self): return self.ispod.korišteni_znakovi()

    def NKA(self, Σ=None):
        if Σ is None: Σ = self.korišteni_znakovi()
        return self.ispod.NKA(Σ).zvijezda()

    def enumerator(self): yield from Upitnik(Plus(self.ispod))


def Plus(ri): return Konkatenacija(Zvijezda(ri), ri)


def Upitnik(ri): return Unija(epsilon, ri)
