import collections, types


class Polinom(collections.Counter):
    @classmethod
    def konstanta(klasa, broj): return klasa({0: broj})

    @classmethod
    def x(klasa, eksponent=1): return klasa({eksponent: 1})

    def __add__(p, q):
        r = Polinom(p)
        for exp in q: r[exp] += q[exp]
        return r

    def __mul__(p, q):
        r = Polinom()
        for e1, k1 in p.items():
            for e2, k2 in q.items(): r[e1 + e2] += k1 * k2
        return r

    def __neg__(p): return Polinom.konstanta(-1) * p

    def __sub__(p, q): return p + -q

    def __str__(p):
        monomi = []
        for e, k in sorted(p.items(), reverse=True):
            if not k: continue
            č = format(k, '+')
            if e:
                if abs(k) == 1: č = č.rstrip('1')  # samo '+' ili '-'
                č += 'x'
                if e > 1: č += str(e)
            monomi.append(č)
        return ''.join(monomi).lstrip('+') or '0'


class StrojSaStogom:
    def __init__(self): self.stog = []

    def PUSH(self, vrijednost): self.stog.append(vrijednost)

    def ADD(self): self.stog.append(self.stog.pop() + self.stog.pop())

    def MUL(self): self.stog.append(self.stog.pop() * self.stog.pop())

    def POW(self):
        eksponent, baza = self.stog.pop(), self.stog.pop()
        self.stog.append(baza ** eksponent)

    def izvrši(self, instr, *args): getattr(self, instr)(*args) 

    def __repr__(self): return '[ ' + ' '.join(map(str, self.stog)) + '<'

    @property
    def rezultat(self):
        [jedini_element_stoga] = self.stog
        return jedini_element_stoga


class RAMStroj:
    def __init__(self, *ulazi):
        self.registri = collections.Counter()
        for i, ulaz in enumerate(ulazi, 1): self.registri[i] = ulaz
    
    def inc(self, j): self.registri[j] += 1

    def dec(self, j):
        if self.registri[j]: self.registri[j] -= 1

    @property
    def rezultat(self): return self.registri[0]


class PristupLog(types.SimpleNamespace):
    """Broji pristupe pojedinom objektu."""

    def __init__(self, objekt):
        self.objekt = objekt
        self.pristup = 0

    def pristupi(self): self.pristup += 1


def logiran(niz, tag=None):
    logging.getLogger().setLevel(logging.DEBUG)
    if tag is None: tag = niz.__name__
    for element in niz:
        logging.debug('%s %r', tag, element)
        yield element
