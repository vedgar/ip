import random, itertools, types, contextlib, pprint, copy, collections
from KA import funkcija, Kartezijev_produkt, petorka, KonačniAutomat


class fset(frozenset): __repr__ = lambda self: repr(set(self)) if self else '∅'


def partitivni_generator(skup):
    for karakteristična in itertools.product({False, True}, repeat=len(skup)):
        yield fset(itertools.compress(skup, karakteristična))

partitivni_skup = lambda skup: set(partitivni_generator(skup))


relacija = lambda R, *skupovi: R <= Kartezijev_produkt(*skupovi)

def kolabiraj(vrijednost):
    with contextlib.suppress(TypeError, ValueError):
        komponenta, = vrijednost
        return komponenta
    return vrijednost

def funkcija_iz_relacije(relacija, *domene):
    m = len(domene)
    funkcija = {kolabiraj(x): set() for x in Kartezijev_produkt(*domene)}
    for n_torka in relacija:
        assert len(n_torka) > m
        for x_i, domena_i in zip(n_torka, domene):
            assert x_i in domena_i
        x, y = n_torka[:m], n_torka[m:]
        if len(x) == 1: x, = x
        if len(y) == 1: y, = y
        funkcija[kolabiraj(x)].add(kolabiraj(y))
    return funkcija

def relacija_iz_funkcije(funkcija):
    for (p, α), moguća_dolazna in funkcija.items():
        for q in moguća_dolazna:
            yield p, α, q


unija_familije = lambda fam: fset(x for skup in fam for x in skup)
dolazna = lambda δ, moguća, znak: unija_familije(δ[q, znak] for q in moguća)

def disjunktna_unija(*skupovi):
    for skup1, skup2 in itertools.combinations(skupovi, 2):
        assert skup1.isdisjoint(skup2)
    return set().union(*skupovi)

ε = epsilon = ''
ε_proširenje = lambda Σ: disjunktna_unija(Σ, {ε})

def ε_zatvorenje(δ, stanja):
    while True:
        nova_stanja = stanja | dolazna(δ, stanja, ε)
        if nova_stanja == stanja: return fset(stanja)
        stanja = nova_stanja


class NedeterminističkiKonačniAutomat(types.SimpleNamespace):
    @classmethod
    def definicija(klasa, stanja, abeceda, prijelaz, početno, završna):
        assert abeceda and početno in stanja and završna <= stanja
        assert relacija(prijelaz, stanja, ε_proširenje(abeceda), stanja)
        return klasa(**locals())

    @classmethod
    def funkcijska_definicija(klasa, stanja, abeceda, funkcija_prijelaza,
                              početno, završna):
        prijelaz = set(relacija_iz_funkcije(funkcija_prijelaza))
        return klasa.definicija(stanja, abeceda, prijelaz, početno, završna)

    @classmethod
    def iz_tablice(klasa, tablica):
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
        return klasa.definicija(stanja, abeceda, prijelaz, početno, završna)

    @classmethod
    def iz_konačnog_automata(klasa, konačni_automat):
        Q, Σ, δ, q0, F = petorka(konačni_automat)
        Δ = {(q, α, δ[q, α]) for q in Q for α in Σ}
        return klasa.definicija(Q, Σ, Δ, q0, F)

    @property
    def abeceda_ε(automat):
        return ε_proširenje(automat.abeceda)

    @property
    def funkcija_prijelaza(automat):
        return funkcija_iz_relacije(
            automat.prijelaz, automat.stanja, automat.abeceda_ε)

    ispiši = lambda automat: pprint.pprint(petorka(automat))

    def prihvaća(automat, ulaz):
        δ = automat.funkcija_prijelaza
        moguća = ε_zatvorenje(δ, {automat.početno})
        for znak in ulaz: moguća = ε_zatvorenje(δ, dolazna(δ, moguća, znak))
        return not moguća.isdisjoint(automat.završna)


