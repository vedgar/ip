"""Pomoćne klase, funkcije i objekti za neke programe u PJ."""


import collections, types, warnings, fractions


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


referentne_atomske_mase = dict(H=1.00797, He=4.00260, Li=6.941, Be=9.01218,
    B=10.81, C=12.011, N=14.0067, O=15.9994, F=18.998403, Ne=20.179,
    Na=22.98977, Mg=24.305, Al=26.98154, Si=28.0855, P=30.97376, S=32.06,
    Cl=35.453, Ar=39.948, K=39.0983, Ca=40.08, Sc=44.9559, Ti=47.90,
    V=50.9415, Cr=51.996, Mn=54.9380, Fe=55.847, Co=58.9332, Ni=58.70,
    Cu=63.546, Zn=65.38, Ga=69.72, Ge=72.59, As=74.9216, Se=78.96, Br=79.904,
    Kr=83.80, Rb=85.4678, Sr=87.62, Y=88.9059, Zr=91.22, Nb=92.9064, Mo=95.94,
    Tc=98, Ru=101.07, Rh=102.9055, Pd=106.4, Ag=107.868, Cd=112.41, In=114.82,
    Sn=118.69, Sb=121.75, Te=127.60, I=126.9045, Xe=131.30, Cs=132.9054,
    Ba=137.33, La=138.9055, Ce=140.12, Pr=140.9077, Nd=144.24, Pm=145,
    Sm=150.4, Eu=151.96, Gd=157.25, Tb=158.9254, Dy=162.50, Ho=164.9304,
    Er=167.26, Tm=168.9342, Yb=173.04, Lu=174.967, Hf=178.49, Ta=180.9479,
    W=183.85, Re=186.207, Os=190.2, Ir=192.22, Pt=195.09, Au=196.9665,
    Hg=200.59, Tl=204.37, Pb=207.2, Bi=208.9804, Po=209, At=210, Rn=222,
    Fr=223, Ra=226.0254, Ac=227.0278, Th=232.0381, Pa=231.0359, U=238.029,
    Np=237.0482, Pu=242, Am=243, Cm=247, Bk=247, Cf=251, Es=252, Fm=257,
    Md=258, No=250, Lr=260, Rf=261, Db=262, Sg=263, Bh=262, Hs=255, Mt=256,
    Ds=269, Rg=272, Cn=285, Nh=286, Fl=289, Mc=290, Lv=293, Ts=294, Og=294)


def Python_eval(izraz):
    """Kao Pythonov eval, ali bez warninga i grešaka koje nisu sintaksne."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try: return eval(izraz)
        except TypeError: raise SyntaxError
