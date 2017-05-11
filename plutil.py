import enum, types, collections, contextlib


def ključna_riječ(enumeracija, riječ):
    with contextlib.suppress(KeyError):
        e = enumeracija[riječ]
        if e.name == e.value: return e

def operator(enumeracija, riječ):
    assert len(riječ) == 1
    with contextlib.suppress(ValueError):
        return enumeracija(riječ)


class LexError(Exception):
    """Greška nastala prilikom leksičke analize."""


class Tokenizer:
    def __init__(self, string):
        self.stack, self.buffer, self.stream = [], None, iter(string)
        self.početak = self.i, self.j = 1, 0

    @property
    def sadržaj(self): return ''.join(self.stack)

    def čitaj(self):
        """Čitanje sljedećeg znaka iz buffera ili stringa."""
        znak = self.buffer or next(self.stream, '')
        self.stack.append(znak)
        self.buffer = None
        if znak == '\n':
            self.gornji_j = self.j
            self.i += 1
            self.j = 0
        else: self.j += 1
        return znak

    def vrati(self):
        """Poništavanje čitanja zadnjeg pročitanog znaka."""
        assert not self.buffer
        self.buffer = self.stack.pop()
        if self.j: self.j -= 1
        else:
            self.j = self.gornji_j
            self.i -= 1
            del self.gornji_j

    def pogledaj(self):
        """'Virenje' u sljedeći znak, 'bez' čitanja."""
        znak = self.čitaj()
        self.vrati()
        return znak

    def zvijezda(self, uvjet):
        """Pročitaj Kleene* (nula ili više) znakova koji zadovoljavaju uvjet."""
        while uvjet(self.čitaj()): pass
        self.vrati()
        
    def očekuj(self, niz):
        """Čita sve znakove zadanog niza redom, ili javlja LexError."""
        for znak in niz:
            pročitan = self.čitaj()
            if znak != pročitan: self.greška('očekivano {!r}'.format(znak))
        return niz

    def greška(self, info=''):
        """Prijavljuje grešku."""
        if self.buffer: self.čitaj()
        poruka = 'Redak {}, stupac {}: neočekivan znak {!r}'
        if info: poruka += ' ' + info.join('()')
        raise LexError(poruka.format(self.i, self.j, self.stack.pop()))

    def token(self, tip):
        """Odašilje token."""
        t = Token(tip, ''.join(self.stack))
        t.početak = self.početak
        self.stack.clear()
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
    def __pow__(self, tip): return self.tip == tip

oznaka_kraja = Token(E.KRAJ, '')
oznaka_kraja.početak = 'zadnji', 0


class Parser:
    def __init__(self, tokeni):
        self.buffer, self.stream = None, iter(tokeni)

    def čitaj(self):
        """Čitanje sljedećeg tokena iz buffera ili inicijalnog niza."""
        self.zadnje = token = self.buffer or next(self.stream, oznaka_kraja)
        self.buffer = None
        return token

    def vrati(self):
        """Poništavanje čitanja zadnjeg pročitanog znaka."""
        assert not self.buffer
        self.buffer = self.zadnje

    pogledaj = Tokenizer.pogledaj

    def pročitaj(self, *tipovi):
        """Čita jedan od dozvoljenih simbola, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token.tip in tipovi: return token
        lokacija = 'Redak {}, stupac {}: '.format(*token.početak)
        očekivani = ' ili '.join(tip.name for tip in tipovi)
        poruka = 'očekivano {}, pročitano {}.'.format(očekivani, token)
        raise SyntaxError(lokacija + poruka)
        # upotrijebiti filename, lineno, offset, text, ... kad bude linecache

    def granaj(self, *simboli):
        """Gleda (bez čitanja) je li sljedeći simbol ok, i vraća ga."""
        sljedeći = self.pročitaj(*simboli)
        self.vrati()
        return sljedeći


elementarni = str, int, type(None), bool


def AST_adapt(component):
    if isinstance(component, (Token, AST0, elementarni)): return component
    elif isinstance(component, (set, frozenset)): return frozenset(component)
    elif isinstance(component, (tuple, list)): return tuple(component)
    else: raise TypeError('Unknown component type {}'.format(type(component)))


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
