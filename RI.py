from util import *
from NKA import (ε, NedeterminističkiKonačniAutomat, nedeterministička_unija,
    nedeterministička_konkatenacija, nedeterministička_zvijezda,
    optimizirana_partitivna_konstrukcija)
from util import *


class Prazan(RegularanIzraz):
    def __str__(self):
        return '∅'

    def enumerator(self):
        yield from set()

    def beskonačan(self):
        return False


class Epsilon(RegularanIzraz):
    def __str__(self):
        return 'ε'

    def enumerator(self):
        yield ε

    def beskonačan(self):
        return False


class Elementaran(RegularanIzraz):
    @classmethod
    def iz_znaka(klasa, znak):
        return klasa(znak=znak)

    def __str__(self):
        z = self.znak
        if isinstance(z, str) and not z.isalnum():
        elif z.isalnum(): return z
        else: return '\\' + z

    def jezik(self):
        if self.element is not None: yield self.element

    @property
    def pozitivan(self): return self.element != ε
    @property
    def beskonačan(self): return False
    @property
    def prazan(self): return self.element is None
    @property
    def trivijalan(self): return self.element in {None, ε}
    @property
    def korišteni_znakovi(self):
        return set() if self.trivijalan else {self.element}

    def bez_ε(self):
        if self.element == ε: return Elementaran(None)
        return self

    def NKA(self, abeceda=None):
        if abeceda is None: abeceda = self.korišteni_znakovi
        if self.trivijalan:
            stanja = {'q0'}
            prijelaz = set()
            završna = {'q0'} if self.element == ε else set()
        else:
            stanja = {'q0', 'q1'}
            prijelaz = {('q0', self.element, 'q1')}
            završna = {'q1'}
        return NedeterminističkiKonačniAutomat.definicija(
            stanja, abeceda, prijelaz, 'q0', završna)

    def reverz(self): return self

a = Elementaran('a')
b = Elementaran('b')
c = Elementaran('c')
nula = Elementaran('0')
jedan = Elementaran('1')
epsilon = Elementaran(ε)
prazan = Elementaran(None)


class BinaranRegularanIzraz(RegularanIzraz):
    def __init__(self, ri1, ri2):
        for ri in ri1, ri2: assert isinstance(ri, RegularanIzraz)
        self.lijevo, self.desno = ri1, ri2

    @property
    def korišteni_znakovi(self):
        return self.lijevo.korišteni_znakovi | self.desno.korišteni_znakovi

class Unija(BinaranRegularanIzraz):
    def __str__(self):
        return '({}|{})'.format(self.lijevo, self.desno)
    
    def jezik(self):
        if self.lijevo.beskonačan:
            if self.desno.beskonačan:
                for lijevo, desno in zip(self.lijevo, self.desno):
                    yield from [lijevo, desno]
            else:
                yield from self.desno
                yield from self.lijevo
        else:
            yield from self.lijevo
            yield from self.desno

    @property
    def pozitivan(self): return self.lijevo.pozitivan and self.desno.pozitivan
    @property
    def beskonačan(self):
        return self.lijevo.beskonačan or self.desno.beskonačan
    @property
    def prazan(self): return self.lijevo.prazan and self.desno.prazan
    @property
    def trivijalan(self):
        return self.lijevo.trivijalan and self.desno.trivijalan

    def bez_ε(self):
        return Unija(self.lijevo.bez_ε(), self.desno.bez_ε())

    def NKA(self, abeceda=None):
        if abeceda is None: abeceda = self.korišteni_znakovi
        return nedeterministička_unija(self.lijevo.NKA(abeceda),
                                       self.desno.NKA(abeceda))

    def reverz(self):
        return Unija(self.lijevo.reverz(), self.desno.reverz())

class Konkatenacija(BinaranRegularanIzraz):
    def __str__(self): return '({}{})'.format(self.lijevo, self.desno)

    def jezik(self):
        if self.lijevo.beskonačan:
            if self.desno.beskonačan:
                dosad = []
                for lijevo in self.lijevo:
                    dosad.append(lijevo)
                    for lijevo1, desno in zip(reversed(dosad), self.desno):
                        yield lijevo1 + desno
            else:
                for lijevo in self.lijevo:
                    for desno in self.desno:
                        yield lijevo + desno
        else:
            for desno in self.desno:
                for lijevo in self.lijevo:
                    yield lijevo + desno

    @property
    def pozitivan(self): return self.lijevo.pozitivan or self.desno.pozitivan
    @property
    def beskonačan(self):
        if self.prazan: return False
        return self.lijevo.beskonačan or self.desno.beskonačan
    @property
    def prazan(self): return self.lijevo.prazan or self.desno.prazan
    @property
    def trivijalan(self):
        if self.prazan: return True
        return self.lijevo.trivijalan and self.desno.trivijalan

    def bez_ε(self):
        return Unija(Konkatenacija(self.lijevo, self.desno.bez_ε()),
                     Konkatenacija(self.lijevo.bez_ε(), self.desno))

    def NKA(self, abeceda=None):
        if abeceda is None: abeceda = self.korišteni_znakovi
        return nedeterministička_konkatenacija(self.lijevo.NKA(abeceda),
                                               self.desno.NKA(abeceda))

    def reverz(self):
        return Konkatenacija(self.desno.reverz(), self.lijevo.reverz())