def partitivna_konstrukcija(nka):
    Q, Σ, Δ, q0, F = petorka(nka)
    δ = nka.funkcija_prijelaza
    PQ = partitivni_skup(Q)
    δ_KA = {}
    F_KA = set()
    for stanje in PQ:
        for α in Σ:
            δ_KA[stanje, α] = ε_zatvorenje(δ, dolazna(δ, stanje, α))
        if not stanje.isdisjoint(F): F_KA.add(stanje)
    q0_KA = ε_zatvorenje(δ, fset({q0}))
    return KonačniAutomat.definicija(PQ, Σ, δ_KA, q0_KA, F_KA)


def optimizirana_partitivna_konstrukcija(nka):
    Q, Σ, Δ, q0, F = petorka(nka)
    δ = nka.funkcija_prijelaza
    Q_KA = set()
    δ_KA = {}
    F_KA = set()
    q0_KA = ε_zatvorenje(δ, fset({q0}))
    red = collections.deque([q0_KA])
    while red:
        stanje = red.popleft()
        if stanje not in Q_KA:
            for α in Σ:
                novo_stanje = ε_zatvorenje(δ, dolazna(δ, stanje, α))
                δ_KA[stanje, α] = novo_stanje
                red.append(novo_stanje)
            Q_KA.add(stanje)
            if not stanje.isdisjoint(F): F_KA.add(stanje)
    return KonačniAutomat.definicija(Q_KA, Σ, δ_KA, q0_KA, F_KA)


def označi1(stanje, l):
    with contextlib.suppress(TypeError):
        return stanje + l
    with contextlib.suppress(TypeError):
        return (*stanje, l)
    return stanje, l

def označi(nka, l):
    Q, Σ, Δ, q0, F = petorka(nka)
    Ql = {označi1(q, l) for q in Q}
    Δl = {(označi1(p, l), α, označi1(q, l)) for p, α, q in Δ}
    q0l = označi1(q0, l)
    Fl = {označi1(q, l) for q in F}
    return NedeterminističkiKonačniAutomat.definicija(Ql, Σ, Δl, q0l, Fl)

def novo(prefiks, iskorišteni):
    if prefiks in iskorišteni:
        for broj in itertools.count():
            kandidat = prefiks + str(broj)
            if kandidat not in iskorišteni:
                return kandidat
    return prefiks


def nedeterministička_unija(N1, N2):
    if not N1.stanja.isdisjoint(N2.stanja):
        N1 = označi(N1, '1')
        N2 = označi(N2, '2')
    q0 = novo('q0', N1.stanja | N2.stanja)
    Q1, Σ1, Δ1, q1, F1 = petorka(N1)
    Q2, Σ2, Δ2, q2, F2 = petorka(N2)
    assert Σ1 == Σ2
    Q = disjunktna_unija(Q1, Q2, {q0})
    F = disjunktna_unija(F1, F2)
    Δ = Δ1 | Δ2 | {(q0, ε, q1), (q0, ε, q2)}
    return NedeterminističkiKonačniAutomat.definicija(Q, Σ1, Δ, q0, F)


def nedeterministička_konkatenacija(N1, N2):
    if not N1.stanja.isdisjoint(N2.stanja):
        N1 = označi(N1, '3')
        N2 = označi(N2, '4')
    Q1, Σ1, Δ1, q1, F1 = petorka(N1)
    Q2, Σ2, Δ2, q2, F2 = petorka(N2)
    assert Σ1 == Σ2
    Q = disjunktna_unija(Q1, Q2)
    Δ = Δ1 | Δ2 | {(p1, ε, q2) for p1 in F1}
    return NedeterminističkiKonačniAutomat.definicija(Q, Σ1, Δ, q1, F2)


def nedeterministički_plus(N):
    Q, Σ, Δ, q0, F = petorka(N)
    Δ_plus = Δ | {(p, ε, q0) for p in F}
    return NedeterminističkiKonačniAutomat.definicija(Q, Σ, Δ_plus, q0, F)


