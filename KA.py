from util import *


class KonačniAutomat(types.SimpleNamespace):
    """Automat koji prepoznaje regularni jezik."""

    @classmethod
    def iz_komponenti(klasa, stanja, abeceda, prijelaz, početno, završna):
        """Sipser page 35 definition 1.5 - konstrukcija iz petorke."""
        assert abeceda  # nije prazna
        assert početno in stanja
        assert završna <= stanja
        assert funkcija(prijelaz, Kartezijev_produkt(stanja, abeceda), stanja)
        return klasa(**vars())

    @classmethod
    def iz_tablice(klasa, tablica):
        """Parsiranje tabličnog zapisa konačnog automata (Sipser page 36).
        Pogledati funkciju util.parsiraj_tablicu_KA za detalje."""
        return klasa.iz_komponenti(*parsiraj_tablicu_KA(tablica))

    @property
    def komponente(M):
        """Sipser page 35 definition 1.5 - rastav u petorku."""
        return M.stanja, M.abeceda, M.prijelaz, M.početno, M.završna

    def prihvaća(automat, ulaz):
        """Prihvaća li konačni automat zadani ulaz?"""
        stanje = automat.početno
        for znak in ulaz:
            stanje = automat.prijelaz[stanje, znak]
        return stanje in automat.završna

    def izračunavanje(automat, ulaz):
        """Stanja kroz koja automat prolazi čitajući ulaz (Sipser page 40)."""
        stanje = automat.početno
        yield stanje
        for znak in ulaz:
            stanje = automat.prijelaz[stanje, znak]
            yield stanje

    def prirodni(automat):
        """Zamjenjuje stanja prirodnim brojevima, radi preglednosti."""
        Q, Σ, δ, q0, F = automat.komponente
        rječnik = {q:i for i, q in enumerate(Q, 1)}
        QN = set(rječnik.values())
        δN = {(rječnik[polazno], znak): rječnik[dolazno]
            for (polazno, znak), dolazno in δ.items()}
        q0N = rječnik[q0]
        FN = {rječnik[završno] for završno in F}
        return KonačniAutomat.iz_komponenti(QN, Σ, δN, q0N, FN)

    def crtaj(automat):
        """Ispisuje na ekran dijagram automata u DOT formatu.
        Dobiveni string može se kopirati u sandbox.kidstrythisathome.com/erdos
        ili u www.webgraphviz.com."""
        NedeterminističkiKonačniAutomat.iz_konačnog_automata(automat).crtaj()

    def unija(M1, M2):
        """Konačni automat za L(M1)∪L(M2)."""
        assert M1.abeceda == M2.abeceda
        Q1, Σ, δ1, q1, F1 = M1.komponente
        Q2, Σ, δ2, q2, F2 = M2.komponente
        Q = Kartezijev_produkt(Q1, Q2)
        δ = {((r1,r2), α): (δ1[r1,α], δ2[r2,α]) for r1,r2 in Q for α in Σ}
        F = Kartezijev_produkt(Q1, F2) | Kartezijev_produkt(F1, Q2)
        return KonačniAutomat.iz_komponenti(Q, Σ, δ, (q1,q2), F)

    def presjek(M1, M2):
        """Konačni automat za L(M1)∩L(M2)."""
        M = M1.unija(M2)
        M.završna = Kartezijev_produkt(M1.završna, M2.završna)
        return M

    def komplement(M):
        """Konačni automat za (M.abeceda)*\L(M)."""
        Q, Σ, δ, q0, F = M.komponente
        return KonačniAutomat.iz_komponenti(Q, Σ, δ, q0, Q - F)

    def razlika(M1, M2):
        """Konačni automat za L(M1)\L(M2)."""
        return M1.presjek(M2.komplement())

    def simetrična_razlika(M1, M2):
        """Konačni automat za L(M1)△L(M2)."""
        return M1.razlika(M2).unija(M2.razlika(M1))

    def optimizirana_simetrična_razlika(M1, M2):
        """Konačni automat za L(M1)△L(M2), s |M1.stanja|·|M2.stanja| stanja."""
        M = M1.razlika(M2)
        M.završna |= Kartezijev_produkt(M1.stanja - M1.završna, M2.završna)
        return M


