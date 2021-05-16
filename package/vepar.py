"""Framework za leksičku, sintaksnu, semantičku analizu, te izvođenje programa.
Za više detalja pogledati šalabahter.txt."""

__version__ = '1.4'


import enum, types, collections, contextlib, itertools, functools, math


def identifikator(znak):
    """Je li znak dopušten u C-ovskom imenu (slovo, znamenka ili _)?"""
    return znak.isalnum() or znak == '_'

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
    """Kontekst u kojem se mora pojaviti greška tip_greške, koja se ispisuje."""
    try: yield
    except tip_greške as e: print(type(e).__name__, e, sep=': ')
    else: raise Greška(f'{tip_greške.__name__} nije dignuta')


class Tokenizer:
    """Pomoćna klasa potrebna za rastavljanje niza znakova na tokene."""
    def __init__(self, string):
        """Inicijalizira tokenizer tako da čita string (od početka)."""
        self.pročitani, self.buffer, self.stream = [], None, iter(string)
        self.i, self.j = 1, 0
        self.početak = 1, 1

    #TODO razmisliti o tome da i kreće od 0 za onelinere, a bez \ nakon '''
    @property
    def pozicija(self):
        """Uređeni par (redak, stupac): gdje se tokenizer trenuntno nalazi."""
        return self.i, self.j

    @property
    def sadržaj(self):
        """Što je tokenizer do sada pročitao (od zadnjeg prepoznatog tokena."""
        return ''.join(self.pročitani)

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
        """'Viri' u sljedeći element, 'bez' čitanja."""
        znak = self.čitaj()
        self.vrati()
        return znak

    def slijedi(self, znak):
        """Čita sljedeći znak ako i samo ako je jednak navedenom."""
        assert len(znak) == 1, f'Duljina znaka {znak!r} mora biti 1'
        return self.čitaj() == znak or self.vrati()

    def __ge__(self, znak):
        """Čita sljedeći znak ako i samo ako je jednak navedenom."""
        return self.slijedi(znak)

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
            raise self.greška(f'očekivano {znak!r}')

    def __rshift__(self, znak):
        """Čita zadani znak, ili prijavljuje leksičku grešku."""
        return self.pročitaj(znak)

    def pročitaj_do(self, znak, *, uključivo=True, više_redova=False):
        """Čita sve znakove do zadanog znaka."""
        assert len(znak) == 1, f'Duljina terminatora {znak!r} mora biti 1'
        if više_redova: self.zvijezda(uvjet = lambda z: z and z != znak)
        else: self.zvijezda(lambda z: z and z != '\n' and z != znak)
        if self.pogledaj() != znak:
            raise self.greška(f'{znak!r} nije pronađen')
        if uključivo: self.pročitaj(znak)

    def greška(self, info=''):
        """Konstruira leksičku grešku."""
        if self.buffer is not None: self.čitaj()
        if self.j: i, j = self.i, self.j
        else: i, j = self.i - 1, self.gornji_j + 1
        poruka = f'Redak {i}, stupac {j}: '
        zadnji = self.pročitani.pop()
        opis = f'znak {zadnji!r}' if zadnji else 'kraj ulaza'
        poruka += f'neočekivani {opis}'
        if info: poruka += f'\n\t({info})'
        return LeksičkaGreška(poruka)

    def token(self, tip):
        """Konstruira token zadanog tipa i pročitanog sadržaja."""
        t = Token(tip, self.sadržaj)
        t._početak = self.početak
        t._kraj = self.pozicija
        self.zanemari()
        return t

    def literal(self, odakle, case=True):
        """Konstruira doslovni token ako ga nađe ili vrstu zadanu argumentom."""
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
        """Resetira pročitano (pretvara se da nije ništa pročitano)."""
        self.pročitani.clear()
        self.početak = self.i, self.j + 1

    def __iter__(self):
        """Omogućuje prolazak `for znak in lex:`."""
        return iter(self.čitaj, '')

    def prirodni_broj(self, početak, *, nula=True):
        """Čita prirodni broj bez vodećih nula, ili nulu ako je dozvoljena."""
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
    """Leksičke jedinice ulaza čiji tipovi upravljaju sintaksnom analizom."""
    def __new__(cls, tip, sadržaj=None):
        """Konstruira novi token zadanog tipa i (podrazumijevanog) sadržaja."""
        if sadržaj is None:
            sadržaj = tip.value
            if isinstance(sadržaj, type): sadržaj = sadržaj.literal
        if isinstance(tip.value, type): cls = tip.value
        return super().__new__(cls, tip, sadržaj)

    def __init__(self, *args):
        """Inicijalizacija tokena za potrebe parsiranja."""
        # if self.tip is E.GREŠKA: prijavi grešku na početku tokena, ne na kraju
        self.uspoređeni = set()
        self.razriješen = False
    
    def __repr__(self):
        """Za ispis tokena u obliku TIP'sadržaj'."""
        ime, sadržaj = self.tip.name, self.sadržaj
        if sadržaj not in {ime, ''}: ime += repr(self.sadržaj)
        return ime

    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače nenavedeno (laž)."""
        if not isinstance(tip, set): tip = {tip}
        self.uspoređeni |= tip
        if self.tip in tip:
            self.razriješen = True
            return self

    def neočekivan(self, info=''):
        """Konstruira sintaksnu grešku: neočekivani tip tokena."""
        if self.tip == KRAJ: poruka = 'Neočekivani kraj ulaza'
        else: poruka = raspon(self) + f': neočekivani token {self!r}'
        if info: poruka += f' ({info})'
        očekivano = ' ili '.join(t.name for t in self.uspoređeni if t!=self.tip)
        if očekivano: poruka += f'\n  Očekivano: {očekivano}'
        return SintaksnaGreška(poruka)

    def redefinicija(self, prvi=None):
        """Konstruira semantičku grešku redefiniranog simbola."""
        poruka = raspon(self) + f': redefinicija {self!r}'
        if prvi: poruka += '\nPrva deklaracija: ' + raspon(prvi).lower()
        return SemantičkaGreška(poruka)

    def nedeklaracija(self, info=''):
        """Konstruira semantičku grešku nedeklariranog simbola."""
        poruka = raspon(self) + f': nedeklarirano {self!r}'
        if info: poruka += f' ({info})'
        return SemantičkaGreška(poruka)

    def krivi_sadržaj(self, info):
        """Konstruira leksičku grešku: token nema dobar sadržaj."""
        poruka = raspon(self) + f': {self!r}: {info}'
        return LeksičkaGreška(poruka)

    def iznimka(self, info):
        """Konstruira grešku izvođenja iz poruke ili Pythonove iznimke."""
        if isinstance(info, BaseException): info = info.args[0]
        poruka = raspon(self) + f': {self!r}: {info}'
        return GreškaIzvođenja(poruka)

    def krivi_tip(self, *tipovi):
        """Konstruira semantičku grešku nepodudarajućih (statičkih) tipova."""
        poruka = raspon(self) + ': {self!r}: tipovi ne odgovaraju: '
        poruka += ' vs. '.join(map(str, tipovi))
        return SemantičkaGreška(poruka)

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
        """(Tokenizira i) parsira ulaz u apstraktno sintaksno stablo."""
        cls.static_lexer = staticmethod(cls.lexer)
        self = super().__new__(cls)
        self.buffer = self.zadnji = None
        self.KRAJ = Token.kraj()
        self.stream = cls.static_lexer(Tokenizer(ulaz))
        try: rezultat = self.start()
        except NoneInAST as exc:
            komponenta = exc.args[0]
            print(f'None je završio u komponenti {komponenta}.')
            print('Provjerite vraćaju li sve metode parsera vrijednost!')
            raise
        else:
            self >> KRAJ
            return rezultat

    @classmethod
    def tokeniziraj(cls, ulaz): 
        """Pregledno ispisuje pronađene tokene, za debugiranje tokenizacije."""
        cls.static_lexer = staticmethod(cls.lexer)
        for token in cls.static_lexer(Tokenizer(ulaz)):
            print(f'\t{raspon(token):23}: {token}')

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
        return nenavedeno

    pogledaj = Tokenizer.pogledaj

    def __rshift__(self, tipovi):
        """Čita jedan od dozvoljenih simbola, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token ^ tipovi: return token
        self.vrati()
        raise self.greška()

    def __ge__(self, tip):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj() ^ tip else self.vrati()

    def __gt__(self, tip):
        """Je li sljedeći token ('bez' čitanja) navedenog tipa ili tipova?"""
        return self.pogledaj() ^ tip

    def greška(self):
        """Konstruira sintaksnu grešku: zadnji pročitani token je pogrešan."""
        return self.zadnji.neočekivan()


