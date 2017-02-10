from KA import *
from NKA import *


k_presjek = Kartezijeva_konstrukcija_presjek
k_unija = Kartezijeva_konstrukcija_unija


def k_komplement(M: KonačniAutomat) -> KonačniAutomat:
    """KonačniAutomat koji prepoznaje komplement od L(M)
    (u odnosu na Kleenejevu zvijezdu od M.abeceda)."""
    raise NotImplementedError('Ovdje treba napisati rješenje.')


def k_simetrična_razlika(M1:KonačniAutomat, M2:KonačniAutomat)->KonačniAutomat:
    """KonačniAutomat koji prepoznaje simetričnu razliku od L(M1) i L(M2).
    Smijete pretpostaviti M1.abeceda == M2.abeceda."""
    raise NotImplementedError('Ovdje treba napisati rješenje.')


def prazan_jezik_KA(M: KonačniAutomat) -> bool:
    """Vraća prepoznaje li M prazan jezik."""
    raise NotImplementedError('Ovdje treba napisati rješenje.')


def jednaki_jezici_KA(M1: KonačniAutomat, M2: KonačniAutomat) -> bool:
    """Vraća prepoznaju li M1 i M2 isti jezik.
    Smijete pretpostaviti M1.abeceda == M2.abeceda."""
    raise NotImplementedError('Ovdje treba napisati rješenje.')


if __name__ == '__main__':
    E1 = KonačniAutomat.iz_tablice('''
          0     1
    qeven qeven qodd
    qodd  qodd  qeven #
    ''')  # page 43 figure 1.20

    E2 = KonačniAutomat.iz_tablice('''
         0    1
    q    q0   q
    q0   q00  q
    q00  q00  q001
    q001 q001 q001 #
    ''')  # page 44 example 1.21 figure 1.22

    EE = KonačniAutomat.iz_tablice('''
        0   1
    q0  q2  q2
    q1  q1  q0  #
    q2  q0  q2
    ''')

    k_komplement(E2).provjeri(lambda ulaz: not E2.prihvaća(ulaz))
    
    Es = k_simetrična_razlika(E1, E2)
    Es.provjeri(lambda ulaz: E1.prihvaća(ulaz) ^ E2.prihvaća(ulaz), 10000)

    assert prazan_jezik_KA(EE)
    assert not prazan_jezik_KA(E2)
    assert jednaki_jezici_KA(E1, prirodni(E1))
    assert not jednaki_jezici_KA(E1, E2)
