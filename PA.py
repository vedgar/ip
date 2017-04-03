from util import *


class PotisniAutomat(types.SimpleNamespace):
    """Automat koji prepoznaje beskontekstni jezik."""

    @classmethod
    def iz_komponenti(klasa,
            stanja, abeceda, abeceda_stoga, prijelaz, početno, završna):
        """Relacijska definicija: Δ⊆Q×(Σ∪{ε})×(Γ∪{ε})×Q×(Γ∪{ε})"""
        assert abeceda
        assert početno in stanja
        assert završna <= stanja
        assert relacija(prijelaz, stanja, ε_proširenje(abeceda),
            ε_proširenje(abeceda_stoga), stanja, ε_proširenje(abeceda_stoga))
        return klasa(**vars())

    @classmethod
    def iz_funkcije(klasa,
            stanja, abeceda, abeceda_stoga, f_prijelaza, početno, završna):
        """Funkcijska definicija: δ:Q×(Σ∪{ε})×(Γ∪{ε})→℘(Q×(Γ∪{ε}))
        Sipser page 113 definition 2.13"""
        prijelaz = relacija_iz_funkcije(f_prijelaza)
        return klasa.iz_komponenti(
            stanja, abeceda, abeceda_stoga, prijelaz, početno, završna)

    @classmethod
    def iz_tablice(klasa, tablica):
        """Parsiranje tabličnog zapisa potisnog automata.
        Pogledati funkciju util.parsiraj_tablicu_PA za detalje."""
        return klasa.iz_komponenti(*parsiraj_tablicu_PA(tablica))

    @classmethod
    def iz_nedeterminističkog_konačnog_automata(klasa, nka):
        """Pretvorba iz nedeterminističkog konačnog automata u potisni."""
        Q, Σ, Δ, q0, F = nka.komponente
        ΔP = {(q, α, ε, p, ε) for (q, α, p) in Δ}
        return klasa.iz_komponenti(Q, Σ, set(), ΔP, q0, F)

    @property
    def funkcija_prijelaza(automat):
        """Relacija prijelaza pretvorena u funkciju."""
        return funkcija_iz_relacije(automat.prijelaz, automat.stanja,
            ε_proširenje(automat.abeceda), ε_proširenje(automat.abeceda_stoga))

    @property
    def komponente(automat):
        """Relacijska definicija - rastav u šestorku."""
        return (automat.stanja, automat.abeceda, automat.abeceda_stoga,
                automat.prijelaz, automat.početno, automat.završna)

    def prihvaća(automat, riječ):
        """Prihvaća li automat zadanu riječ?
        Poluodlučivo: može zapeti u beskonačnoj petlji ako ne prihvaća."""
        red = collections.deque([(riječ, automat.početno, None)])
        while red:
            riječ, stanje, stog = red.popleft()
            if not riječ and stanje in automat.završna:
                return True
            for polazno, znak, uzmi, dolazno, stavi in automat.prijelaz:
                if stanje != polazno: continue
                if znak == ε: nova_riječ = riječ
                elif riječ and riječ[0] == znak: nova_riječ = riječ[1:]
                else: continue
                if uzmi == ε: novi_stog = stog
                elif stog and stog[~0] == uzmi: novi_stog = stog[0]
                else: continue
                if stavi != ε: novi_stog = novi_stog, stavi
                red.append((nova_riječ, dolazno, novi_stog))
        return False

    def crtaj(automat):
        """Ispisuje na ekran dijagram automata u DOT formatu.
        Dobiveni string može se kopirati u sandbox.kidstrythisathome.com/erdos
        ili u www.webgraphviz.com."""
        print(DOT_PA(automat))