class KleeneZvijezda(RegularanIzraz):
    def __init__(self, ri):
        assert isinstance(ri, RegularanIzraz)
        self.ispod = ri

    def __str__(self):
        return str(self.ispod) + '*'

    def jezik(self):
        yield ε
        if not self.trivijalan:
            yield from self.bez_ε()

    @property
    def pozitivan(self): return False
    @property
    def beskonačan(self): return not self.trivijalan
    @property
    def prazan(self): return False
    @property
    def trivijalan(self): return self.ispod.trivijalan
    @property
    def korišteni_znakovi(self): return self.ispod.korišteni_znakovi

    def bez_ε(self):
        return KleenePlus(self.ispod.bez_ε())

    def NKA(self, abeceda=None):
        if abeceda is None: abeceda = self.korišteni_znakovi
        return nedeterministička_zvijezda(self.ispod.NKA(abeceda))

    def reverz(self):
        return KleeneZvijezda(self.ispod.reverz())

def KleenePlus(ri):
    return Konkatenacija(ri, KleeneZvijezda(ri))

def KleeneUpitnik(ri):
    return Unija(epsilon, ri)


def početak(ri, n=5):
    return list(itertools.islice(ri, n))


def primjer1():
    binarni = nula | jedan * -(nula | jedan)
    print(početak(binarni, 10))
    print(binarni.NKA())

def primjer2():  # page 65 example 1.53
    sigma = nula | jedan
    r1 = -nula * jedan * -nula
    r1.KA().provjeri(lambda ulaz: ulaz.count('1') == 1)
    r2 = -sigma * jedan * -sigma
    r2.KA().provjeri(lambda ulaz: '1' in ulaz)
    r3 = -sigma * nula * nula * jedan * -sigma
    r3.KA().provjeri(lambda ulaz: '001' in ulaz)
    r4 = -jedan * -(nula * +jedan)
    def spec4(ulaz):
        for i in range(len(ulaz)):
            if ulaz[i] == '0' and (i+1 >= len(ulaz) or ulaz[i+1] != '1'):
                return False
        return True
    r4.KA().provjeri(spec4)
    r5 = -(sigma ** 2)
    r5.KA().provjeri(lambda ulaz: not len(ulaz)%2)
    r6 = -(sigma ** 3)
    r6.KA().provjeri(lambda ulaz: not len(ulaz)%3)
    r7 = nula * jedan | jedan * nula
    r7.KA().provjeri(lambda ulaz: ulaz in {'01', '10'})
    r8 = nula*-sigma*nula | jedan*-sigma*jedan | sigma
    r8.KA().provjeri(lambda ulaz: ulaz and ulaz[0] == ulaz[~0])
    r9 = (nula | epsilon) * -jedan
    r9.KA().provjeri(lambda ulaz: '0' not in ulaz or ulaz.rindex('0') == 0)
    r10 = (nula | epsilon) * (jedan | epsilon)
    r10.KA().provjeri(lambda ulaz: ulaz in {ε, '0', '1', '01'})
    r11 = -jedan * prazan
    r11.KA().provjeri(lambda ulaz: False)
    r12 = -prazan
    r12.KA(sigma.korišteni_znakovi).provjeri(lambda ulaz: ulaz == ε)


def primjer3():
    r1 = -(a*b | a)  # page 68 example 1.56
    r1.NKA().ispiši()
    r2 = -(a|b) * a * b * a  # page 60 example 1.58 
    r2.NKA().ispiši()
    r2.KA().provjeri(lambda ulaz: ulaz.endswith('aba'))

def primjer4():  # page 76 figure 1.69
    p = -(a*a | b)
    t = (b*a | a)*p
    r1 = a*p*a*b | b
    r2 = t | b*b
    r3 = ~t
    r4 = a * p
    r = r1 * -r2 * r3 | r4
    print(r)
    return r

def primjer5():  # page 88 excercise 1.28
    ra = a * -(a*b*b) | b
    rb = +a | +(a*b)
    rc = (a | +b) * +a * +b
    return ra, rb, rc


if __name__ == '__main__':
    primjer1()
    primjer2()
    primjer3()
    primjer4()
