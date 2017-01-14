import collections, enum, types


class Buffer:
    MAX_BUFFER = 1
    
    def __init__(self, sequence):
        self.iterator = iter(sequence)
        self.buffer = []
        self.redni_broj = 0

    def čitaj(self):
        self.redni_broj += 1
        if self.buffer:
            self.zadnje = self.buffer.pop()
        else:
            self.zadnje = next(self.iterator, None)
        # print(self.zadnje)
        return self.zadnje

    def vrati(self):
        self.redni_broj -= 1
        assert len(self.buffer) < self.MAX_BUFFER
        self.buffer.append(self.zadnje)

    def pogledaj(self):
        znak = self.čitaj()
        self.vrati()
        return znak


class Tokenizer(Buffer):
    def plus(self, *vrste):
        pročitano = ''
        while True:
            znak = self.čitaj()
            if vrsta(znak) in vrste:
                pročitano += znak
            else:
                self.vrati()
                return pročitano
        
    def praznine(self):
        return self.plus('praznina')

    def ime(self):
        return self.plus('slovo', 'znamenka')

    def broj(self):
        return self.plus('znamenka')


class Token(types.SimpleNamespace):
    def __init__(self, simbol, sadržaj):
        self.tip, self.sadržaj = simbol, sadržaj

    def __repr__(self):
        return self.tip.name + repr(self.sadržaj)


def vrsta(znak):
    if znak is None: return 'kraj'
    elif znak.isspace(): return 'praznina'
    elif znak.isalpha(): return 'slovo'
    elif znak.isdigit(): return 'znamenka'
    elif znak.isprintable(): return 'ostalo'
    else: return 'greška'


class Parser(Buffer):
    def pročitaj(self, *simboli):
        sljedeći = self.čitaj()
        if sljedeći.tip in simboli:
            return sljedeći
        poruka = 'Token #{}: očekivano {}, pročitano {}'
        očekivani = ' ili '.join(simbol.name for simbol in simboli)
        raise SyntaxError(poruka.format(self.redni_broj, očekivani, sljedeći))

    def granaj(self, *simboli):
        sljedeći = self.pročitaj(*simboli)
        self.vrati()
        return sljedeći.tip


class AST(types.SimpleNamespace):
    def __repr__(self):
        atributi = vars(self).copy()
        ime = atributi.pop('stablo', type(self).__name__)
        stavke = ['{}={}'.format(k, v) for k, v in atributi.items()]
        return ime + ', '.join(stavke).join('()')