elementarni = str, int, bool


class NoneInAST(Exception): """U apstraktnom sintaksnom stablu se našao None."""

def AST_adapt(component):
    """Pretvara komponente budućeg AST-a u oblik prikladan za AST."""
    if isinstance(component, (Token, AST0, elementarni)): return component
    elif isinstance(component, (tuple, list)):
        if None in component: raise NoneInAST(component)
        return ListaAST(component)
    elif isinstance(component, dict):
        if None in component or None in component.values():
            raise NoneInAST(component)
        return RječnikAST(component.items())
    elif isinstance(component, Memorija): return AST_adapt(dict(component))
    elif component is None: raise NoneInAST(component)
    else: raise TypeError(f'Nepoznat tip komponente {type(component)}')


def prikaz(objekt, dubina:int=math.inf, uvlaka:str='', ime:str=None):
    """Vertikalni prikaz AST-a, do zadane dubine."""
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
    elif isinstance(objekt, types.SimpleNamespace):
        print(intro + type(objekt).__name__ + ':'*bool(vars(objekt)))
        for ime, vrijednost in vars(objekt).items():
            prikaz(vrijednost, dubina-1, uvlaka+'  ', ime)
    else: assert False, f'Ne znam lijepo prikazati {objekt}'


def raspon(ast):
    """String koji kazuje odakle dokle se prostire token ili AST."""
    if hasattr(ast, '_početak'):
        ip, jp = ast._početak
        ik, jk = ast._kraj
        if ip == ik:
            if jp == jk: return f'Redak {ip}, stupac {jp}'
            else: return f'Redak {ip}, stupci {jp}–{jk}'
        else: return f'Redak {ip}, stupac {jp} – redak {ik}, stupac {jk}'
    else: return 'Nepoznata pozicija'


