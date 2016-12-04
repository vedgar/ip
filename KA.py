import random, itertools, operator, types, pprint


Kartezijev_produkt = lambda *skupovi: set(itertools.product(*skupovi))
funkcija = lambda f, A, B: f.keys() == A and set(f.values()) <= B
petorka = operator.attrgetter(
    'stanja', 'abeceda', 'prijelaz', 'početno', 'završna')


class KonačniAutomat(types.SimpleNamespace):
    @classmethod
    def definicija(klasa, stanja, abeceda, prijelaz, početno, završna):
        assert abeceda and početno in stanja and završna <= stanja
        assert funkcija(prijelaz, Kartezijev_produkt(stanja, abeceda), stanja)
        return klasa(**locals())

    @classmethod
    def iz_tablice(klasa, tablica):
        prva, *ostale = tablica.strip().splitlines()
        znakovi = prva.split()
        assert all(len(znak) == 1 for znak in znakovi)
        abeceda = set(znakovi)
        stanja, završna = set(), set()
        prijelaz, početno = {}, None
        for linija in ostale:
            stanje, *dolazna = linija.split()
            if početno is None: početno = stanje
            extra = len(dolazna) - len(znakovi)
            assert extra in {0, 1}
            if extra == 1:
                assert dolazna.pop() == '#'
                završna.add(stanje)
            for znak, dolazno in zip(znakovi, dolazna):
                prijelaz[stanje, znak] = dolazno
            stanja.add(stanje)
        return klasa.definicija(stanja, abeceda, prijelaz, početno, završna)

    ispiši = lambda automat: pprint.pprint(petorka(automat))

    def prihvaća(automat, ulaz):
        stanje = automat.početno
        for znak in ulaz: stanje = automat.prijelaz[stanje, znak]
        return stanje in automat.završna

    def slučajni_testovi(automat, koliko=None, maxduljina=None):
        znakovi = list(automat.abeceda)
        yield ''
        yield from znakovi
        if maxduljina is None: maxduljina = max(len(automat.stanja), 3)
        if koliko is None: koliko = max(len(znakovi) ** maxduljina, 99)
        for _ in range(koliko):
            duljina = random.randint(2, maxduljina)
            yield ''.join(random.choice(znakovi) for _ in range(duljina))

    def provjeri(automat, specifikacija):
        for test in automat.slučajni_testovi():
            lijevo = automat.prihvaća(test)
            desno = specifikacija(test)
            if lijevo != bool(desno):
                print('!!Kontraprimjer', repr(test), lijevo, desno)
                break
        return specifikacija

    def log(automat, ulazi):
        ulazi = ulazi.split()
        najduljina = max(map(len, ulazi))
        for ulaz in ulazi:
            print(ulaz.ljust(najduljina), automat.prihvaća(ulaz))
        print('END'.rjust(najduljina + 6, '-'))

    def debug(automat, ulaz):
        stanje = automat.početno
        for znak in ulaz:
            print(stanje, znak, end=' ')
            stanje = automat.prijelaz[stanje, znak]
        print(stanje, stanje in automat.završna)


M1 = KonačniAutomat.iz_tablice(
'''0  1
q1 q1 q2
q2 q3 q2 #
q3 q2 q2   ''')  # page 34 figure 1.4  # page 36 figure 1.6
M1.log('1 01 11 0101010101 100 0100 110000 0101000000 0 10 101000')

M2 = KonačniAutomat.iz_tablice(
'''0  1
q1 q1 q2
q2 q1 q2 # ''')  # page 37 example 1.7 figure 1.8
M2.log('1101')
M2.provjeri(lambda ulaz: ulaz.endswith('1'))

M3 = KonačniAutomat.iz_tablice(
'''0  1
q1 q1 q2 #
q2 q1 q2   ''')  # page 38 example 1.9 figure 1.10
M3.provjeri(lambda ulaz: ulaz.endswith('0') or not ulaz)

M4 = KonačniAutomat.iz_tablice('''
   a  b
s  q1 r1
q1 q1 q2 #
q2 q1 q2
r1 r2 r1 #
r2 r2 r1
''')  # page 38 example 1.11 figure 1.12
M4.log('a b aa bb bab ab ba bbba')
M4.provjeri(lambda ulaz: ulaz and ulaz[0] == ulaz[~0])

M5 = KonačniAutomat.iz_tablice('''
   R  0  1  2
q0 q0 q0 q1 q2 #
q1 q0 q1 q2 q0
q2 q0 q2 q0 q1
''')  # page 39 example 1.13 figure 1.14
M5.log('10R22R012')

@M5.provjeri
def M5_spec(ulaz):
    zbroj = 0
    for znak in ulaz:
        if znak == 'R': zbroj = 0
        else: zbroj += int(znak)
    return not zbroj % 3

E1 = KonačniAutomat.iz_tablice('''
      0     1
qeven qeven qodd
qodd  qodd  qeven #
''')  # page 43 figure 1.20
E1.provjeri(lambda ulaz: ulaz.count('1') % 2)

E2 = KonačniAutomat.iz_tablice('''
     0    1
q    q0   q
q0   q00  q
q00  q00  q001
q001 q001 q001 #
''')  # page 44 example 1.21 figure 1.22
E2.provjeri(lambda ulaz: '001' in ulaz)


def Kartezijeva_konstrukcija_unija(M1, M2):
    Q1, Σ1, δ1, q1, F1 = petorka(M1)
    Q2, Σ2, δ2, q2, F2 = petorka(M2)
    Q = Kartezijev_produkt(Q1, Q2)
    assert Σ1 == Σ2
    Σ = Σ1
    δ = {((r1, r2), a): (δ1[r1, a], δ2[r2, a]) for r1, r2 in Q for a in Σ}
    q0 = q1, q2
    F = Kartezijev_produkt(Q1, F2) | Kartezijev_produkt(F1, Q2)
    return KonačniAutomat.definicija(Q, Σ, δ, q0, F)

def Kartezijeva_konstrukcija_presjek(M1, M2):
    M = Kartezijeva_konstrukcija_unija(M1, M2)
    M.završna = Kartezijev_produkt(M1.završna, M2.završna)
    return M


E1u2 = Kartezijeva_konstrukcija_unija(E1, E2)
E1u2.provjeri(lambda ulaz: ulaz.count('1') % 2 or '001' in ulaz)
E1u2.ispiši()

E1n2 = Kartezijeva_konstrukcija_presjek(E1, E2)
E1n2.provjeri(lambda ulaz: ulaz.count('1') % 2 and '001' in ulaz)
E1n2.debug('101')
