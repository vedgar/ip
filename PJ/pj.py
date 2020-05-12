import enum, types, collections, contextlib, itertools


def identifikator(znak): return znak.isalnum() or znak == '_'

TipoviTokena = enum.Enum
TipTokena = enum.auto

# TODO: bolji API: Greška(poruka, pozicija ili token ili AST...)
# ali ostaviti i lex.greška() i parser.greška() for convenience
class Greška(Exception): """Baza za sve greške vezane uz poziciju u kodu."""
class LeksičkaGreška(Greška): """Greška nastala prilikom leksičke analize."""
class SintaksnaGreška(Greška): """Greška nastala prilikom sintaksne analize."""
class SemantičkaGreška(Greška):"""Greška nastala prilikom semantičke analize."""
class GreškaIzvođenja(Greška): """Greška nastala prilikom izvođenja."""


#TODO maknuti potrebu za ovim: with SintaksnaGreška:... (zahtijeva metaklase)
@contextlib.contextmanager
def očekivano(tip_greške):
    try: yield
    except tip_greške as e: print(type(e).__name__, e, sep=': ')
    else: raise Greška('{} nije dignuta'.format(tip_greške.__name__))


class Tokenizer:
    def __init__(self, string):
        self.pročitani, self.buffer, self.stream = [], None, iter(string)
        self.i, self.j = 1, 0
        self.početak = 1, 1

    #TODO razmisliti o tome da i kreće od 0 za onelinere, a bez \ nakon '''
    @property
    def pozicija(self): return self.i, self.j

    @property
    def sadržaj(self): return ''.join(self.pročitani)

    def čitaj(self):
        """Čita sljedeći znak iz buffera ili stringa."""
        znak = next(self.stream, '') if self.buffer is None else self.buffer
        self.pročitani.append(znak)
        self.buffer = None
        if znak == '\n':
            self.gornji_j = self.j
            self.i += 1
            self.j = 0
        else: self.j += 1
        return znak

    def vrati(self):
        """Poništava čitanje zadnjeg pročitanog znaka."""
        assert self.buffer is None, 'Buffer je pun'
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

    def slijedi(self, znak):
        """Čita sljedeći znak ako i samo ako je jednak očekivanom."""
        assert len(znak) == 1, 'Duljina znaka {!r} mora biti 1'.format(znak)
        return self.čitaj() == znak or self.vrati()

    def __rshift__(self, znak): return self.slijedi(znak)

    def zvijezda(self, uvjet):
        """Čita Kleene* (nula ili više) znakova koji zadovoljavaju uvjet."""
        while uvjet(self.čitaj()): pass
        self.vrati()

    def plus(self, uvjet):
        """Čita Kleene+ (jedan ili više) znakova koji zadovoljavaju uvjet."""
        prvi = self.čitaj()
        if not uvjet(prvi): raise self.greška('očekivan ' + uvjet.__name__)
        self.zvijezda(uvjet)
    
    def pročitaj(self, znak):
        """Čita zadani znak, ili prijavljuje leksičku grešku."""
        if znak != self.čitaj():
            raise self.greška('očekivano {!r}'.format(znak))

    def pročitaj_do(self, znak, *, uključivo=True, više_redova=False):
        """Čita sve znakove do zadanog znaka."""
        assert len(znak) == 1, 'Duljina terminatora {} mora biti 1'.format(znak)
        if više_redova: self.zvijezda(uvjet = lambda z: z and z != znak)
        else: self.zvijezda(lambda z: z and z != '\n' and z != znak)
        if self.pogledaj() != znak:
            raise self.greška('{!r} nije pronađen'.format(znak))
        if uključivo: self.pročitaj(znak)

    def greška(self, info=''):
        """Konstruira leksičku grešku."""
        if self.buffer is not None: self.čitaj()
        if self.j: pozicija = self.i, self.j
        else: pozicija = self.i - 1, self.gornji_j + 1
        poruka = 'Redak {}, stupac {}: '.format(*pozicija)
        zadnji = self.pročitani.pop()
        opis = 'znak {!r}'.format(zadnji) if zadnji else 'kraj ulaza'
        poruka += 'neočekivani {}'.format(opis)
        if info: poruka += ' (' + info + ')'
        return LeksičkaGreška(poruka)

    def token(self, tip):
        """Odašilje token."""
        t = Token(tip, self.sadržaj)
        t._početak = self.početak
        t._kraj = self.pozicija
        self.zanemari()
        return t

    def literal(self, odakle, case=True):
        """Odašilje doslovni token ako ga nađe, ili vrstu zadanu argumentom."""
        t = self.sadržaj if case else self.sadržaj.casefold()
        def p(odakle):
            if isinstance(odakle, enum.EnumMeta):
                for e in odakle:
                    if e.value == t or getattr(e.value, 'literal', None) == t:
                        return e
        nađen = p(odakle) or p(type(odakle))
        if nađen: return self.token(nađen)
        elif isinstance(type(odakle), enum.EnumMeta): return self.token(odakle)
        else: raise self.greška()

    def zanemari(self):
        """Resetira pročitano."""
        self.pročitani.clear()
        self.početak = self.i, self.j + 1

    def __iter__(self):
        """Omogućuje prolazak `for znak in lex:`."""
        return iter(self.čitaj, '')

    def prirodni_broj(self, početak='', *, nula=True):
        """Čita prirodni broj bez vodećih nula, ili (ako je dozvoljena) nulu."""
        if not početak: početak = self.čitaj()
        if početak.isdecimal():
            if int(početak):
                pročitano = [početak]
                while True:
                    znak = self.čitaj()
                    if znak.isdecimal(): pročitano.append(znak)
                    else: break
                self.vrati()
                return int(''.join(pročitano))
            elif nula:
                if not self.pogledaj().isdecimal(): return 0
                else: raise self.greška('vodeće nule nisu dozvoljene')
            else: raise self.greška('nula nije dozvoljena ovdje')
        else: raise self.greška('očekivan prirodni broj')


