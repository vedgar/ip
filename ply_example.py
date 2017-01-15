import collections
from ply import lex, yacc

tokens = 'SYMBOL', 'COUNT'

t_SYMBOL = ('C[laroudsemf]?|Os?|N[eaibdpos]?|S[icernbmg]?|P[drmtboau]?|'
    'H[eofgas]?|A[lrsgutcm]|B[eraik]?|Dy|E[urs]|F[erm]?|G[aed]|I[nr]?|Kr?|'
    'L[iaur]|M[gnodt]|R[buhenaf]|T[icebmalh]|U|V|W|Xe|Yb?|Z[nr]')

def t_COUNT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    raise TypeError(f'Unknown text {t.value!r}')

lex.lex()

lex.input('CH3COOH')
for tok in iter(lex.token, None):
    print(tok.type, repr(tok.value))

Atom = collections.namedtuple('Atom', 'symbol count')

def p_species_list(p):
    "chemical_equation :  chemical_equation species"
    p[0]               =  p[1]             + [p[2]]

def p_species(p):
    "chemical_equation : species"
    p[0]               = [p[1]]

def p_single_species(p):
    """
    species : SYMBOL
    species : SYMBOL COUNT
    """
    if len(p) == 2:
        p[0] = Atom(p[1], 1)
    elif len(p) == 3:
        p[0] = Atom(p[1], p[2])
        
def p_error(p):
    raise TypeError(f'Syntax error at {p.value!r}')
    
yacc.yacc()

print(yacc.parse('H2SO4'))
