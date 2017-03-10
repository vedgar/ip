from util import *


class KonačniAutomat(types.SimpleNamespace):
    @classmethod
    def iz_komponenti(klasa, stanja, abeceda, prijelaz, početno, završna):
        assert abeceda  # nije prazna
        assert početno in stanja
        assert završna <= stanja
        assert funkcija(prijelaz, Kartezijev_produkt(stanja, abeceda), stanja)
        return klasa(**vars())

    @classmethod
    def iz_tablice(klasa, tablica):
        return klasa.iz_komponenti(*parsiraj_tablicu_KA(tablica))

    @property
    def komponente(M):
        return M.stanja, M.abeceda, M.prijelaz, M.početno, M.završna

    def prihvaća(automat, ulaz):
        stanje = automat.početno
        for znak in ulaz:
            stanje = automat.prijelaz[stanje, znak]
        return stanje in automat.završna

    def izračunavanje(automat, ulaz):
        stanje = automat.početno
        yield stanje
        for znak in ulaz:
            stanje = automat.prijelaz[stanje, znak]
            yield stanje

    def prirodni(automat):
        Q, Σ, δ, q0, F = automat.komponente
        rječnik = {q:i for i, q in enumerate(Q, 1)}
        QN = set(rječnik.values())
        δN = {(rječnik[polazno], znak): rječnik[dolazno]
            for (polazno, znak), dolazno in δ.items()}
        q0N = rječnik[q0]
        FN = {rječnik[završno] for završno in F}
        return KonačniAutomat.iz_komponenti(QN, Σ, δN, q0N, FN)

    def crtaj(automat):
        NedeterminističkiKonačniAutomat.iz_konačnog_automata(automat).crtaj()

    def unija(M1, M2):
        assert M1.abeceda == M2.abeceda
        Q1, Σ, δ1, q1, F1 = M1.komponente
        Q2, Σ, δ2, q2, F2 = M2.komponente
        Q = Kartezijev_produkt(Q1, Q2)
        δ = {((r1,r2), α): (δ1[r1,α], δ2[r2,α]) for r1,r2 in Q for α in Σ}
        F = Kartezijev_produkt(Q1, F2) | Kartezijev_produkt(F1, Q2)
        return KonačniAutomat.iz_komponenti(Q, Σ, δ, (q1,q2), F)

    def presjek(M1, M2):
        M = M1.unija(M2)
        M.završna = Kartezijev_produkt(M1.završna, M2.završna)
        return M

    def komplement(M):
        Q, Σ, δ, q0, F = M.komponente
        return KonačniAutomat.iz_komponenti(Q, Σ, δ, q0, Q - F)

    def razlika(M1, M2):
        return M1.presjek(M2.komplement())

    def simetrična_razlika(M1, M2):
        return M1.razlika(M2).unija(M2.razlika(M1))

    def optimizirana_simetrična_razlika(M1, M2):
        M = M1.razlika(M2)
        M.završna |= Kartezijev_produkt(M1.stanja - M1.završna, M2.završna)
        return M


def dohvatljiva(δ, moguća, α):
    return unija_familije(δ[q, α] for q in moguća)

def ε_proširenje(Σ):
    return disjunktna_unija(Σ, {ε})

def ε_ljuska(δ, stanja):
    while True:
        nova_stanja = dohvatljiva(δ, stanja, ε) | stanja
        if nova_stanja == stanja:
            return nova_stanja
        stanja = nova_stanja


class NedeterminističkiKonačniAutomat(types.SimpleNamespace):
    @classmethod
    def iz_komponenti(klasa, stanja, abeceda, prijelaz, početno, završna):
        assert abeceda
        assert početno in stanja
        assert završna <= stanja
        assert relacija(prijelaz, stanja, ε_proširenje(abeceda), stanja)
        return klasa(**vars())

    @classmethod
    def iz_funkcije(klasa, stanja, abeceda, f_prijelaza, početno, završna):
        prijelaz = relacija_iz_funkcije(f_prijelaza)
        return klasa.iz_komponenti(stanja, abeceda, prijelaz, početno, završna)

    @classmethod
    def iz_konačnog_automata(klasa, konačni_automat):
        Q, Σ, δ, q0, F = konačni_automat.komponente
        Δ = {(q, α, δ[q, α]) for q in Q for α in Σ}
        return klasa.iz_komponenti(Q, Σ, Δ, q0, F)

    @classmethod
    def iz_tablice(klasa, tablica):
        return klasa.iz_komponenti(*parsiraj_tablicu_NKA(tablica))

    @property
    def komponente(M):
        return M.stanja, M.abeceda, M.prijelaz, M.početno, M.završna

    @property
    def abeceda_ε(automat):
        return ε_proširenje(automat.abeceda)

    @property
    def funkcija_prijelaza(automat):
        return funkcija_iz_relacije(automat.prijelaz,
            automat.stanja, ε_proširenje(automat.abeceda))

    def prihvaća(automat, ulaz):
        δ = automat.funkcija_prijelaza
        moguća = ε_ljuska(δ, {automat.početno})
        for znak in ulaz: moguća = ε_ljuska(δ, dohvatljiva(δ, moguća, znak))
        return not moguća.isdisjoint(automat.završna)

    def crtaj(automat):
        print('www.webgraphviz.com | sandbox.kidstrythisathome.com/erdos')
        print(DOT_NKA(automat))

    def izračunavanje(automat, ulaz):
        return automat.optimizirana_partitivna_konstrukcija().izračunavanje(ulaz)

    def partitivna_konstrukcija(nka):
        Q, Σ, Δ, q0, F = nka.komponente
        δ = nka.funkcija_prijelaza
        PQ = partitivni_skup(Q)
        δ_KA = {(S,α): ε_ljuska(δ, dohvatljiva(δ, S, α)) for S in PQ for α in Σ}
        F_KA = {S for S in PQ if S & F}
        q0_KA = ε_ljuska(δ, {q0})
        return KonačniAutomat.iz_komponenti(PQ, Σ, δ_KA, q0_KA, F_KA)

    def optimizirana_partitivna_konstrukcija(nka):
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
        Q, Σ, Δ, q0, F = nka.komponente
        Ql = {označi1(q, l) for q in Q}
        Δl = {(označi1(p, l), α, označi1(q, l)) for p, α, q in Δ}
        q0l = označi1(q0, l)
        Fl = {označi1(q, l) for q in F}
        return NedeterminističkiKonačniAutomat.iz_komponenti(Ql, Σ, Δl, q0l, Fl)

    def unija(N1, N2):
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
        Q, Σ, Δ, q0, F = N.komponente
        Δp = Δ | {(p, ε, q0) for p in F}
        return NedeterminističkiKonačniAutomat.iz_komponenti(Q, Σ, Δp, q0, F)

    def zvijezda(N):
        Q, Σ, Δ, q0, F = N.plus().komponente
        start = novo('start', Q)
        return NedeterminističkiKonačniAutomat.iz_komponenti(
            Q | {start}, Σ, Δ | {(start, ε, q0)}, start, F | {start})

    def reverz(N):
        Q, Σ, Δ, q0, F = N.komponente
        kraj = novo('qz', Q)
        Δ_ᴙ = {(q, α, p) for p, α, q in Δ} | {(kraj, ε, z) for z in F}
        return NedeterminističkiKonačniAutomat.iz_komponenti(
            Q | {kraj}, Σ, Δ_ᴙ, kraj, {q0})
