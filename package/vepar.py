"""Framework za leksičku, sintaksnu, semantičku analizu, te izvođenje programa.
Za više detalja pogledati šalabahter.txt."""


__version__ = '2.3'


import enum, types, collections, contextlib, itertools, functools, \
        dataclasses, textwrap, inspect, math


the_lexer = None

def lexer(gen):
    global the_lexer
    assert the_lexer is None, 'Lexer je već postavljen!'
    assert inspect.isgeneratorfunction(gen), 'Lexer mora biti generator!'
    the_lexer = gen

    @functools.wraps(gen)
    def tokeniziraj(ulaz): 
        """Pregledno ispisuje pronađene tokene, za debugiranje tokenizacije."""
        if '\n' not in ulaz: print('Tokenizacija:', ulaz)
        for token in the_lexer(Tokenizer(ulaz)):
            r = raspon(token)
            if r.startswith('Znak'): print(f'\t\t{r:15}: {token}')
            else: print(f'\t{r:23}: {token}')
    return tokeniziraj


def paše(znak, uvjet): 
    """Zadovoljava li znak zadani uvjet (funkcija, znak ili skup)."""
    if isinstance(uvjet, str):
        assert len(uvjet) <= 1, 'Znakovi moraju biti duljine 1!'
        return znak == uvjet
    elif callable(uvjet):
        rezultat = uvjet(znak)
        assert isinstance(rezultat, bool), 'Uvjet nije predikat!'
        return rezultat
    elif isinstance(uvjet, (set, frozenset)):
        return any(paše(znak, disjunkt) for disjunkt in uvjet)
    else: assert False, f'Nepoznata vrsta uvjeta {uvjet}!'

def raspis(uvjet):
    if isinstance(uvjet, str): yield repr(uvjet)
    elif callable(uvjet): yield uvjet.__name__
    elif isinstance(uvjet, (set, frozenset)):
        yield from itertools.chain.from_iterable(map(raspis, uvjet))
    else: assert False, f'Nepoznata vrsta uvjeta {uvjet}!'


def omotaj(metoda):
    """Jednostavni wrapper za metode parsera."""
    @functools.wraps(metoda)
    def omotano(self, *args, **kw):
        početak = self.pogledaj()._početak
        pvr = metoda(self, *args, **kw)
        kraj = self.zadnji._kraj
        if pvr is None: raise NoneInAST(textwrap.dedent(f'''
            Sve metode parsera moraju vratiti vrijednost!
            Provjerite metodu {metoda.__name__}.
            Umjesto None vratite nenavedeno.'''))
        if isinstance(pvr, AST): pvr._početak, pvr._kraj = početak, kraj
        return pvr
    return omotano


TipoviTokena = enum.Enum


class Kontekst(type):
    """Metaklasa: upravitelj konteksta (with) za očekivanu grešku."""
    def __enter__(self): pass
    def __exit__(self, e_type, e_val, e_tb):
        if e_type is None: raise Greška(f'{self.__name__} nije dignuta')
        elif issubclass(e_type, self):
            print(e_type.__name__, e_val, sep=': ')
            return True


class Runtime(types.SimpleNamespace):
    """Globalni objekt za pamćenje runtime konteksta (npr. memorije)."""
    def __delattr__(self, atribut):
        with contextlib.suppress(AttributeError): super().__delattr__(atribut)

rt = Runtime()


# TODO: bolji API: Greška(poruka, pozicija ili token ili AST...)
# ali ostaviti i lex.greška() i parser.greška() for convenience
class Greška(Exception, metaclass=Kontekst): """Greška vezana uz poziciju."""
class LeksičkaGreška(Greška): """Greška nastala u leksičkoj analizi."""
class SintaksnaGreška(Greška): """Greška nastala u sintaksnoj analizi."""
class SemantičkaGreška(Greška): """Greška nastala u semantičkoj analizi."""
class GreškaIzvođenja(Greška): """Greška nastala u izvođenju."""


class E(TipoviTokena): KRAJ = None
KRAJ = E.KRAJ


class NoneInAST(Exception): """U apstraktnom sintaksnom stablu se našao None."""


cache = functools.lru_cache(maxsize=None)


def Registri(prefiks='_t', start=0):
    for i in itertools.count(start): yield prefiks + str(i)