class E(TipoviTokena):  # Everywhere
    """Često korišteni tipovi tokena, neovisno o konkretnom jeziku."""
    KRAJ = None        # End
    # GREŠKA = '\x00'  # Error
    # PRAZNO = ' '     # Empty
    # VIŠAK = ''       # Extra
KRAJ = E.KRAJ


class Token(collections.namedtuple('TokenTuple', 'tip sadržaj')):
    """Klasa koja predstavlja tokene."""
    def __new__(cls, tip, sadržaj=None):
        if sadržaj is None:
            sadržaj = tip.value
            if isinstance(sadržaj, type): sadržaj = sadržaj.literal
        if isinstance(tip.value, type): cls = tip.value
        return super().__new__(cls, tip, sadržaj)

    def __init__(self, *args):
        # if self.tip is E.GREŠKA: prijavi grešku na početku tokena, ne na kraju
        self.uspoređeni = set()
        self.razriješen = False
    
    def __repr__(self):
        ime, sadržaj = self.tip.name, self.sadržaj
        if sadržaj not in {ime, ''}: ime += repr(self.sadržaj)
        return ime

    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače None (laž)."""
        if not isinstance(tip, set): tip = {tip}
        self.uspoređeni |= tip
        if self.tip in tip:
            self.razriješen = True
            return self

    def je(self, *tipovi):
        self.uspoređeni.update(tipovi)
        if self.tip in tipovi:
            self.razriješen = True
            return self

    def neočekivan(self, info=''):
        """Konstruira sintaksnu grešku: neočekivani tip tokena."""
        if self.tip == KRAJ: poruka = 'Neočekivani kraj ulaza'
        else: poruka = raspon(self) + ': neočekivani token {!r}'
        if info: poruka += ' (' + info + ')'
        očekivano = ' ili '.join(t.name for t in self.uspoređeni if t!=self.tip)
        if očekivano: poruka += '\n  Očekivano: ' + očekivano
        return SintaksnaGreška(poruka.format(self))

    if False:
      def redeklaracija(self, prvi=None):
        """Konstruira semantičku grešku redeklaracije."""
        poruka = raspon(self) + ': redeklaracija {!r}'.format(self)
        if prvi is not None:
            info = 'Prva deklaracija je bila ovdje: ' + raspon(prvi).lower()
            poruka += '\n' + info
        return SemantičkaGreška(poruka)

    def nedeklaracija(self, info=''):
        """Konstruira semantičku grešku nedeklariranog simbola."""
        poruka = raspon(self) + ': nedeklarirano {!r}'.format(self)
        if info: poruka += ' ' + info.join('()')
        return SemantičkaGreška(poruka)

    def krivi_sadržaj(self, info):
        """Konstruira leksičku grešku: token nema dobar sadržaj."""
        poruka = raspon(self) + ': {!r}: {}'.format(self, info)
        return LeksičkaGreška(poruka)

    def iznimka(self, info):
        """Konstruira grešku izvođenja."""
        if isinstance(info, BaseException): info = info.args[0]
        poruka = raspon(self) + ': {!r}: {}'.format(self, info)
        return GreškaIzvođenja(poruka)

    def krivi_tip(self, *tipovi):
        """Konstruira semantičku grešku."""
        poruka = raspon(self) + ': {!r}: tipovi ne odgovaraju: '
        poruka += ' vs. '.join(map(str, tipovi))
        return SemantičkaGreška(poruka.format(self))

    @classmethod
    def kraj(cls):
        """Oznaka kraja niza tokena."""
        t = cls(KRAJ, '')
        t._početak = t._kraj = 'zadnji', 'nepoznat'
        t.razriješen = False
        return t

    def prikaz(self, dubina): print(self)


class Parser:
    def __new__(cls, ulaz):
        cls.static_lexer = staticmethod(cls.lexer)
        self = super().__new__(cls)
        self.buffer = self.zadnji = None
        self.KRAJ = Token.kraj()
        self.stream = cls.static_lexer(Tokenizer(ulaz))
        try: rezultat = self.start()
        except NoneInAST as exc:
            komponenta = exc.args[0]
            print('None je završio u komponenti {}.'.format(komponenta))
            print('Provjerite vraćaju li sve metode parsera vrijednost.')
            raise
        else:
            self.pročitaj(KRAJ)
            return rezultat

    @classmethod
    def tokeniziraj(cls, ulaz): 
        cls.static_lexer = staticmethod(cls.lexer)
        for token in cls.static_lexer(Tokenizer(ulaz)):
            print('\t{:23}: {}'.format(raspon(token), token))

    def čitaj(self):
        """Čitanje sljedećeg tokena iz buffera ili inicijalnog niza."""
        token = self.buffer
        if token is None:
            if self.zadnji is not None and not self.zadnji.razriješen:
                raise self.greška()
            token = next(self.stream, self.KRAJ)
        self.buffer = None
        self.zadnji = token
        return token

    def vrati(self):
        """Poništavanje čitanja zadnjeg pročitanog tokena."""
        assert self.buffer is None, 'Buffer je pun'
        self.buffer = self.zadnji

    pogledaj = Tokenizer.pogledaj

    def pročitaj(self, *tipovi):
        """Čita jedan od dozvoljenih simbola, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token ^ set(tipovi): return token
        self.vrati()
        raise self.greška()

    def slijedi(self, *tipovi):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj().je(*tipovi) else self.vrati()

    def __rshift__(self, tip):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj() ^ tip else self.vrati()

    def vidi(self, *tipovi): return self.pogledaj().je(*tipovi)

    def __ge__(self, tip): return self.pogledaj() ^ tip

    def greška(self): return self.zadnji.neočekivan()