def dohvatljiva(δ, S, α):
    """Stanja do kojih je moguće doći iz stanja iz S čitanjem znaka α."""
    return unija_familije(δ[q, α] for q in S)

def ε_ljuska(δ, S):
    """Stanja do kojih je moguće doći iz stanja iz S bez čitanja znaka."""
    while True:
        S_novi = dohvatljiva(δ, S, ε) | S
        if S_novi == S:
            return S_novi
        S = S_novi


class NedeterminističkiKonačniAutomat(types.SimpleNamespace):
    """Nedeterministički automat koji prepoznaje regularni jezik."""
    
    @classmethod
    def iz_komponenti(klasa, stanja, abeceda, prijelaz, početno, završna):
        """Relacijska definicija: Δ⊆Q×(Σ∪{ε})×Q"""
        assert abeceda  # nije prazna
        assert početno in stanja
        assert završna <= stanja
        assert relacija(prijelaz, stanja, ε_proširenje(abeceda), stanja)
        return klasa(**vars())

    @classmethod
    def iz_funkcije(klasa, stanja, abeceda, f_prijelaza, početno, završna):
        """Funkcijska definicija: δ:Q×(Σ∪{ε})→℘(Q) (Sipser page 53 def.1.37)"""
        prijelaz = relacija_iz_funkcije(f_prijelaza)
        return klasa.iz_komponenti(stanja, abeceda, prijelaz, početno, završna)

    @classmethod
    def iz_konačnog_automata(klasa, konačni_automat):
        """Pretvorba iz determinističkog KA u nedeterministički."""
        Q, Σ, δ, q0, F = konačni_automat.komponente
        Δ = {(q, α, δ[q, α]) for q in Q for α in Σ}
        return klasa.iz_komponenti(Q, Σ, Δ, q0, F)

    @classmethod
    def iz_tablice(klasa, tablica):
        """Parsiranje tabličnog zapisa nedeterminističkog KA (Sipser page 54).
        Pogledati funkciju util.parsiraj_tablicu_NKA za detalje."""
        return klasa.iz_komponenti(*parsiraj_tablicu_NKA(tablica))

    @property
    def komponente(M):
        """Relacijska definicija - rastav u petorku."""
        return M.stanja, M.abeceda, M.prijelaz, M.početno, M.završna

    @property
    def funkcija_prijelaza(automat):
        """Relacija prijelaza pretvorena u funkciju."""
        return funkcija_iz_relacije(automat.prijelaz,
            automat.stanja, ε_proširenje(automat.abeceda))

    def prihvaća(automat, ulaz):
        """Prihvaća li automat zadani ulaz?"""
        δ = automat.funkcija_prijelaza
        moguća = ε_ljuska(δ, {automat.početno})
        for znak in ulaz: moguća = ε_ljuska(δ, dohvatljiva(δ, moguća, znak))
        return not moguća.isdisjoint(automat.završna)

    def crtaj(automat):
        """Ispisuje na ekran dijagram automata u DOT formatu.
        Dobiveni string može se kopirati u sandbox.kidstrythisathome.com/erdos
        ili u www.webgraphviz.com."""
        from PA import PotisniAutomat
        print(DOT_PA(PotisniAutomat.
            iz_nedeterminističkog_konačnog_automata(automat)))

    def izračunavanje(nka, ulaz):
        """Generator niza skupova mogućih stanja kroz koja nedeterministički
        konačni automat prolazi čitajući zadani ulaz."""
        return nka.optimizirana_partitivna_konstrukcija().izračunavanje(ulaz)

    def partitivna_konstrukcija(nka):
        """Ekvivalentni KA zadanom NKA, s 2^|nka.stanja| stanja."""
        Q, Σ, Δ, q0, F = nka.komponente
        δ = nka.funkcija_prijelaza
        PQ = partitivni_skup(Q)
        δ_KA = {(S,α): ε_ljuska(δ, dohvatljiva(δ, S, α)) for S in PQ for α in Σ}
        F_KA = {S for S in PQ if S & F}
        q0_KA = ε_ljuska(δ, {q0})
        return KonačniAutomat.iz_komponenti(PQ, Σ, δ_KA, q0_KA, F_KA)

    def optimizirana_partitivna_konstrukcija(nka):
        """Ekvivalentni KA zadanom NKA, samo s dostižnim stanjima."""
        Q, Σ, Δ, q0, F = nka.komponente
        δ = nka.funkcija_prijelaza
        Q_KA = set()
        δ_KA = {}
        F_KA = set()
        q0_KA = ε_ljuska(δ, {q0})
        red = collections.deque([q0_KA])
        while red:
            stanje = red.popleft()
            if stanje not in Q_KA:
                for α in Σ:
                    novo_stanje = ε_ljuska(δ, dohvatljiva(δ, stanje, α))
                    δ_KA[stanje, α] = novo_stanje
                    red.append(novo_stanje)
                Q_KA.add(stanje)
                if not stanje.isdisjoint(F):
                    F_KA.add(stanje)
        return KonačniAutomat.iz_komponenti(Q_KA, Σ, δ_KA, q0_KA, F_KA)

    def označi(nka, l):
        """Označava stanja danog NKA dodatnom oznakom l, radi disjunktnosti."""
        Q, Σ, Δ, q0, F = nka.komponente
        Ql = {označi1(q, l) for q in Q}
        Δl = {(označi1(p, l), α, označi1(q, l)) for p, α, q in Δ}
        q0l = označi1(q0, l)
        Fl = {označi1(q, l) for q in F}
        return NedeterminističkiKonačniAutomat.iz_komponenti(Ql, Σ, Δl, q0l, Fl)

    def unija(N1, N2):
        """Nedeterministički konačni automat koji prepoznaje L(N1)∪L(N2)."""
        assert N1.abeceda == N2.abeceda
        if not N1.stanja.isdisjoint(N2.stanja):
            N1 = N1.označi(1)
            N2 = N2.označi(2)
        Q1, Σ, Δ1, q1, F1 = N1.komponente
        Q2, Σ, Δ2, q2, F2 = N2.komponente
        q0 = novo('q0', Q1 | Q2)
        Q = disjunktna_unija(Q1, Q2, {q0})
        F = disjunktna_unija(F1, F2)
        Δ = disjunktna_unija(Δ1, Δ2, {(q0, ε, q1), (q0, ε, q2)})
        return NedeterminističkiKonačniAutomat.iz_komponenti(Q, Σ, Δ, q0, F)

    def konkatenacija(N1, N2):
        """Nedeterministički konačni automat koji prepoznaje L(N1)L(N2)."""
        assert N1.abeceda == N2.abeceda
        if not N1.stanja.isdisjoint(N2.stanja):
            N1 = N1.označi(3)
            N2 = N2.označi(4)
        Q1, Σ, Δ1, q1, F1 = N1.komponente
        Q2, Σ, Δ2, q2, F2 = N2.komponente
        Q = disjunktna_unija(Q1, Q2)
        Δ = disjunktna_unija(Δ1, Δ2, {(p1, ε, q2) for p1 in F1})
        return NedeterminističkiKonačniAutomat.iz_komponenti(Q, Σ, Δ, q1, F2)

    def plus(N):
        """Nedeterministički konačni automat za Kleenejev plus od L(N)."""
        Q, Σ, Δ, q0, F = N.komponente
        Δp = Δ | {(p, ε, q0) for p in F}
        return NedeterminističkiKonačniAutomat.iz_komponenti(Q, Σ, Δp, q0, F)

    def zvijezda(N):
        """Nedeterministički konačni automat za Kleenejevu zvijezdu od L(N)."""
        Q, Σ, Δ, q0, F = N.plus().komponente
        start = novo('start', Q)
        return NedeterminističkiKonačniAutomat.iz_komponenti(
            Q | {start}, Σ, Δ | {(start, ε, q0)}, start, F | {start})
