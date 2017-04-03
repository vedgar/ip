from util import *


class BeskontekstnaGramatika(types.SimpleNamespace):
    """Gramatika koja generira beskontekstni jezik."""

    @classmethod
    def iz_komponenti(klasa, varijable, abeceda, pravila, početna):
        """Sipser page 104 definition 2.2 - definicija iz četvorke."""
        assert abeceda
        simboli = disjunktna_unija(varijable, abeceda)
        assert all(set(pravilo) <= simboli for pravilo in pravila)
        assert početna in varijable
        pozitivna = None
        del simboli
        return klasa(**vars())

    @property
    def komponente(G):
        """Sipser page 104 definition 2.2 - rastav u četvorku."""
        return G.varijable, G.abeceda, G.pravila, G.početna

    @property
    def simboli(G):
        """Skup simbola (varijabli i znakova zajedno) Y."""
        return disjunktna_unija(G.varijable, G.abeceda)

    @classmethod
    def iz_strelica(klasa, strelice):
        """Parsiranje streličnog zapisa beskontekstne gramatike.
        Pogledati funkciju util.parsiraj_strelice_BKG za detalje."""
        return klasa.iz_komponenti(*parsiraj_strelice_BKG(strelice))

    @classmethod
    def iz_konačnog_automata(klasa, ka):
        """Pretvorba konačnog automata u desnolinearnu gramatiku."""
        nka = NedeterminističkiKonačniAutomat.iz_konačnog_automata(ka)
        rezultat = klasa.iz_nedeterminističkog_konačnog_automata(nka)
        assert rezultat.desnolinearna()
        return rezultat
        
    @classmethod
    def iz_nedeterminističkog_konačnog_automata(klasa, nka):
        """Pretvorba NKA u desnolinearnu gramatiku."""
        Q, Σ, Δ, q0, F = nka.komponente
        P = {(p,α,q) if α != ε else (p,q) for p,α,q in Δ} | {(q,) for q in F}
        return BeskontekstnaGramatika.iz_komponenti(Q, Σ, P, q0)

    def daje(gramatika, prije, poslije):
        """Daje li riječ prije riječ poslije po pravilima gramatike?
        Vraća None, ili pravilo i mjesto na kojem ga treba primijeniti."""
        assert set(prije) | set(poslije) <= gramatika.simboli
        for mjesto, simbol in enumerate(prije):
            if simbol in gramatika.varijable:
                for pravilo in gramatika.pravila:
                    if simbol == pravilo[0]:
                        if primijeni(pravilo, prije, mjesto) == poslije:
                            return pravilo, mjesto

    def validan(gramatika, izvod):
        """Je li izvod u skladu s pravilima gramatike?"""
        početak, *ostatak = izvod
        if list(početak) != [gramatika.početna]:
            return False
        for prije, poslije in zip(izvod, ostatak):
            if not gramatika.daje(prije, poslije):
                print(prije, poslije)
                return False
        return set(izvod[~0]) <= gramatika.abeceda

    def desnolinearna(gramatika):
        """Je li gramatika desnolinearna?"""
        for A, *zamjene in gramatika.pravila:
            if not zamjene:
                continue
            elif len(zamjene) == 2:
                b, C = zamjene
                if b in gramatika.abeceda and C in gramatika.varijable:
                    continue
            return False
        return True

    def Chomskyjeva(gramatika):
        """Je li gramatika u Chomskyjevoj normalnoj formi?
        Ako jest, postavlja i oznaku da je gramatika sigurno pozitivna."""
        for A, *zamjene in gramatika.pravila:
            if len(zamjene) == 1:
                a, = zamjene
                if a in gramatika.abeceda:
                    continue
            elif len(zamjene) == 2:
                if set(zamjene) <= gramatika.varijable:
                    continue
            return False
        if gramatika.pozitivna is None:
            gramatika.pozitivna = True
        return True

    def faza_START(G):
        stara_S = G.početna
        for A, *zamjene in G.pravila:
            if stara_S in zamjene:
                nova_S = novo('S', G.varijable)
                G.varijable.add(nova_S)
                G.pravila.add((nova_S, stara_S))
                G.početna = nova_S
                break

    def faza_TERM(G):
        N = {}
        for α in G.abeceda:
            for pravilo in G.pravila.copy():
                if α in pravilo and len(pravilo) > 2:
                    if α not in N:
                        N[α] = novo('N' + str(α), G.simboli)
                        G.varijable.add(N[α])
                        G.pravila.add((N[α], α))
                    G.pravila.remove(pravilo)
                    G.pravila.add(tuple(N[α] if s == α else s for s in pravilo))
                
    def faza_BIN(G):
        for pravilo in G.pravila.copy():
            if len(pravilo) >= 4:
                G.pravila.remove(pravilo)
                početna = trenutna = pravilo[0]
                for simbol in pravilo[1:-2]:
                    vezna = novo(početna, G.varijable)
                    G.varijable.add(vezna)
                    G.pravila.add((trenutna, simbol, vezna))
                    trenutna = vezna
                G.pravila.add((trenutna, pravilo[~1], pravilo[~0]))

    def faza_DEL(G):
        nep = set()
        while True:
            for A, *zamjene in G.pravila:
                if A not in nep and set(zamjene) <= nep:
                    nep.add(A)
                    break
            else: break
        G.pozitivna = G.početna not in nep
        for A, *zamjene in G.pravila.copy():
            pojave = {i for i, simbol in enumerate(zamjene) if simbol in nep}
            if pojave:
                for podskup in partitivni_skup(pojave):
                    novo_pravilo = [A]
                    for i, simbol in enumerate(zamjene):
                        if i not in podskup:
                            novo_pravilo.append(simbol)
                    G.pravila.add(tuple(novo_pravilo))
        G.pravila -= {(A,) for A in G.varijable}

    def faza_UNIT(G):
        maknuta = set()
        while True:
            for pravilo in G.pravila.copy():
                if len(pravilo) == 2 and pravilo[1] in G.varijable:
                    A, B = pravilo
                    G.pravila.remove(pravilo)
                    maknuta.add(pravilo)
                    for zamjensko in G.pravila.copy():
                        if zamjensko[0] == B:
                            B, *u = zamjensko
                            novo = tuple([A] + u)
                            if novo not in maknuta:
                                G.pravila.add(novo)
                    break
            else: break
            
    def ChNF(gramatika):
        """Ekvivalentna (do na ε) gramatika u Chomskyjevoj normalnoj formi."""
        if gramatika.Chomskyjeva():
            return gramatika
        G = copy.deepcopy(gramatika)
        G.faza_START()
        G.faza_TERM()
        G.faza_BIN()
        G.faza_DEL()
        G.faza_UNIT()
        return G

    def označi(gramatika, l):
        """Označava stanja gramatike dodatnom oznakom l, radi disjunktnosti."""
        def označi_pravilo(p, l):
            for simbol in p:
                if simbol in gramatika.varijable: yield označi1(simbol, l)
                else: yield simbol
        V, Σ, P, S = gramatika.komponente
        Vl = {označi1(A, l) for A in V}
        Pl = {tuple(označi_pravilo(p, l)) for p in P}
        Sl = označi1(S, l)
        return BeskontekstnaGramatika.iz_komponenti(Vl, Σ, Pl, Sl)

    def unija(G1, G2):
        """Beskontekstna gramatika koja generira L(G1)∪L(G2)."""
        assert G1.abeceda == G2.abeceda
        if not G1.varijable.isdisjoint(G2.varijable):
            G1 = G1.označi(1)
            G2 = G2.označi(2)
        V1, Σ, P1, S1 = G1.komponente
        V2, Σ, P2, S2 = G2.komponente
        S = novo('S', V1 | V2 | Σ)
        V = disjunktna_unija(V1, V2, {S})
        P = disjunktna_unija(P1, P2, {(S, S1), (S, S2)})
        return BeskontekstnaGramatika.iz_komponenti(V, Σ, P, S)

    def konkatenacija(G1, G2):
        """Beskontekstna gramatika koja generira L(G1)L(G2)."""
        assert G1.abeceda == G2.abeceda
        if not G1.varijable.isdisjoint(G2.varijable):
            G1 = G1.označi(3)
            G2 = G2.označi(4)
        V1, Σ, P1, S1 = G1.komponente
        V2, Σ, P2, S2 = G2.komponente
        S = novo('S', V1 | V2 | Σ)
        V = disjunktna_unija(V1, V2, {S})
        P = disjunktna_unija(P1, P2, {(S, S1, S2)})
        return BeskontekstnaGramatika.iz_komponenti(V, Σ, P, S)

    def plus(G):
        """Beskontekstna gramatika koja generira Kleenejev plus od L(G)."""
        V0, Σ, P0, S0 = G.komponente
        S = novo('S', V0)
        V = disjunktna_unija(V0, {S})
        P = disjunktna_unija(P0, {(S, S0, S), (S, S0)})
        return BeskontekstnaGramatika.iz_komponenti(V, Σ, P, S)

    def zvijezda(G):
        """Beskontekstna gramatika koja generira Kleenejevu zvijezdu od L(G)."""
        V0, Σ, P0, S0 = G.komponente
        S = novo('S', V0)
        V = disjunktna_unija(V0, {S})
        P = disjunktna_unija(P0, {(S, S0, S), (S,)})
        return BeskontekstnaGramatika.iz_komponenti(V, Σ, P, S)

    def CYK(gramatika, riječ):
        """Cocke-Younger-Kasami algoritam za problem prihvaćanja za BKG."""
        G = gramatika.ChNF()
        if not riječ:
            return not G.pozitivna
        
        expand = {V: set() for V in G.varijable}
        for pravilo in G.pravila:
            if len(pravilo) == 3:
                A, B, C = pravilo
                expand[A].add((B, C))

        @memoiziraj
        def izvodi(A, i, j):
            assert j > i
            if j - i == 1:
                return (A, riječ[i]) in G.pravila
            for k in range(i + 1, j):
                for B, C in expand[A]:
                    if izvodi(B, i, k) and izvodi(C, k, j):
                            return True
            return False
        return izvodi(G.početna, 0, len(riječ))
