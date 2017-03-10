from KA import *

tests = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}

if 1 in tests:  # page 34 figure 1.4  # page 36 figure 1.6
    M1 = KonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q2
        q2 q3 q2 #
        q3 q2 q2   ''')
    print(*M1.izračunavanje('1101'))
    for riječ in '1','01','11','0101010101','100','0100','110000','0101000000':
        assert M1.prihvaća(riječ)
    for riječ in '0', '10', '101000':
        assert not M1.prihvaća(riječ)
    provjeri(M1, lambda ulaz: djeljiv(ulaz[::-1].find('1'), 2))

if 2 in tests:  # page 37 example 1.7 figure 1.8
    M2 = KonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q2
        q2 q1 q2 # ''')
    print(*M2.izračunavanje('1101'), *M2.izračunavanje('110'))
    provjeri(M2, lambda ulaz: ulaz.endswith('1'))

if 3 in tests:  # page 38 example 1.9 figure 1.10
    M3 = KonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q2 #
        q2 q1 q2   ''')
    provjeri(M3, lambda ulaz: ulaz == ε or ulaz.endswith('0'))

if 4 in tests:  # page 38 example 1.11 figure 1.12
    M4 = KonačniAutomat.iz_tablice('''
           a  b
        s  q1 r1
        q1 q1 q2 #
        q2 q1 q2
        r1 r2 r1 #
        r2 r2 r1    ''')
    for riječ in 'a', 'b', 'aa', 'bb', 'bab':
        assert M4.prihvaća(riječ)
    for riječ in 'ab', 'ba', 'bbba':
        assert not M4.prihvaća(riječ)
    provjeri(M4, lambda ulaz: ulaz and ulaz[0] == ulaz[~0])

if 5 in tests:  # page 39 example 1.13 figure 1.14
    M5 = KonačniAutomat.iz_tablice('''
           R  0  1  2
        q0 q0 q0 q1 q2 #
        q1 q0 q1 q2 q0
        q2 q0 q2 q0 q1   ''')
    print(*M5.izračunavanje('10R22R012'))  # page 41 example 1.17

    def M5_spec(ulaz):
        zbroj = 0
        for znak in ulaz:
            if znak == 'R': zbroj = 0
            else: zbroj += int(znak)
        return djeljiv(zbroj, 3)
    provjeri(M5, M5_spec)

if 6 in tests:  # page 40 example 1.15
    for i in range(1, 10):
        def Ai(ulaz):
            zbroj = 0
            for znak in ulaz:
                if znak == '<RESET>': zbroj = 0
                else: zbroj += int(znak)
            return djeljiv(zbroj, i)
        Qi = set(range(i))
        Σ = {'<RESET>', 0, 1, 2}
        δi = {}
        for j in Qi:
            δi[j, '<RESET>'] = 0
            δi[j, 0] = j
            δi[j, 1] = (j + 1) % i
            δi[j, 2] = (j + 2) % i
        Bi = KonačniAutomat.iz_komponenti(Qi, Σ, δi, 0, {0})
        provjeri(Bi, Ai)
        print(i, end=' OK  ')

if 7 in tests:  # page 43 figure 1.20
    E1 = KonačniAutomat.iz_tablice('''
              0     1
        qeven qeven qodd
        qodd  qodd  qeven # ''')
    provjeri(E1, lambda ulaz: ulaz.count('1') % 2)

if 8 in tests:  # page 44 example 1.21 figure 1.22
    E2 = KonačniAutomat.iz_tablice('''
             0    1
        q    q0   q
        q0   q00  q
        q00  q00  q001
        q001 q001 q001 # ''')
    provjeri(E2, lambda ulaz: '001' in ulaz)

if 9 in tests:
    E1u2 = E1.unija(E2)
    provjeri(E1u2, lambda ulaz: E1.prihvaća(ulaz) or E2.prihvaća(ulaz))
    ispiši(E1u2)

    E1n2 = E1.presjek(E2)
    provjeri(E1n2, lambda ulaz: E1.prihvaća(ulaz) and E2.prihvaća(ulaz))
    print(*E1n2.izračunavanje('101'))

    E1n2.prirodni().crtaj()

    E1k = E1.komplement()
    provjeri(E1k, lambda ulaz: not E1.prihvaća(ulaz))

    E1b2 = E1.razlika(E2)
    provjeri(E1b2, lambda ulaz: E1.prihvaća(ulaz) > E2.prihvaća(ulaz))

    E1t2 = E1.optimizirana_simetrična_razlika(E2)
    provjeri(E1t2, lambda ulaz: E1.prihvaća(ulaz) ^ E2.prihvaća(ulaz))

