import types, itertools, collections
from KA import Kartezijev_produkt

parcijalna_funkcija = lambda f, A, B: (
    f.keys() <= A and set(map(frozenset, f.values())) <= B)

partitivni_skup = lambda skup: set(itertools.chain.from_iterable(
    map(frozenset, itertools.combinations(skup, r))
        for r in range(0, 1+len(skup))))
ε = ''


class NedeterminističkiKonačniAutomat(types.SimpleNamespace):
    @classmethod
    def definicija(klasa, stanja, abeceda, prijelaz, početno, završna):
        assert abeceda and početno in stanja and završna <= stanja
        assert parcijalna_funkcija(prijelaz,
            Kartezijev_produkt(stanja, abeceda | {ε}),
            partitivni_skup(stanja))
        return klasa(**locals())

    def prihvaća(automat, riječ):
        stanja = automat.εzatvorenje({automat.početno})
        for znak in riječ:
            skupovi = [automat.prijelaz[q, znak] for q in stanja]
            if skupovi:
                stanja = automat.εzatvorenje(set.union(*skupovi))
            else:
                stanja = set()
        return not stanja.isdisjoint(automat.završna)

    def εzatvorenje(automat, skup):
        stari_skup = skup.copy()
        while True:
            for stanje in stari_skup:
                skup |= automat.prijelaz[stanje, ε]
            if skup == stari_skup:
                break
            stari_skup = skup.copy()
        return skup

N1 = NedeterminističkiKonačniAutomat.definicija(
    {0, 1, 2},
    {'0', '1'},
    collections.defaultdict(set, {(0, ε): {1}, (1, '0'): {0, 2}, (2, '1'): {0}}),
    0,
    {1},
)
