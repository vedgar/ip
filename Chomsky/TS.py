from util import *


class TuringovStroj(types.SimpleNamespace):

    @classmethod
    def iz_komponenti(klasa, stanja, abeceda, radna_abeceda, praznina,
                      prijelaz, početno, prihvat):
        assert abeceda
        assert abeceda <= radna_abeceda
        assert praznina in radna_abeceda - abeceda
        assert {početno, prihvat} <= stanja
        assert funkcija(prijelaz,
                        Kartezijev_produkt(stanja - {prihvat}, radna_abeceda),
                        Kartezijev_produkt(stanja, radna_abeceda, {-1, 1}))
        return klasa(**vars())

    @classmethod
    def iz_tablice(klasa, tablica):
        """Parsiranje tabličnog zapisa Turingovog stroja.
        Pogledati funkciju util.parsiraj_tablicu_TS za detalje."""
        return klasa.iz_komponenti(*parsiraj_tablicu_TS(tablica))

    @property
    def komponente(stroj):
        """Relacijska definicija - rastav u sedmorku."""
        return (stroj.stanja, stroj.abeceda, stroj.radna_abeceda,
                stroj.praznina, stroj.prijelaz, stroj.početno, stroj.prihvat)

    def prihvaća(T, riječ):
        """Prihvaća li Turingov stroj T zadanu riječ?
        Poluodlučivo: može zapeti u beskonačnoj petlji ako ne prihvaća."""
        return T.rezultat(riječ) is not None

    def izračunavanje(T, riječ):
        assert set(riječ) <= T.abeceda
        stanje, pozicija, traka = T.početno, 0, list(riječ)
        yield stanje, pozicija, traka
        while stanje != T.prihvat:
            if pozicija >= len(traka): traka.append(T.praznina)
            stanje, traka[pozicija], pomak = T.prijelaz[stanje, traka[pozicija]]
            pozicija = max(pozicija + pomak, 0)
            yield stanje, pozicija, traka

    def rezultat(T, riječ):
        for stanje, pozicija, traka in T.izračunavanje(riječ):
            if stanje == T.prihvat: break
            if (T.prijelaz[stanje, T.praznina] == (stanje, T.praznina, 1) and
                pozicija == len(traka)): return
        while traka and traka[~0] == T.praznina: del traka[~0]
        join_ok = all(type(znak) is str and len(znak) == 1 for znak in traka)
        return ''.join(traka) if join_ok else traka