if 10 in tests:  # page 48 figure 1.27
    N1 = NedeterminističkiKonačniAutomat.iz_komponenti({'q1', 'q2', 'q3', 'q4'},
        {'0', '1'}, {('q1', '0', 'q1'), ('q1', '1', 'q1'), ('q1', '1', 'q2'),
                     ('q2', '0', 'q3'), ('q2', ε, 'q3'), ('q3', '1', 'q4'),
                     ('q4', '0', 'q4'), ('q4', '1', 'q4')}, 'q1', {'q4'})
    assert N1 == NedeterminističkiKonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q1/q2
        q2 q3 /     q3
        q3 /  q4
        q4 q4 q4       #''')  # page 54 example 1.38

    provjeri(N1, lambda ulaz: '101' in ulaz or '11' in ulaz)
    print(*N1.izračunavanje('010110'))  # page 49 figure 1.29
    print(*N1.izračunavanje('010'))

    N1b = NedeterminističkiKonačniAutomat.iz_komponenti({1,2,3,4}, {0,1},
    {(1,0,1),(1,1,1),(1,1,2),(2,0,3),(2,ε,3),(3,1,4),(4,0,4),(4,1,4)}, 1, {4})
    D1b = N1b.optimizirana_partitivna_konstrukcija()

if 11 in tests:  # page 51 example 1.30 figure 1.31
    N2 = NedeterminističkiKonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q1/q2
        q2 q3 q3
        q3 q4 q4
        q4 /  /  # ''')
    provjeri(N2, lambda ulaz: len(ulaz) >= 3 and ulaz[~2] == '1')
    D2 = N2.optimizirana_partitivna_konstrukcija()
    D2.prirodni().crtaj()
    print(len(D2.stanja), len(D2.prijelaz))

    N2c = copy.deepcopy(N2)
    N2c.prijelaz |= {('q2', ε, 'q3'), ('q3', ε, 'q4')}
    provjeri(N2c, lambda ulaz: '1' in ulaz[~2:])

if 12 in tests:  # page 52 example 1.33
    N3 = NedeterminističkiKonačniAutomat.iz_tablice('''
            0
        0   / 20 30
        20 21 #
        21 20
        30 31 #
        31 32
        32 30''')
    for ulaz in ε, '00', '000', '0000', '000000':
        assert N3.prihvaća(ulaz)
    for ulaz in '0', '00000':
        assert not N3.prihvaća(ulaz)
    provjeri(N3, lambda ulaz: djeljiv(len(ulaz), 2) or djeljiv(len(ulaz), 3))

if 13 in tests:  # page 52 example 1.35 figure 1.36
    N4 = NedeterminističkiKonačniAutomat.iz_tablice('''
            a     b
        q1  /     q2  q3  #
        q2  q2/q3 q3
        q3  q1    /''')
    for ulaz in ε, 'a', 'baba', 'baa':
        assert N4.prihvaća(ulaz)
    for ulaz in 'b', 'bb', 'babba':
        assert not N4.prihvaća(ulaz)
    D4 = N4.partitivna_konstrukcija()  # page 58 example 1.41
    D4.prirodni().crtaj()  # figure 1.43
    N4.optimizirana_partitivna_konstrukcija().crtaj()  # figure 1.44

if 14 in tests:
    N1 = NedeterminističkiKonačniAutomat.iz_komponenti(
        {0, 1}, {'a'}, {(0, 'a', 1), (1, 'a', 0)}, 0, {0})
    N2 = NedeterminističkiKonačniAutomat.iz_komponenti(
        {0, 1, 2}, {'a'}, {(0, 'a', 1), (1, 'a', 2), (2, 'a', 0)}, 0, {0})
    N1u2 = N1.unija(N2)
    N1o2 = N1.konkatenacija(N2)
    N1o2.crtaj()