class AST0:
    """Bazna klasa za sva apstraktna sintaksna stabla."""
    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače nenavedeno (laž)."""
        if isinstance(tip, type) and isinstance(self, tip): return self

    @classmethod
    def ili_samo(cls, lista):
        """Konstruktor koji umjesto cls([x]) vraća samo x."""
        if not lista or len(cls._fields) != 1:
            raise SemantičkaGreška('Ispuštanje korijena nije dozvoljeno!')
        return lista[0] if len(lista) == 1 else cls(lista)
    

class Atom(Token, AST0): """Atomarni token kao apstraktno stablo."""


class ListaAST(tuple):
    """Lista komponenata kao jedna vrijednost atributa AST-a."""
    def __init__(self, component):
        raspon = obuhvati(component)
        if raspon: self._početak, self._kraj = raspon
    def __repr__(self): return repr(list(self))


class RječnikAST(tuple):
    """Rječnik kao jedna vrijednost atributa AST-a."""
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
    """Dinamički generirana klasa sa zadanim atributima."""
    AST2 = collections.namedtuple('AST2', atributi)
    # AST2.__new__.__defaults__ = tuple(nenavedeno for field in AST2._fields)
    
    class AST1(AST2, AST0):
        """Tip apstraktnog sintaksnog stabla."""
        def __new__(cls, *args, **kw):
            """Konstrukcija apstraktnog sintaksnog stabla iz komponenti."""
            new_args = [AST_adapt(arg) for arg in args]
            new_kw = {k: AST_adapt(v) for k, v in kw.items()}
            self = super().__new__(cls, *new_args, **new_kw)
            raspon = obuhvati(itertools.chain(args, kw.values()))
            if raspon: self._početak, self._kraj = raspon
            return self
    return AST1


class Memorija:
    """Memorija računala, indeksirana tokenima ili njihovim sadržajima."""
    def __init__(self, podaci={}, redefinicija=True):
        self.redefinicija = redefinicija
        self.podaci, self.token_sadržaja = {}, {}
        for ključ, vrijednost in podaci.items(): self[ključ] = vrijednost

    def provjeri(self, lokacija, sadržaj):
        if sadržaj in self.podaci: return
        if isinstance(lokacija, Token): raise lokacija.nedeklaracija()
        raise LookupError(f'{lokacija!r} nije pronađeno u memoriji')

    def razriješi(self, l):
        """Vraća sadržaj i čitav token (ili None ako ga ne zna) za l."""
        if isinstance(l, Token):
            d = self.token_sadržaja.setdefault(l.sadržaj, l)
            if l == d: return l.sadržaj, d
            else: raise d.krivi_tip(l.tip, d.tip)
        elif isinstance(l, str): return l, self.token_sadržaja.get(l)
        else: raise TypeError(f'Memorija nije indeksirana s {type(l)}!')

    def __delitem__(self, lokacija):
        if not self.redefinicija:  # razmisliti o ovome, možda promijeniti
            raise TypeError(f'Brisanje iz memorije zahtijeva redefiniciju')
        sadržaj, token = self.razriješi(lokacija)
        self.provjeri(lokacija, sadržaj)
        del self.podaci[sadržaj]

    def __getitem__(self, lokacija):
        sadržaj, token = self.razriješi(lokacija)
        self.provjeri(lokacija, sadržaj)
        return self.podaci[sadržaj]

    def __setitem__(self, lokacija, vrijednost):
        sadržaj, token = self.razriješi(lokacija)
        if self.redefinicija or sadržaj not in self.podaci:
            self.podaci[sadržaj] = vrijednost
        elif isinstance(lokacija, Token): raise lokacija.redefinicija(token)
        elif token: raise token.redefinicija()
        else: raise SemantičkaGreška(f'Nedozvoljena redefinicija {lokacija!r}')

    def __contains__(self, lokacija):
        with contextlib.suppress(SemantičkaGreška, LookupError):
            sadržaj, token = self.razriješi(lokacija)
            return sadržaj in self.podaci

    def __iter__(self):
        for ključ, vrijednost in self.podaci.items():
            yield self.token_sadržaja.get(ključ, ključ), vrijednost

    def __len__(self): return len(self.podaci)


cache = functools.lru_cache(maxsize=None)


class NelokalnaKontrolaToka(Exception):
    """Bazna klasa koja služi za implementaciju nelokalne kontrole toka."""
    @property
    def preneseno(self):
        """Vrijednost koja je prenesena "unatrag" prema korijenu."""
        return self.args[0] if self.args else nenavedeno