def nedeterministička_zvijezda(N):
    Q, Σ, Δ, q0, F = petorka(nedeterministički_plus(N))
    poč = novo('q0', Q)
    return NedeterminističkiKonačniAutomat.definicija(
        Q | {poč}, Σ, Δ | {(poč, ε, q0)}, poč, F | {poč})


def nedeterministički_reverz(N):
    Q, Σ, Δ, q0, F = petorka(N)
    kraj = novo('qz', Q)
    Δ_ᴙ = {(q, α, p) for p, α, q in Δ} | {(kraj, ε, z) for z in F}
    return NedeterminističkiKonačniAutomat.definicija(
        Q | {kraj}, Σ, Δ_ᴙ, kraj, {q0})


def primjer():
    N1 = NedeterminističkiKonačniAutomat.definicija({'q1', 'q2', 'q3', 'q4'},
        {'0', '1'}, {('q1', '0', 'q1'), ('q1', '1', 'q1'), ('q1', '1', 'q2'),
                     ('q2', '0', 'q3'), ('q2', ε, 'q3'), ('q3', '1', 'q4'),
                     ('q4', '0', 'q4'), ('q4', '1', 'q4')}, 'q1', {'q4'})
    
    assert N1 == NedeterminističkiKonačniAutomat.iz_tablice('''
       0  1
    q1 q1 q1/q2
    q2 q3 /     q3
    q3 /  q4
    q4 q4 q4       #''')  # page 48 figure 1.27

    D1 = optimizirana_partitivna_konstrukcija(N1)
    D1.debug('010110')  # page 49 figure 1.29
    D1.debug('010')
    D1.provjeri(lambda ulaz: '101' in ulaz or '11' in ulaz)

    N1b = NedeterminističkiKonačniAutomat.definicija({1,2,3,4}, {0,1},
    {(1,0,1),(1,1,1),(1,1,2),(2,0,3),(2,'',3),(3,1,4),(4,0,4),(4,1,4)}, 1, {4})
    D1b = optimizirana_partitivna_konstrukcija(N1b)

    N2 = NedeterminističkiKonačniAutomat.iz_tablice('''
       0  1
    q1 q1 q1/q2
    q2 q3 q3
    q3 q4 q4
    q4 /  /  #''')  # page 51 example 1.30

    D2 = optimizirana_partitivna_konstrukcija(N2)
    print(len(D2.stanja), len(D2.prijelaz))
    D2.provjeri(lambda ulaz: len(ulaz) >= 3 and ulaz[~2] == '1')

    N2c = copy.deepcopy(N2)
    N2c.prijelaz |= {('q2', epsilon, 'q3'), ('q3', epsilon, 'q4')}

    D2c = optimizirana_partitivna_konstrukcija(N2c)
    D2c.provjeri(lambda ulaz: '1' in ulaz[~2:])

    N3 = NedeterminističkiKonačniAutomat.iz_tablice('''
        0
    0  / 20 30
    20 21 #
    21 20
    30 31 #
    31 32
    32 30''')  # page 52 example 1.33

    D3 = optimizirana_partitivna_konstrukcija(N3)
    D3.provjeri(lambda ulaz: not len(ulaz) % 2 or not len(ulaz) % 3)

    N4 = NedeterminističkiKonačniAutomat.iz_tablice('''
        a     b
    q1  /     q2  q3  #
    q2  q2/q3 q3
    q3  q1    /''')  # page 52 example 1.35

    D4 = optimizirana_partitivna_konstrukcija(N4)  # page 56 example 1.41
    D4.log('a baba baa b bb babba')

    N1 = NedeterminističkiKonačniAutomat.definicija(
        {0, 1}, {'a'}, {(0, 'a', 1), (1, 'a', 0)}, 0, {0})
    N2 = NedeterminističkiKonačniAutomat.definicija(
        {0, 1, 2}, {'a'}, {(0, 'a', 1), (1, 'a', 2), (2, 'a', 0)}, 0, {0})
    N1u2 = nedeterministička_unija(N1, N2)
    N1o2 = nedeterministička_konkatenacija(N1, N2)


if __name__ == '__main__':
    primjer()
