from types import SimpleNamespace
import random, itertools


class KonačniAutomat(SimpleNamespace):
    if False:
      def __init__(automat, početno, završna, prijelaz):
        automat.stanja = {stanje for stanje, znak in prijelaz}
        automat.abeceda = {znak for stanje, znak in prijelaz}
        assert automat.abeceda
        automat.prijelaz = prijelaz
        assert prijelaz.keys() == set(
            itertools.product(automat.stanja, automat.abeceda))
        assert automat.stanja.issuperset(prijelaz.values())
        automat.početno = početno
        assert automat.početno in automat.stanja
        automat.završna = set(završna)
        assert automat.završna <= automat.stanja

    def __init__(M, tablica):
        prva, *ostale = tablica.strip().splitlines()
        znakovi = prva.split()
        assert set(map(len, znakovi)) == {1}
        M.abeceda = set(znakovi)
        M.stanja, M.završna, sva_dolazna = set(), set(), set()
        M.prijelaz = {}
        for linija in ostale:
            stanje, *dolazna = linija.split()
            if not hasattr(M, 'početno'): M.početno = stanje
            extra = len(dolazna) - len(znakovi)
            if extra == 1:
                assert dolazna.pop() == '#'
                M.završna.add(stanje)
            else: assert not extra
            sva_dolazna.update(dolazna)
            for znak, dolazno in zip(M.abeceda, dolazna):
                M.prijelaz[stanje, znak] = dolazno
            M.stanja.add(stanje)
        assert sva_dolazna <= M.stanja

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


M1 = KonačniAutomat(
'''0  1
q1 q1 q2
q2 q3 q2 #
q3 q2 q2   ''')
M1.log('1 01 11 0101010101 100 0100 110000 0101000000 0 10 101000')

M2 = KonačniAutomat(
'''0  1
q1 q1 q2
q2 q1 q2 # ''')
M2.log('1101')
M2.provjeri(lambda ulaz: ulaz.endswith('1'))

M3 = KonačniAutomat(
'''0  1
q1 q1 q2 #
q2 q1 q2   ''')
M3.provjeri(lambda ulaz: ulaz.endswith('0') or not ulaz)

M4 = KonačniAutomat('''
   a  b
s  q1 r1
q1 q1 q2 #
q2 q1 q2
r1 r2 r1 #
r2 r2 r1
''')
M4.log('a b aa bb bab ab ba bbba')
M4.provjeri(lambda ulaz: ulaz and ulaz[0] == ulaz[~0])

M5 = KonačniAutomat('''
   R  0  1  2
q0 q0 q0 q1 q2 #
q1 q0 q1 q2 q0
q2 q0 q2 q0 q1
''')