class NelokalnaKontrolaToka(Exception):
    """Bazna klasa koja služi za implementaciju nelokalne kontrole toka."""
    @property
    def preneseno(self):
        """Vrijednost koja je prenesena "unatrag" prema korijenu."""
        return self.args[0] if self.args else nenavedeno

class Tokenizer:
    """Klasa za rastavljanje niza znakova na tokene."""
    def __init__(self, string):
        """Inicijalizira tokenizer tako da čita string (od početka)."""
        self.pročitani, self.buffer, self.stream = [], None, iter(string)
        self.i = int('\n' in string and not string.startswith('\n'))
        self.j = 0
        self.početak = 0, 1

    @property
    def sadržaj(self):
        """Što je tokenizer do sada pročitao, od zadnjeg prepoznatog tokena."""
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

    def slijedi(self, uvjet):
        """Čita sljedeći znak ako i samo ako zadovoljava uvjet."""
        return paše(self.čitaj(), uvjet) or self.vrati()

    def vidi(self, uvjet):
        """Ispituje sljedeći znak ('bez' čitanja)."""
        return paše(self.pogledaj(), uvjet)

    def zvijezda(self, uvjet):
        """Čita Kleene* (nula ili više) znakova koji zadovoljavaju uvjet."""
        while paše(self.čitaj(), uvjet): pass
        self.vrati()

    def plus(self, uvjet):
        """Čita Kleene+ (jedan ili više) znakova koji zadovoljavaju uvjet."""
        self.nužno(uvjet)
        self.zvijezda(uvjet)
    
    def nužno(self, uvjet):
        """Čita zadani znak, ili prijavljuje leksičku grešku."""
        if not paše(self.čitaj(), uvjet):
            raise self.greška(f"očekivano {' ili '.join(raspis(uvjet))}")

    def pročitaj_do(self, uvjet, *, uključivo=True, više_redova=False):
        """Čita sve znakove do ispunjenja uvjeta."""
        poruka = ' ni '.join(raspis(uvjet)) + ' nije pronađen '
        while ...:
            znak = self.čitaj()
            if paše(znak, uvjet):
                if not uključivo: self.vrati()
                break
            elif znak == '\n' and not više_redova:
                raise self.greška(poruka + 'u retku')
            elif not znak:
                raise self.greška(poruka + 'do kraja ulaza')

    def __lt__(self, uvjet): 
        return self.pročitaj_do(uvjet, uključivo=False)

    def greška(self, info=''):
        """Konstruira leksičku grešku."""
        if self.buffer is not None: self.čitaj()
        if self.j: i, j = self.i, self.j
        else: i, j = self.i - 1, self.gornji_j + 1
        poruka = f'Redak {i}, stupac {j}: ' if i else f'Znak #{j}: '
        zadnji = self.pročitani.pop()
        opis = f'znak {zadnji!r}' if zadnji else 'kraj ulaza'
        poruka += f'neočekivani {opis}'
        if info: poruka += f'\n\t({info})'
        return LeksičkaGreška(poruka)

    def token(self, tip):
        """Konstruira token zadanog tipa i pročitanog sadržaja."""
        t = Token(tip, self.sadržaj)
        t._početak = self.početak
        t._kraj = self.i, self.j
        self.zanemari()
        return t

    def literal(self, odakle, *, case=True):
        """Doslovni token s pročitanim sadržajem, ili leksička greška."""
        t = self.sadržaj if case else self.sadržaj.casefold()
        for e in odakle:
            if e.value == t or getattr(e.value, 'literal', None) == t:
                return self.token(e)
        else: raise self.greška()

    def literal_ili(self, inače, *, case=True):
        """Doslovni token ako je nađen po sadržaju, ili token tipa inače."""
        t = self.sadržaj if case else self.sadržaj.casefold()
        for e in type(inače):
            if e.value == t or getattr(e.value, 'literal', None) == t:
                return self.token(e)
        else: return self.token(inače)

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
                while (z := self.čitaj()).isdecimal(): pročitano.append(z)
                self.vrati()
                return int(''.join(pročitano))
            elif nula:
                if not self.pogledaj().isdecimal(): return 0
                else: raise self.greška('vodeće nule nisu dozvoljene')
            else: raise self.greška('nula nije dozvoljena ovdje')
        else: raise self.greška('očekivan prirodni broj')

    __next__ = čitaj
    __ge__ = slijedi
    __gt__ = vidi
    __mul__ = zvijezda
    __add__ = plus
    __rshift__ = nužno
    __sub__ = __le__ = pročitaj_do


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
        self.uspoređeni = set()
        self.razriješen = False
    
    def __repr__(self):
        """Za ispis tokena u obliku TIP'sadržaj'."""
        return self.tip.name + repr(self.sadržaj)

    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače nenavedeno (laž)."""
        if not isinstance(tip, set): tip = {tip}
        self.uspoređeni |= tip
        if self.tip in tip:
            self.razriješen = True
            return self
        else: return nenavedeno

    def neočekivan(self, info=''):
        """Konstruira sintaksnu grešku: neočekivani tip tokena."""
        if self.tip is KRAJ: poruka = 'Neočekivani kraj ulaza'
        else: poruka = raspon(self) + f': neočekivani token {self!r}'
        if info: poruka += f' ({info})'
        uspoređeni = sorted(t.name for t in self.uspoređeni if t != self.tip)
        if uspoređeni: poruka += f"\n\tOčekivano: {' ili '.join(uspoređeni)}"
        return SintaksnaGreška(poruka)

    def redeklaracija(self, prvi=None):
        """Konstruira semantičku grešku redeklariranog simbola."""
        poruka = raspon(self) + f': redeklaracija {self!r}'
        if prvi: poruka += '\n\tPrva deklaracija: ' + raspon(prvi).lower()
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
        if isinstance(info, BaseException):
            info = type(info).__name__ + ': ' + info.args[0]
        poruka = raspon(self) + f':\n\t{self!r}:  {info}'
        return GreškaIzvođenja(poruka)

    def krivi_tip(self, *tipovi):
        """Konstruira semantičku grešku nepodudarajućih (statičkih) tipova."""
        poruka = raspon(self) + f': {self!r}: tipovi ne odgovaraju: '
        poruka += ' vs. '.join(map(str, tipovi))
        return SemantičkaGreška(poruka)

    @classmethod
    def kraj(cls):
        """Oznaka kraja niza tokena."""
        t = cls(KRAJ, '')
        t._početak = t._kraj = 'zadnji', 'nepoznat'
        t.razriješen = False
        return t


class Parser:
    def __new__(cls, ulaz):
        """(Tokenizira i) parsira ulaz u apstraktno sintaksno stablo."""
        if the_lexer is None:
            raise LookupError('Dekorirajte generator tokena s @lexer!')
        self = super().__new__(cls)
        self.buffer = self.zadnji = None
        self.KRAJ = Token.kraj()
        self.stream = the_lexer(Tokenizer(ulaz))
        rezultat = self.start()
        self >> KRAJ
        return rezultat

    def __init_subclass__(cls):
        prva = None
        for ime, metoda in vars(cls).items():
            if ime.startswith('_'): continue
            if prva is None: prva = metoda
            if isinstance(metoda, types.FunctionType):
                setattr(cls, ime, omotaj(metoda))
        if not hasattr(cls, 'start'): cls.start = omotaj(prva)

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

    def nužno(self, tip):
        """Čita token odgovarajućeg tipa, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token ^ tip: return token
        self.vrati()
        raise self.greška()

    def slijedi(self, tip):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj() ^ tip else self.vrati()

    def vidi(self, tip):
        """Je li sljedeći token ('bez' čitanja) navedenog tipa ili tipova?"""
        return self.pogledaj() ^ tip

    __rshift__ = nužno
    __ge__ = slijedi
    __gt__ = vidi

    def greška(self):
        """Konstruira sintaksnu grešku: zadnji pročitani token je pogrešan."""
        return self.zadnji.neočekivan()


