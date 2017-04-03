from KA import *
from RI import *
from PA import *
from BKG import *


tests = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
tests |= {21, 22, 23, 24, 25, 26, 27, 28, 29, 30}
tests |= {31, 32, 33, 34, 35, 36, 37, 38, 39, 40}
tests = {41, 42, 43, 44, 45, 46, 47, 48, 49, 50}

# tests = {31, 32, 33, 34, 35, 36, 37, 38, 39, 40}


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


if 21 in tests:
    binarni = nula | jedan * (nula|jedan).z
    print(binarni.početak())
    binarni.NKA().crtaj()


if 22 in tests:
    primjer1 = (nula | jedan) * nula.z  # page 63
    print(primjer1.početak())
    provjeri(primjer1, lambda ulaz: ulaz != ε and '1' not in ulaz[1:])


if 23 in tests:  # page 64 example 1.51
    sve = (nula|jedan).z
    print(sve.početak())
    provjeri(sve, lambda ulaz: True)
    provjeri(nula*sve | sve*jedan,
             lambda ulaz: ulaz.startswith('0') or ulaz.endswith('1'))
    

if 24 in tests:  # page 65 example 1.53
    sigma = nula | jedan
    r1 = nula.z * jedan * nula.z
    provjeri(r1, lambda ulaz: ulaz.count('1') == 1)
    r2 = sigma.z * jedan * sigma.z
    provjeri(r2, lambda ulaz: '1' in ulaz)
    r3 = sigma.z * nula * nula * jedan * sigma.z
    provjeri(r3, lambda ulaz: '001' in ulaz)
    r4 = jedan.z * (nula*jedan.p).z
    provjeri(r4, lambda ulaz: '00' not in ulaz and not ulaz.endswith('0'))
    r5 = (sigma**2).z
    provjeri(r5, lambda ulaz: djeljiv(len(ulaz), 2))
    r6 = (sigma**3).z
    provjeri(r6, lambda ulaz: djeljiv(len(ulaz), 3))
    r7 = nula * jedan | jedan * nula
    print(r7.konačan(), r7.početak())
    r8 = nula*sigma.z*nula | jedan*sigma.z*jedan | sigma
    provjeri(r8, lambda ulaz: ulaz and ulaz[0] == ulaz[~0])
    r9 = nula.u * jedan.z
    print(r9.početak())
    r10 = nula.u * jedan.u
    print(r10.konačan(), r10.početak())
    r11 = jedan.z * prazan
    print(r11.prazan())
    r12 = prazan.z
    print(r12.prazan(), r12.trivijalan())


if 25 in tests:  # page 68 example 1.56
    e1 = (a*b|a).z
    e1.NKA().crtaj()


if 26 in tests:  # page 69 example 1.58 
    e2 = (a|b).z * a * b * a
    e2.NKA().crtaj()
    provjeri(e2, lambda ulaz: ulaz.endswith('aba'))


if 27 in tests:  # page 76 figure 1.69
    p = (a**2|b).z
    t = (b*a | a) * p
    r = (a*p*a).u * b * (t|b**2).z * t.u | a * p
    print(r)


if 28 in tests:  # page 88 excercise 1.28
    ra = a * (a*b*b).z | b
    rb = a.p | (a*b).p
    rc = (a | b.p) * a.p * b.p
    ra.NKA().crtaj()
    rb.NKA().crtaj()
    rc.NKA().crtaj()


if 31 in tests:  # page 114 example 2.14
    Ֆ = '$'

    M21 = PotisniAutomat.iz_komponenti({1, 2, 3, 4}, {0, 1}, {0, Ֆ},
        {(1,ε,ε,2,Ֆ), (2,0,ε,2,0), (2,1,0,3,ε), (3,1,0,3,ε), (3,ε,Ֆ,4,ε)},
        1, {1, 4})
    ispiši(M21)
    M21.crtaj()  # page 115 figure 2.15
    print(M21.prihvaća((0, 0, 1, 1)), M21.prihvaća((0, 1, 0, 1)))


