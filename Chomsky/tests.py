from KA import *
from RI import *
from PA import *
from BKG import *
from TS import *


tests = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
tests |= {21, 22, 23, 24, 25, 26, 27, 28, 29, 30}
tests |= {31, 32, 33, 34, 35, 36, 37, 38, 39, 40}
tests |= {41, 42, 43, 44, 45, 46, 47, 48, 49, 50}
tests |= {51, 52, 53, 54}
tests |= {90}


def test(i):
    if i in tests:
        print('#' * 30, 'Test', i, '#' * 30)
        return True


if test(1):  # page 34 figure 1.4  # page 36 figure 1.6
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


if test(2):  # page 37 example 1.7 figure 1.8
    M2 = KonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q2
        q2 q1 q2 # ''')
    print(*M2.izračunavanje('1101'), *M2.izračunavanje('110'))
    provjeri(M2, lambda ulaz: ulaz.endswith('1'))


if test(3):  # page 38 example 1.9 figure 1.10
    M3 = KonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q2 #
        q2 q1 q2   ''')
    provjeri(M3, lambda ulaz: ulaz == ε or ulaz.endswith('0'))


if test(4):  # page 38 example 1.11 figure 1.12
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


if test(5):  # page 39 example 1.13 figure 1.14
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


if test(6):  # page 40 example 1.15
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


if test(7):  # page 43 figure 1.20
    E1 = KonačniAutomat.iz_tablice('''
              0     1
        qeven qeven qodd
        qodd  qodd  qeven # ''')
    provjeri(E1, lambda ulaz: ulaz.count('1') % 2)


if test(8):  # page 44 example 1.21 figure 1.22
    E2 = KonačniAutomat.iz_tablice('''
             0    1
        q    q0   q
        q0   q00  q
        q00  q00  q001
        q001 q001 q001 # ''')
    provjeri(E2, lambda ulaz: '001' in ulaz)


if test(9):
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


if test(10):  # page 48 figure 1.27
    N1 = NedeterminističniKonačniAutomat.iz_komponenti({'q1', 'q2', 'q3', 'q4'},
        {'0', '1'}, {('q1', '0', 'q1'), ('q1', '1', 'q1'), ('q1', '1', 'q2'),
                     ('q2', '0', 'q3'), ('q2', ε, 'q3'), ('q3', '1', 'q4'),
                     ('q4', '0', 'q4'), ('q4', '1', 'q4')}, 'q1', {'q4'})
    assert N1 == NedeterminističniKonačniAutomat.iz_tablice('''
           0  1
        q1 q1 q1/q2
        q2 q3 /     q3
        q3 /  q4
        q4 q4 q4       #''')  # page 54 example 1.38

    provjeri(N1, lambda ulaz: '101' in ulaz or '11' in ulaz)
    print(*N1.izračunavanje('010110'))  # page 49 figure 1.29
    print(*N1.izračunavanje('010'))

    N1b = NedeterminističniKonačniAutomat.iz_komponenti({1,2,3,4}, {0,1},
    {(1,0,1),(1,1,1),(1,1,2),(2,0,3),(2,ε,3),(3,1,4),(4,0,4),(4,1,4)}, 1, {4})
    D1b = N1b.optimizirana_partitivna_konstrukcija()