elementarni = str, int, bool


class NoneInAST(Exception): pass

def AST_adapt(component):
    if isinstance(component, (Token, AST0, elementarni)): return component
    elif isinstance(component, (tuple, list)):
        if None in component: raise NoneInAST(component)
        return ListaAST(component)
    elif isinstance(component, dict):
        if None in component or None in component.values():
            raise NoneInAST(component)
        return RječnikAST(component.items())
    elif isinstance(component, Memorija): return AST_adapt(component.podaci)
    elif component is None: raise NoneInAST(component)
    else: raise TypeError('Nepoznat tip komponente {}'.format(type(component)))


def prikaz(objekt, dubina:int=float('inf'), uvlaka:str='', ime:str=None):
    intro = uvlaka
    if ime is not None: intro += ime + ' = '
    if isinstance(objekt, (Token, elementarni, Nenavedeno, enum.Enum)) \
            or not dubina:
        return print(intro, repr(objekt), sep='')
    if isinstance(objekt, ListaAST):
        print(intro, end='[...]:\n' if objekt else '[]\n')
        for vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+'. ')
    elif isinstance(objekt, AST0):
        print(intro + type(objekt).__name__ + ':')  # + '  ' + raspon(objekt))
        for ime, vrijednost in objekt._asdict().items():
            prikaz(vrijednost, dubina-1, uvlaka+' '*2, ime)
    elif isinstance(objekt, Memorija):
        print(intro + type(objekt).__name__ + ':')
        for ime, vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+': ', repr(ime))
    elif isinstance(objekt, (RječnikAST, dict)):
        print(intro, end='{:::}:\n' if objekt else '{}\n')
        for ključ, vrijednost in dict(objekt).items():
            prikaz(vrijednost, dubina-1, uvlaka+': ', repr(ključ))
    elif isinstance(objekt, tuple):
        print(intro, end='(...):\n' if objekt else '()\n')
        for vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+', ')
    else: assert False, 'Ne znam lijepo prikazati ' + str(objekt)