if 32 in tests:  # page 114 example 2.14
    M21b = PotisniAutomat.iz_tablice('''
        q1 /  /  q2 $  #
        q2 0  /  q2 0
        q2 1  0  q3 /
        q3 1  0  q3 /
        q3 /  $  #  /
    ''')
    provjeri(M21b, lambda w: w.count('0') == w.count('1') and '10' not in w)


if 33 in tests:  # page 115 example 2.16
    M22 = PotisniAutomat.iz_tablice('''
        q1 / / q2 $
        q2 a / q2 a
        q2 / / q3 /
        q2 / / q5 /
        q3 b a q3 /
        q3 / $ q4 /
        q4 c / q4 / #
        q5 b / q5 /
        q5 / / q6 /
        q6 c a q6 /
        q6 / $ #  /
    ''')
    M22.crtaj()  # page 115 figure 2.17
    provjeri(M22, lambda w: w.count('a') in {w.count('b'), w.count('c')} and
         'ba' not in w and 'cb' not in w and 'ca' not in w)


if 34 in tests:  # page 116 example 2.18
    M23 = PotisniAutomat.iz_tablice('''
        q1 / / q2 $
        q2 0 / q2 0
        q2 1 / q2 1
        q2 / / q3 /
        q3 0 0 q3 /
        q3 1 1 q3 /
        q3 / $ #  /
    ''')
    M23.crtaj()  # page 116 figure 2.19
    provjeri(M23, lambda w: w == w[::-1] and djeljiv(len(w), 2))


if 35 in tests:  # page 120 example 2.25
    P1 = PotisniAutomat.iz_tablice('''
        qstart / / p1    $
        p1     / / qloop S
        qloop  / S a1    b
        a1     / / a2    T
        a2     / / qloop a
        qloop  / T b1    a
        b1     / / qloop T
        qloop  / S qloop b
        qloop  / T qloop /
        qloop  a a qloop /
        qloop  b b qloop /
        qloop  / $ #     /    ''')  # može beskonačno računati
    P1m = PotisniAutomat.iz_tablice('''
        qstart / / p1    $
        p1     / / qloop S
        qloop  / S a1    b
        a1     / / a2    T
        a2     / / qloop a
        qloop  / T b1    T
        b1     / / qloop a
        qloop  / S qloop b
        qloop  / T qloop /
        qloop  a a qloop /
        qloop  b b qloop /
        qloop  / $ #     /    ''')  # uvijek konačno računa
    provjeri(P1m, lambda w: w == 'a' * (len(w) - 1) + 'b')


if 41 in tests:  # page 102
    G1 = BeskontekstnaGramatika.iz_strelica('''
        A -> 0 A 1
        A -> B
        B -> #
    ''')
    assert G1.varijable == {'A', 'B'} and G1.početna == 'A'
    assert G1.abeceda == {'0', '1', '#'} and len(G1.pravila) == 3
    assert G1.validan('A 0A1 00A11 000A111 000B111 000#111'.split())


if 42 in tests:  # page 103
    G2 = BeskontekstnaGramatika.iz_strelica('''
        <SENTENCE> -> <NOUN-PHRASE> _ <VERB-PHRASE>
        <NOUN-PHRASE> -> <CMPLX-NOUN> | <CMPLX-NOUN> _ <PREP-PHRASE>
        <VERB-PHRASE> -> <CMPLX-VERB> | <CMPLX-VERB> _ <PREP-PHRASE>
        <PREP-PHRASE> -> <PREP> _ <CMPLX-NOUN>
        <CMPLX-NOUN> -> <ARTICLE> _ <NOUN>
        <CMPLX-VERB> -> <VERB> | <VERB> _ <NOUN-PHRASE>
        <ARTICLE> -> a | t h e
        <NOUN> -> b o y | g i r l | f l o w e r
        <VERB> -> t o u c h e s | l i k e s | s e e s
        <PREP> -> w i t h  ''')
    assert len(G2.varijable) == 10
    G2.abeceda |= set(string.ascii_lowercase + '_')
    assert len(G2.abeceda) == 27
    assert len(G2.pravila) == 18
    assert G2.CYK('a_boy_sees')
    assert G2.CYK('the_boy_sees_a_flower')
    assert G2.CYK('a_girl_with_a_flower_likes_the_boy')
    assert G2.CYK('the_girl_touches_the_boy_with_the_flower')
    assert G2.validan([linija.split() for linija in [
        '<SENTENCE>',
        '<NOUN-PHRASE> _ <VERB-PHRASE>',
        '<CMPLX-NOUN> _ <VERB-PHRASE>',
        '<ARTICLE> _ <NOUN> _ <VERB-PHRASE>',
        'a _ <NOUN> _ <VERB-PHRASE>',
        'a _ b o y _ <VERB-PHRASE>',
        'a _ b o y _ <CMPLX-VERB>',
        'a _ b o y _ <VERB>',
        'a _ b o y _ s e e s',
    ]])  # page 104