if test(11):  # page 51 example 1.30 figure 1.31
    N2 = NedeterminističniKonačniAutomat.iz_tablice('''
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


if test(12):  # page 52 example 1.33
    N3 = NedeterminističniKonačniAutomat.iz_tablice('''
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


if test(13):  # page 52 example 1.35 figure 1.36
    N4 = NedeterminističniKonačniAutomat.iz_tablice('''
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


if test(14):
    N1 = NedeterminističniKonačniAutomat.iz_komponenti(
        {0, 1}, {'a'}, {(0, 'a', 1), (1, 'a', 0)}, 0, {0})
    N2 = NedeterminističniKonačniAutomat.iz_komponenti(
        {0, 1, 2}, {'a'}, {(0, 'a', 1), (1, 'a', 2), (2, 'a', 0)}, 0, {0})
    N1u2 = N1.unija(N2)
    N1o2 = N1.konkatenacija(N2)
    N1o2.crtaj()


if test(21):
    binarni = nula | jedan * (nula|jedan).z
    print(binarni.početak())
    binarni.NKA().crtaj()


if test(22):
    primjer1 = (nula | jedan) * nula.z  # page 63
    print(primjer1.početak())
    provjeri(primjer1, lambda ulaz: ulaz != ε and '1' not in ulaz[1:])


if test(23):  # page 64 example 1.51
    sve = (nula|jedan).z
    print(sve.početak())
    provjeri(sve, lambda ulaz: True)
    provjeri(nula*sve | sve*jedan,
             lambda ulaz: ulaz.startswith('0') or ulaz.endswith('1'))


if test(24):  # page 65 example 1.53
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
    r11 = jedan.z * prazni
    print(r11.prazan())
    r12 = prazni.z
    print(r12.prazan(), r12.trivijalan())


if test(25):  # page 68 example 1.56
    e1 = (a*b|a).z
    e1.NKA().crtaj()


if test(26):  # page 69 example 1.58
    e2 = (a|b).z * a * b * a
    e2.NKA().crtaj()
    provjeri(e2, lambda ulaz: ulaz.endswith('aba'))


if test(27):  # page 76 figure 1.69
    p = (a**2|b).z
    t = (b*a | a) * p
    r = (a*p*a).u * b * (t|b**2).z * t.u | a * p
    print(r)


if test(28):  # page 88 excercise 1.28
    ra = a * (a*b*b).z | b
    rb = a.p | (a*b).p
    rc = (a | b.p) * a.p * b.p
    ra.NKA().crtaj()
    rb.NKA().crtaj()
    rc.NKA().crtaj()


if test(31):  # page 114 example 2.14
    Ֆ = '$'

    M21 = PotisniAutomat.iz_komponenti({1, 2, 3, 4}, {0, 1}, {0, Ֆ},
        {(1,ε,ε,2,Ֆ), (2,0,ε,2,0), (2,1,0,3,ε), (3,1,0,3,ε), (3,ε,Ֆ,4,ε)},
        1, {1, 4})
    ispiši(M21)
    M21.crtaj()  # page 115 figure 2.15
    print(M21.prihvaća((0, 0, 1, 1)), M21.prihvaća((0, 1, 0, 1)))


if test(32):  # page 114 example 2.14
    M21b = PotisniAutomat.iz_tablice('''
        q1 /  /  q2 $  #
        q2 0  /  q2 0
        q2 1  0  q3 /
        q3 1  0  q3 /
        q3 /  $  #  /
    ''')
    provjeri(M21b, lambda w: w.count('0') == w.count('1') and '10' not in w)


if test(33):  # page 115 example 2.16
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


if test(34):  # page 116 example 2.18
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


if test(35):  # page 120 example 2.25
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


if test(41):  # page 102
    G1 = BeskontekstnaGramatika.iz_strelica('''
        A -> 0 A 1
        A -> B
        B -> #
    ''')
    assert G1.varijable == {'A', 'B'} and G1.početna == 'A'
    assert G1.abeceda == {'0', '1', '#'} and len(G1.pravila) == 3
    assert G1.validan('A 0A1 00A11 000A111 000B111 000#111'.split())


if test(42):  # page 103
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


if test(43):  # page 105 example 2.3
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


if test(44):  # page 105 example 2.4
    G4 = BeskontekstnaGramatika.iz_strelica('''
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | a
    ''')
    assert G4.CYK('a+a*a') and G4.CYK('(a+a)*a')
    assert G4.validan('E E+T T+T F+T a+T a+T*F a+F*F a+a*F a+a*a'.split())
    assert G4.validan('''E T T*F T*a F*a (E)*a (E+T)*a
                        (T+T)*a (T+F)*a (F+F)*a (a+F)*a (a+a)*a'''.split())


if test(45):  # page 107
    G5 = BeskontekstnaGramatika.iz_strelica('E -> E + E | E * E | ( E ) | a')
    assert G5.validan('E E*E E+E*E a+E*E a+a*E a+a*a'.split())
    assert G5.validan('E E+E E+E*E a+E*E a+a*E a+a*a'.split())


if test(46):  # https://goo.gl/FmMNY7
    GwpDEL = BeskontekstnaGramatika.iz_strelica('''
        S0 -> A b B | C
        B -> A A | A C
        C -> b | c
        A -> a | ε ''')
    GwpDEL.faza_DEL()
    strelice(GwpDEL)


if test(47):  # https://en.wikipedia.org/wiki/Chomsky_normal_form#Example
    Gwp = BeskontekstnaGramatika.iz_strelica('''
        Expr -> Term | Expr AddOp Term | AddOp Term
        Term -> Factor | Term MulOp Factor
        Factor -> Primary | Factor ^ Primary
        Primary -> number | variable | ( Expr )
        AddOp -> + | −
        MulOp -> * | / ''')
    GwpČ = Gwp.ChNF()
    assert len(GwpČ.pravila) == 37


if test(48):  # page 110 example 2.10
    G6 = BeskontekstnaGramatika.iz_strelica('''
        S -> A S A | a B
        A -> B | S
        B -> b | ε   ''')
    strelice(G6.ChNF())


if test(49):  # page 106
    G01 = BeskontekstnaGramatika.iz_strelica('S -> 0 S 1 | ε')
    G10 = BeskontekstnaGramatika.iz_strelica('S -> 1 S 0 | ε')
    strelice(G01.unija(G10))
    strelice(G1.zvijezda())


if test(50):  # 2019-dz1-Z2a
    g = BeskontekstnaGramatika.iz_strelica('''
        S->S S|A B
        A->B a|ε
        B->B b A a|c A|b
    ''')
    c = g.ChNF()
    strelice(g)
    strelice(c)


if test(51):  # page 171 example 3.7
    ts = TuringovStroj.iz_tablice('''0    _   x
                                  q1 _+q2 !   !
                                  q2 x+q3 .   +
                                  q3 +q4  -q5 +
                                  q4 x+q3 !   +
                                  q5 -    +q2 - ''')
    for n in range(9): print(n, ts.prihvaća('0' * n), end='  ', sep=':')
    print()
    for konf in ts.izračunavanje('0000'): prikaz(*konf)


if test(52):  # page 173 example 3.9
    ts = TuringovStroj.iz_tablice('''0    1    #    _ x
                                  q1 x+q2 x+q3 +q8  ! !
                                  q2 +    +    +q4  ! !
                                  q3 +    +    +q5  ! !
                                  q4 x-q6 !    !    ! +
                                  q5 !    x-q6 !    ! +
                                  q6 -    -    -q7  ! -
                                  q7 -    -    !    ! +q1
                                  q8 !    !    !    . +    ''')
    print(ts)
    for konf in ts.izračunavanje('#'.join(['011000'] * 2)): prikaz(*konf)


if test(53):  # Komputonomikon, Primjer 4.6
    tsh = TuringovStroj.iz_tablice('''a   b   _  c   d
                                    A c+B d+B .  !   !
                                    B +   +   -C !   !
                                    C _-D _-D !  !   !
                                    D -   -   !  a+A b+A''')
    for korak, konf in enumerate(tsh.izračunavanje('aba')):
        prikaz(*konf)
        if korak > 9: break
    print()
    for konf in tsh.izračunavanje('abaa'): prikaz(*konf)
    print(tsh.rezultat('abaa'))
    print()
    for konf in tsh.izračunavanje('aababa'): prikaz(*konf)
    print(tsh.rezultat('aababa'))
    print('\n', tsh.prihvaća('aabbaba'), tsh.rezultat('aabbaba'))


if test(54):  # Komputonomikon, Lema 4.16
    def tsid(Σ):
        _ = novo('_', Σ)
        Γ = Σ | {_}
        δ = {(0, α): (1, α, 1) for α in Γ}
        return TuringovStroj.iz_komponenti({0, 1}, Σ, Γ, _, δ, 0, 1)

    print(tsid(set('abc_')).rezultat('a_c_a_b_'))


if test(55):
    ...


if test(90):  # 2019-k1-z3
    zadatak = jedan.p * nula * jedan.z | jedan.u * nula.z * jedan.p
    naivno = zadatak.KA()
    službeno_rješenje = '''     0   1
                            S   /   J/N  N
                            J   Z   J
                            N   N   Z
                            Z   /   Z    #   '''
    službeni_NKA = NedeterminističniKonačniAutomat.iz_tablice(službeno_rješenje)
    službeni_KA = službeni_NKA.optimizirana_partitivna_konstrukcija()
    rješenje = '''       0     1
                    q0   q2    q3/q1
                    q1   q3    q1
                    q2   q2    q3
                    q3   q2    q3    #
    '''
    rješenje = NedeterminističniKonačniAutomat.iz_tablice(rješenje)
    print(*rješenje.izračunavanje('0101'))
    deterministični = rješenje.optimizirana_partitivna_konstrukcija()
    razlika = deterministični.optimizirana_simetrična_razlika(službeni_KA)
    nedet = NedeterminističniKonačniAutomat.iz_konačnog_automata(razlika)
    je_li_prazan = nedet.optimizirana_partitivna_konstrukcija()
    je_li_prazan.prirodni().crtaj()
    print(je_li_prazan.završna)
