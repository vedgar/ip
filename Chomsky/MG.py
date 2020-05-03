mg = '''\
S>a
S>PZ
PZ>aZ
aZ>aa
PZ>PAAZ
PA>PB
BAA>BBA
BAZ>BBZ
PB>PAB
ABB>AAAB
ABZ>AAAAZ
PA>aA
aAA>aaA
aAZ>aaZ
'''

import collections, contextlib

pravila = collections.defaultdict(set)
for linija in mg.splitlines():
    lijevo, desne = linija.split('>')
    pravila[lijevo].update(desne.split('|'))
# print(pravila)

def mjesta(riječ, podriječ):
    i = -1
    with contextlib.suppress(ValueError):
        while ...:
            i = riječ.index(podriječ, i+1)
            yield i, i + len(podriječ)

def sljedeće(pravila, riječ):
    for lijevo, desna in pravila.items():
        for početak, kraj in mjesta(riječ, lijevo):
            for desno in desna:
                yield riječ[:početak] + desno + riječ[kraj:]

def jezik(pravila, do=16, početna='S'):
    moguće = {'S'}
    while ...:
        novo = set()
        for riječ in moguće:
            if riječ.islower(): yield riječ
            elif len(riječ) <= do:
                novo.update(sljedeće(pravila, riječ))
        if not novo: return
        moguće = novo

for riječ in jezik(pravila, do=64):
    print(riječ)