def prikaz(objekt, dubina:int=math.inf, uvlaka='', ime:str=None, rasponi=2):
    """Vertikalni prikaz AST-a, do zadane dubine."""
    intro = uvlaka
    if ime is not None: intro += ime + ' = '
    if isinstance(objekt, (str, int, Nenavedeno, enum.Enum)) \
            or not dubina:
        return print(intro, repr(objekt), sep='')
    elif isinstance(objekt, Token):
        r, tail = raspon(objekt), ''
        if r != 'Nepoznata pozicija' and rasponi > 1: tail = '  @[' + r + ']'
        return print(intro, repr(objekt), tail, sep='')
    elif isinstance(objekt, list):
        print(intro, end='[...]:\n' if objekt else '[]\n')
        for vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+'. ')
    elif isinstance(objekt, Memorija):
        print(intro + type(objekt).__name__ + ':')
        for ime, vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+': ', repr(ime))
    elif isinstance(objekt, dict):
        print(intro, end='{:::}:\n' if objekt else '{}\n')
        for ključ, vrijednost in dict(objekt).items():
            prikaz(vrijednost, dubina-1, uvlaka+': ', repr(ključ))
    elif isinstance(objekt, tuple):
        print(intro, end='(...):\n' if objekt else '()\n')
        for vrijednost in objekt:
            prikaz(vrijednost, dubina-1, uvlaka+', ')
    elif isinstance(objekt, (types.SimpleNamespace, AST)):
        header = intro + type(objekt).__name__ + ':'*bool(vars(objekt))
        r = raspon(objekt)
        if r != 'Nepoznata pozicija' and rasponi: header += '  @[' + r + ']'
        print(header)
        try: d, t = objekt.za_prikaz(), '~ '
        except AttributeError: d, t = vars(objekt), '  '
        for ime, vrijednost in d.items():
            if not ime.startswith('_'):
                prikaz(vrijednost, dubina - 1, uvlaka + t, ime)
    else: raise TypeError(f'Ne znam lijepo prikazati {objekt}')


