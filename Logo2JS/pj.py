import enum, types, collections, contextlib


def ključna_riječ(enumeracija, riječ, case=True):
    with contextlib.suppress(ValueError, KeyError):
        e = enumeracija(riječ) if case else enumeracija[riječ.upper()]
        if e.name.casefold() == e.value.casefold(): return e

def operator(enumeracija, znak):
    assert len(znak) == 1
    with contextlib.suppress(ValueError): return enumeracija(znak)


class Greška(Exception): """Baza za sve greške vezane uz poziciju u kodu."""
class LeksičkaGreška(Greška): """Greška nastala prilikom leksičke analize."""
class SintaksnaGreška(Greška): """Greška nastala prilikom sintaksne analize."""
class SemantičkaGreška(Greška):"""Greška nastala prilikom semantičke analize."""
class GreškaIzvođenja(Greška): """Greška nastala prilikom izvođenja."""


class Tokenizer:
    def __init__(self, string):
        self.pročitani, self.buffer, self.stream = [], None, iter(string)
        self.početak = self.i, self.j = 1, 0

    @property
    def sadržaj(self): return ''.join(self.pročitani)

    def čitaj(self):
        """Čita sljedeći znak iz buffera ili stringa."""
        znak = self.buffer or next(self.stream, '')
        self.pročitani.append(znak)
        self.buffer = None
        if znak == '\n':
            self.gornji_j = self.j
            self.i += 1
            self.j = 0
        else: self.j += 1
        # print(znak, end='_')
        return znak

    def vrati(self):
        """Poništava čitanje zadnjeg pročitanog znaka."""
        assert not self.buffer
        self.buffer = self.pročitani.pop()
        if self.j: self.j -= 1
        else:
            self.j = self.gornji_j
            self.i -= 1
            del self.gornji_j

    def pogledaj(self):
        """'Viri' u sljedeći znak, 'bez' čitanja."""
        znak = self.čitaj()
        self.vrati()
        return znak

    def zvijezda(self, uvjet):
        """Čita Kleene* (nula ili više) znakova koji zadovoljavaju uvjet."""
        while uvjet(self.čitaj()): pass
        self.vrati()
        
    def pročitaj(self, znak):
        """Čita zadani znak, ili prijavljuje leksičku grešku."""
        if znak != self.čitaj(): self.greška('očekivano {!r}'.format(znak))

    def greška(self, info=''):
        """Prijavljuje leksičku grešku."""
        if self.buffer: self.čitaj()
        poruka = 'Redak {}, stupac {}: neočekivan znak {!r}'
        if info: poruka += ' (' + info + ')'
        raise LeksičkaGreška(poruka.format(self.i,self.j,self.pročitani.pop()))

    def token(self, tip):
        """Odašilje token."""
        t = Token(tip, ''.join(self.pročitani))
        t.početak = self.početak
        t.uspoređeni = set()
        t.razriješen = False
        self.pročitani.clear()
        self.početak = self.i, self.j
        return t


class E(enum.Enum):
    KRAJ = None
    GREŠKA = '\x00'
    PRAZNO = ' '


class Token(collections.namedtuple('_', 'tip sadržaj')):
    """Jednostavna klasa koja predstavlja tokene."""
    def __repr__(self):
        ime, sadržaj = self.tip.name, self.sadržaj
        if sadržaj not in {ime, ''}: ime += repr(self.sadržaj)
        return ime

    def __pow__(self, tip):
        if isinstance(tip, set):
            self.uspoređeni.update(tip)
            povrat = self.tip in tip
        else:
            self.uspoređeni.add(tip)
            povrat = self.tip == tip
        if povrat: self.razriješen = True
        return povrat

    def neočekivan(self, info=''):
        """Prijavljuje sintaksnu grešku: neočekivani tip tokena."""
        poruka = 'Redak {}, stupac {}: neočekivan token {!r}'
        if info: poruka += ' (' + info + ')'
        očekivano = ' ili '.join(t.name for t in self.uspoređeni)
        if očekivano: poruka += '\nOčekivano: ' + očekivano
        i, j = getattr(self, 'početak', '??')
        raise SintaksnaGreška(poruka.format(i, j, self))

    def problem(self, info):
        """Prijavljuje grešku izvođenja."""
        poruka = 'Redak {}, stupac {}: {!r}: {}'
        i, j = getattr(self, 'početak', '??')
        raise GreškaIzvođenja(poruka.format(i, j, self, info))


    @classmethod
    def kraj(cls):
        """Oznaka kraja niza tokena."""
        t = cls(E.KRAJ, '')
        t.početak = 'zadnji', 0
        t.uspoređeni = set()
        t.razriješen = False
        return t


class Parser:
    def __init__(self, tokeni):
        self.buffer, self.stream = None, iter(tokeni)
        self.zadnji, self.kraj = None, Token.kraj()

    def čitaj(self):
        """Čitanje sljedećeg tokena iz buffera ili inicijalnog niza."""
        token = self.buffer
        if token is None:
            if self.zadnji is not None and not self.zadnji.razriješen:
                self.zadnji.neočekivan()
            token = next(self.stream, self.kraj)
        self.buffer = None
        self.zadnji = token
        return token

    def vrati(self):
        """Poništavanje čitanja zadnjeg pročitanog tokena."""
        assert not self.buffer
        self.buffer = self.zadnji

    pogledaj = Tokenizer.pogledaj

    def pročitaj(self, *tipovi):
        """Čita jedan od dozvoljenih simbola, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token ** set(tipovi): return token
        token.neočekivan()

    def do(self, tip):
        """Čita do uključivo tokena zadanog tipa, pogodno za while petlju."""
        t = not self.čitaj() ** tip
        if t: self.vrati()
        return t

elementarni = str, int, type(None), bool


def AST_adapt(component):
    if isinstance(component, (Token, AST0, elementarni)): return component
    elif isinstance(component, (set, frozenset)): return frozenset(component)
    elif isinstance(component, (tuple, list)): return tuple(component)
    else: raise TypeError('Nepoznat tip komponente {}'.format(type(component)))


class AST0:
    """Bazna klasa za sva apstraktna sintaksna stabla."""
    def __pow__(self, tip):
        return isinstance(tip, type) and isinstance(self, tip)


def AST(atributi):
    AST2 = collections.namedtuple('AST2', atributi)
    AST2.__new__.__defaults__ = tuple(None for field in AST2._fields)
    
    class AST1(AST2, AST0):
        def __new__(cls, *args, **kw):
            new_args = [AST_adapt(arg) for arg in args]
            new_kw = {k: AST_adapt(v) for k, v in kw.items()}
            return super().__new__(cls, *new_args, **new_kw)
    return AST1

class Atom(Token, AST0):
    """Atomarni token kao apstraktno stablo."""
