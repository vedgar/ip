from pj import *

class LS(enum.Enum):
    NEG = '!'
    KONJ = '&'
    DISJ = '|'
    KOND = '->'
    BIKOND = '<->'
    OTV = '('
    ZATV = ')'
    PVAR = None

def ls_lex(kod):
    lex = Tokenizer(kod)
    while True:
        znak = lex.čitaj()
        if not znak: return  # kraj ulaza
        elif znak == '!': yield lex.token(LS.NEG)
        elif znak == '&': yield lex.token(LS.KONJ)
        elif znak == '|': yield lex.token(LS.DISJ)
        elif znak == '(': yield lex.token(LS.OTV)
        elif znak == ')': yield lex.token(LS.ZATV)
        elif znak == '-':
            if lex.čitaj() == '>': yield lex.token(LS.KOND)
            else: raise lex.greška('Nepotpuna strelica')
        elif znak == '<':
            if lex.čitaj() == '-' and lex.čitaj() == '>':
                yield lex.token(LS.BIKOND)
            else: raise lex.greška('Nepotpuna strelica')
        elif znak == 'P':
            prvo = lex.čitaj()
            if prvo == '0': yield lex.token(LS.PVAR)
            elif prvo.isdigit():
                while lex.čitaj().isdigit(): pass
                lex.vrati()  # pročitali smo jedan previše
                yield lex.token(LS.PVAR)
            else: raise lex.greška('Nema znamenke nakon P')
        else: raise lex.greška()

for tok in ls_lex('!(P0&!!(P3->P5))'):
    print(tok)