def raspon(ast):
    """String koji kazuje odakle dokle se prostire token ili AST."""
    if hasattr(ast, '_početak'):
        ip, jp = ast._početak
        ik, jk = ast._kraj
        if ip == ik:
            if ip == 0:
                if jp == jk: return f'Znak #{jp}'
                else: return f'Znakovi #{jp}–#{jk}'
            elif jp == jk: return f'Redak {ip}, stupac {jp}'
            else: return f'Redak {ip}, stupci {jp}–{jk}'
        elif ik == 'zadnji':
            if ip == 0: return f'Znakovi #{jp}–kraj'
            else: return f'Redak {ip}, stupac {jp} – kraj'
        else: return f'Redak {ip}, stupac {jp} – redak {ik}, stupac {jk}'
    else: return 'Nepoznata pozicija'


class AST:
    """Bazna klasa za sva apstraktna sintaksna stabla."""
    def __init_subclass__(cls): dataclasses.dataclass(cls, frozen=False)

    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače nenavedeno (laž)."""
        if isinstance(tip, type) and isinstance(self, tip): return self
        else: return nenavedeno

    iznimka = Token.iznimka

    @classmethod
    def ili_samo(cls, lista):
        """Konstruktor koji umjesto cls([x]) vraća samo x."""
        if not lista or len(dataclasses.fields(cls)) != 1:
            raise SemantičkaGreška('Ispuštanje korijena nije dozvoljeno!')
        return lista[0] if len(lista) == 1 else cls(lista)


class Nenavedeno(AST):
    """Atribut koji nije naveden."""
    def __bool__(self): return False
    def __repr__(self): return type(self).__name__.lower().join('<>')

nenavedeno = Nenavedeno()


class Memorija:
    """Memorija računala, indeksirana tokenima ili njihovim sadržajima."""
    def __init__(self, podaci={}, *, redefinicija=True):
        self.redefinicija = redefinicija
        self.podaci, self.token_sadržaja = {}, {}
        if isinstance(podaci, dict): podaci = podaci.items()
        elif not isinstance(podaci, (zip, Memorija)):
            raise TypeError(f'Memorija ne razumije podatke: {podaci}')
        for ključ, vrijednost in podaci: self[ključ] = vrijednost

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
        elif isinstance(lokacija, Token): raise lokacija.redeklaracija(token)
        elif token: raise token.redeklaracija()
        else: raise SemantičkaGreška(f'Nedozvoljena redefinicija {lokacija!r}')

    def __contains__(self, lokacija):
        with contextlib.suppress(SemantičkaGreška, LookupError):
            sadržaj, token = self.razriješi(lokacija)
            return sadržaj in self.podaci

    def __iter__(self):
        for ključ, vrijednost in self.podaci.items():
            yield self.token_sadržaja.get(ključ, ključ), vrijednost

    def __len__(self): return len(self.podaci)

    #TODO: dodati Memorija.imena kao dict(Memorija).keys(), koristiti u 04_...