def raspon(ast):
    if hasattr(ast, '_početak'):
        ip, jp = ast._početak
        ik, jk = ast._kraj
        if ip == ik:
            if jp == jk: return 'Redak {}, stupac {}'.format(ip, jp)
            else: return 'Redak {}, stupci {}–{}'.format(ip, jp, jk)
        else: return 'Redak {}, stupac {} – redak {}, stupac {}'.format(
            ip, jp, ik, jk)
    else: return 'Nepoznata pozicija'


class AST0:
    """Bazna klasa za sva apstraktna sintaksna stabla."""
    def __xor__(self, tip):
        if isinstance(tip, type) and isinstance(self, tip): return self

    def je(self, *tipovi): return isinstance(self, tipovi)

    @classmethod
    def ili_samo(cls, lista):
        if not lista or len(cls._fields) != 1:
            raise SemantičkaGreška('Ispuštanje korijena nije dozvoljeno!')
        return lista[0] if len(lista) == 1 else cls(lista)
    

class Atom(Token, AST0): """Atomarni token kao apstraktno stablo."""


class ListaAST(tuple):
    def __init__(self, component):
        raspon = obuhvati(component)
        if raspon: self._početak, self._kraj = raspon
    def __repr__(self): return repr(list(self))


class RječnikAST(tuple):
    def __init__(self, component):
        raspon = obuhvati(itertools.chain(
            dict(component).keys(), dict(component).values()))
        if raspon: self._početak, self._kraj = raspon
    def __repr__(self): return repr(dict(self))


class Nenavedeno(AST0):
    """Atribut koji nije naveden."""
    def __bool__(self): return False
    def __repr__(self): return type(self).__name__.lower().join('<>')

nenavedeno = Nenavedeno()


def obuhvati(dijelovi):
    """Raspon koji obuhvaća sve dijelove koji imaju raspon."""
    d = [p for p in dijelovi if hasattr(p, '_početak') and hasattr(p, '_kraj')]
    if d: return min(p._početak for p in d), max(p._kraj for p in d)


def AST(atributi):
    AST2 = collections.namedtuple('AST2', atributi)
    # AST2.__new__.__defaults__ = tuple(nenavedeno for field in AST2._fields)
    
    class AST1(AST2, AST0):
        def __new__(cls, *args, **kw):
            new_args = [AST_adapt(arg) for arg in args]
            new_kw = {k: AST_adapt(v) for k, v in kw.items()}
            self = super().__new__(cls, *new_args, **new_kw)
            raspon = obuhvati(itertools.chain(args, kw.values()))
            if raspon: self._početak, self._kraj = raspon
            return self
    return AST1


class Memorija:
    """Simulira memoriju računala."""
    #TODO: puno precizniji interfejs: Token > str pri stavljanju i dohvaćanju
    def __init__(self, podaci=None, redefinicija=True):
        self.podaci = {} if podaci is None else podaci
        self.redefinicija = redefinicija

    def dohvati(self, token):
        if token in self.podaci: return self.podaci[token]
        elif token.sadržaj in self.podaci: return self.podaci[token.sadržaj]
        else: raise token.nedeklaracija()

    def __getitem__(self, token): return self.dohvati(token)

    def __contains__(self, token):
        if token in self.podaci: return True
        if isinstance(token, Token): return token.sadržaj in self.podaci

    def __setitem__(self, token, vrijednost):
        if not self.redefinicija and token in self: 
            raise SemantičkaGreška('Redefinicija od {!r}'.format(token))
        self.podaci[token] = vrijednost

    def imena(self): return self.podaci.keys()

    def __iter__(self): return iter(self.podaci.items())


class NelokalnaKontrolaToka(Exception):
    @property
    def preneseno(self): return self.args[0] if self.args else nenavedeno
