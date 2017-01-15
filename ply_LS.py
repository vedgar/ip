from types import SimpleNamespace
from re import escape
from ply import lex, yacc

### Leksička analiza

tokens = ('PROP_VAR', 'NEGACIJA', 'KONJUNKCIJA', 'DISJUNKCIJA',
          'KONDICIONAL', 'BIKONDICIONAL', 'OTVORENA', 'ZATVORENA')

t_NEGACIJA = escape('!')
t_KONJUNKCIJA = escape('&')
t_DISJUNKCIJA = escape('|')
t_KONDICIONAL = escape('->')
t_BIKONDICIONAL = escape('<->')
t_OTVORENA = escape('(')
t_ZATVORENA = escape(')')

@lex.Token(r'P\d+')
def t_PROP_VAR(t):
    t.value = int(t.value[1:])
    return t

def t_error(t):
    print('Nepoznat znak', t.value[0])
    t.lexer.skip(1)

t_ignore = ' '

lex.lex()

### Sintaktička analiza

class Stablo(SimpleNamespace):
    pass

def p_binarni(p):
    '''
    formula : dnf KONDICIONAL dnf
    formula : dnf BIKONDICIONAL dnf
    dnf : dnf DISJUNKCIJA ek
    ek : ek KONJUNKCIJA literal
    '''
    p[0] = Stablo(lijevo=p[1], op=p[2], desno=p[3])

def p_unit(p):
    '''
    formula : dnf
    dnf : ek
    ek : literal
    literal : atom
    atom : PROP_VAR
    '''
    p[0] = p[1]

def p_unarni(p):
    'literal : NEGACIJA atom'
    p[0] = Stablo(op=p[1], ispod=p[2])

def p_zagrade(p):
    'atom : OTVORENA formula ZATVORENA'
    p[0] = p[2]

def p_error(p):
    raise RuntimeError('Greška pri parsiranju!', p)

yacc.yacc()

### Semantička analiza

def var(formula):
    if isinstance(formula, int):
        return {formula}
    elif formula.op == '!':
        return var(formula.ispod)
    else:
        return var(formula.lijevo) | var(formula.desno)

def vrijednost(formula, interpretacija):
    if isinstance(formula, int):
        return int(formula in interpretacija)
    elif formula.op == '!':
        return 1 - vrijednost(formula.ispod, interpretacija)
    else:
        veznik = formula.op
        lijevo = vrijednost(formula.lijevo, interpretacija)
        desno = vrijednost(formula.desno, interpretacija)
        if veznik == '&': return min(lijevo, desno)
        elif veznik == '|': return max(lijevo, desno)
        elif veznik == '->': return max(1 - lijevo, desno)
        elif veznik == '<->': return (1 + lijevo + desno) % 2

if __name__ == '__main__':
    lex.input('P1<->((')
    for tok in iter(lex.token, None):
        print(tok)
    t = yacc.parse('P1->(P3<->P1&P72&P3)')
    print(t, var(t), vrijednost(t, {1, 3}), sep='\n')
