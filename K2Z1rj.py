from KA import *
from NKA import *

k_presjek = Kartezijeva_konstrukcija_presjek
k_unija = Kartezijeva_konstrukcija_unija

def k_komplement(M: KonačniAutomat) -> KonačniAutomat:
    """KonačniAutomat koji prepoznaje komplement od L(M)
    (u odnosu na Kleenejevu zvijezdu od M.abeceda)."""
    Q, Σ, δ, q0, F = petorka(M)
    return KonačniAutomat.definicija(Q, Σ, δ, q0, Q-F)

def k_razlika(M1, M2):
    return k_presjek(M1, k_komplement(M2))

def k_simetrična_razlika(M1: KonačniAutomat,
                         M2: KonačniAutomat) -> KonačniAutomat:
    """KonačniAutomat koji prepoznaje simetričnu razliku od L(M1) i L(M2).
    Smijete pretpostaviti M1.abeceda == M2.abeceda."""
    M3 = k_razlika(M1, M2)
    M4 = k_razlika(M2, M1)
    return k_unija(M3, M4)

def optimizirana_k_simetrična_razlika(M1: KonačniAutomat,
                                      M2: KonačniAutomat) -> KonačniAutomat:
    M3 = k_unija(M1, M2)
    M3.završna = (Kartezijev_produkt(M1.završna, M2.stanja - M2.završna) |
                  Kartezijev_produkt(M1.stanja - M1.završna, M2.završna))
    return M3

def prazan_jezik_KA(M: KonačniAutomat) -> bool:
    """Vraća prepoznaje li M prazan jezik."""
    N = NedeterminističkiKonačniAutomat.iz_konačnog_automata(M)
    O = optimizirana_partitivna_konstrukcija(N)
    return not O.završna

def jednaki_jezici_KA(M1: KonačniAutomat, M2: KonačniAutomat) -> bool:
    """Vraća prepoznaju li M1 i M2 isti jezik.
    Smijete pretpostaviti M1.abeceda == M2.abeceda."""
    return prazan_jezik_KA(k_simetrična_razlika(M1, M2))

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

    assert not prazan_jezik_KA(E2)
    assert prazan_jezik_KA(EE)
    assert jednaki_jezici_KA(E1, prirodni(E1))
    assert not jednaki_jezici_KA(E1, E2)