if 43 in tests:  # page 105 example 2.3
    G3 = BeskontekstnaGramatika.iz_strelica('S -> a S b | S S | ε')
    G3k = BeskontekstnaGramatika.iz_komponenti(
        {'S'}, {'a', 'b'}, {'SaSb', 'SSS', 'S'}, 'S')
    G3z = BeskontekstnaGramatika.iz_strelica('S -> ( S ) | S S | ε')
    for riječ in 'abab', 'aaabbb', 'aababb':
        assert G3k.CYK(riječ)

    def G3_spec(riječ):
        brojač = 0
        for znak in riječ:
            if znak == '(': brojač += 1
            elif znak == ')': brojač -= 1
            else: return False
            if brojač < 0: return False
        return brojač == 0
    provjeri(G3z, G3_spec)


if 44 in tests:  # page 105 example 2.4
    G4 = BeskontekstnaGramatika.iz_strelica('''
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | a
    ''')
    assert G4.CYK('a+a*a') and G4.CYK('(a+a)*a')
    assert G4.validan('E E+T T+T F+T a+T a+T*F a+F*F a+a*F a+a*a'.split())
    assert G4.validan('''E T T*F T*a F*a (E)*a (E+T)*a
                        (T+T)*a (T+F)*a (F+F)*a (a+F)*a (a+a)*a'''.split())


if 45 in tests:  # page 107
    G5 = BeskontekstnaGramatika.iz_strelica('E -> E + E | E * E | ( E ) | a')
    assert G5.validan('E E*E E+E*E a+E*E a+a*E a+a*a'.split())
    assert G5.validan('E E+E E+E*E a+E*E a+a*E a+a*a'.split())


if 46 in tests:  # https://goo.gl/FmMNY7
    GwpDEL = BeskontekstnaGramatika.iz_strelica('''
        S0 -> A b B | C
        B -> A A | A C
        C -> b | c
        A -> a | ε ''')
    GwpDEL.faza_DEL()
    strelice(GwpDEL)


if 47 in tests:  # https://en.wikipedia.org/wiki/Chomsky_normal_form#Example
    Gwp = BeskontekstnaGramatika.iz_strelica('''
        Expr -> Term | Expr AddOp Term | AddOp Term
        Term -> Factor | Term MulOp Factor
        Factor -> Primary | Factor ^ Primary
        Primary -> number | variable | ( Expr )
        AddOp -> + | −
        MulOp -> * | / ''')
    GwpČ = Gwp.ChNF()
    assert len(GwpČ.pravila) == 37


if 48 in tests:  # page 110 example 2.10
    G6 = BeskontekstnaGramatika.iz_strelica('''
        S -> A S A | a B
        A -> B | S
        B -> b | ε   ''')
    strelice(G6.ChNF())


if 49 in tests:  # page 106
    G01 = BeskontekstnaGramatika.iz_strelica('S -> 0 S 1 | ε')
    G10 = BeskontekstnaGramatika.iz_strelica('S -> 1 S 0 | ε')
    strelice(G01.unija(G10))
    strelice(G1.zvijezda())
