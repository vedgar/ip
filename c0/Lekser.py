from Tokeni import *
from uuid import uuid1
import re

separatoriZnakovi = '()[]{},;'
escapeZnakovi = ['\n', '\t', '\v', '\b', '\r', '\f', '\a', '\'', '\"', '\\']
escapeChars = ['n', 't', 'v', 'b', 'r', 'f', 'a', "'", '"', '\\']
naredbe = {'if', 'else', 'while', 'for', 'assert', 'error', 'print'}

assignOperators = {Tokeni.PLUSEQ, Tokeni.MINUSEQ, Tokeni.ZVJEQ, Tokeni.SLASHEQ, Tokeni.MODEQ, Tokeni.LSHIFTEQ, Tokeni.RSHIFTEQ, Tokeni.ASSIGN, Tokeni.ANDEQ, Tokeni.POTEQ, Tokeni.CRTAEQ}
primitivniTipovi = {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR, Tokeni.POINTER, Tokeni.ARRAY}
osnovniIzrazi = {Tokeni.DECIMALNI, Tokeni.HEKSADEKADSKI, Tokeni.STRLIT, Tokeni.CHRLIT,
            Tokeni.BOOLEAN, Tokeni.NULL}

def isxdigit(znak):
    """Provjerava je li znak hex znamenka"""
    return znak != '' and (znak.isdigit() or znak in 'ABCDEFabcdef')

def isuzatv(znak):
    """Provjerava je li znak UZATV"""
    return znak ==']'

def isNChar(znak):
    """Provjerava je li znak nchar"""
    p = re.compile('^[ -~]$')
    if (p.match(znak) is None or znak == '"'):
        return False
    return True

def isSChar(znak):
    """Provjerava je li znak schar"""
    if (isNChar(znak) or znak in escapeZnakovi):
        return True
    return False

def Lekser(kôd):
    lex = Tokenizer(kôd)
    citamString = False

    for znak in iter(lex.čitaj, ''):
        if (citamString):
            if znak == '\\':
                idući = lex.čitaj()
                if (idući not in escapeChars):
                    lex.greška("Neispravan string")
            elif isNChar(znak):
                continue
            elif znak == '"':
                citamString = False
                yield lex.token(Tokeni.STRLIT)
            else:
                lex.greška("Neispravan string")
        elif znak == ' ': 
            lex.token(E.PRAZNO) #enter i tabulator su nam tokeni
        elif znak == '"': #prelazimo u stanje citanja stringa
            citamString = True
            continue
        elif znak.isalpha() or znak == '_':
            # onda je identifier
            lex.zvijezda(identifikator)
            if lex.sadržaj in {'true', 'false'}: yield lex.token(Tokeni.BOOLEAN)
            elif (lex.sadržaj == 'NULL'): yield lex.token(Tokeni.NULL)
            elif (lex.sadržaj in naredbe): yield lex.token(Tokeni(lex.sadržaj))
            elif (lex.sadržaj == 'break'): yield lex.token(Tokeni.BREAK)
            elif (lex.sadržaj == 'continue'): yield lex.token(Tokeni.CONTINUE)
            elif (lex.sadržaj == 'return'): yield lex.token(Tokeni.RETURN)
            elif (lex.sadržaj == 'alloc'): yield lex.token(Tokeni.ALLOC)
            elif (lex.sadržaj == 'alloc_array'): yield lex.token(Tokeni.ALLOCA)
            elif (lex.sadržaj == 'int'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                else: yield lex.token(Tokeni.INT)
            elif (lex.sadržaj == 'bool'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.BOOL)
            elif (lex.sadržaj == 'char'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.CHAR)
            elif (lex.sadržaj == 'string'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.STRING)
            elif (lex.sadržaj == 'void'): 
                sljedeći = lex.pogledaj()
                if sljedeći == '*':
                    lex.čitaj()
                    yield lex.token(Tokeni.POINTER)
                elif sljedeći == '[':
                    lex.čitaj()
                    lex.pročitaj(']')
                    yield lex.token(Tokeni.ARRAY)
                yield lex.token(Tokeni.VOID)
            else:
                yield lex.token(Tokeni.IDENTIFIER)
        elif znak.isdigit(): 
            # onda je dec ili hex
            if znak == '0': 
                sljedeći = lex.pogledaj()
                if sljedeći == 'x' or sljedeći == 'X':
                    # onda je hex
                    lex.čitaj()
                    lex.plus(isxdigit)
                    yield lex.token(Tokeni.HEKSADEKADSKI)
                elif sljedeći.isdigit():
                    lex.greška('očekujem x ili X')
                    
                else:
                    yield lex.token(Tokeni.DECIMALNI)
            else:
                lex.pogledaj()
                # onda je dec
                lex.zvijezda(str.isdigit)
                yield lex.token(Tokeni.DECIMALNI)
        # je li chrlit?
        elif znak == "'":
            idući = lex.čitaj()
            if (not isNChar(idući) and not idući in escapeZnakovi and not idući == '"' and not idući == '\0'):
                raise LeksičkaGreška("Neispravan chrlit")
            kraj = lex.čitaj()
            if (kraj == "'"):
                yield lex.token(Tokeni.CHRLIT)
            else:
                raise LeksičkaGreška("Neispravan chrlit")           
        #je li escape sekvenca ili separator?
        elif znak in separatoriZnakovi:
            yield lex.token(Tokeni(znak))
        elif znak in escapeZnakovi:
            if (znak.isspace()):
                lex.token(Tokeni(znak))
            else:
                yield lex.token(Tokeni(znak))
        # je li operator?
        # !, !=
        elif znak == '!':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.DISEQ)
            else:
                yield lex.token(Tokeni.USKL)
        # ~
        elif znak == '~':
            yield lex.token(Tokeni.TILDA)
        # *, *=
        elif znak == '*':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.ZVJEQ)
            else: 
                yield lex.token(Tokeni.ZVJ)
        # .
        elif znak == '.':
            yield lex.token(Tokeni.TOCKA)
        # -, ->, -=, --
        elif znak == '-':
            sljedeći = lex.pogledaj()
            if sljedeći == '>':
                lex.čitaj()
                yield lex.token(Tokeni.STRELICA)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.MINUSEQ)
            elif sljedeći == '-':
                lex.čitaj()
                yield lex.token(Tokeni.DECR)
            else:
                yield lex.token(Tokeni.MINUS)
        # /, /=
        elif znak == '/':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.SLASHEQ)
            elif sljedeći == '/':

                lex.zvijezda(lambda znak: znak != '\n')
                lex.pročitaj('\n')
                lex.token(Tokeni.COMMENT)
            elif sljedeći == '*': #komentari tipa /* */
                lex.pročitaj('*')
                while not (lex.čitaj() == '*' and lex.pogledaj() == '/'): pass
                lex.pročitaj('/')
                lex.token(Tokeni.COMMENT)
            else:
                yield lex.token(Tokeni.SLASH)
        # %, %=
        elif znak == '%':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.MODEQ)
            else:
                yield lex.token(Tokeni.MOD)
        
        # +, +=, ++
        elif znak == '+':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.PLUSEQ)
            elif sljedeći == '+':
                lex.čitaj()
                yield lex.token(Tokeni.INCR)
            else:
                yield lex.token(Tokeni.PLUS)
        #operatori <, <<, <<=, <=
        elif znak == '<':
            sljedeći = lex.pogledaj()

            if sljedeći == '<':
                lex.čitaj()
                ssljedeći = lex.pogledaj()
                if ssljedeći == '=':
                    lex.čitaj()
                    yield lex.token(Tokeni.LSHIFTEQ)
                else:
                    yield lex.token(Tokeni.LSHIFT)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.LESSEQ)
            else:
                yield lex.token(Tokeni.LESS)
        # >, >>, >>=, >=
        elif znak == '>':
            sljedeći = lex.pogledaj()
            if sljedeći == '>':
                lex.čitaj()
                ssljedeći = lex.pogledaj()
                if ssljedeći == '=':
                    lex.čitaj()
                    yield lex.token(Tokeni.RSHIFTEQ)
                else:
                    yield lex.token(Tokeni.RSHIFT)
            elif sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.GRTEQ)
            else:
                yield lex.token(Tokeni.GRT)
        # =, ==
        elif znak == '=':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.EQ)
            else:
                yield lex.token(Tokeni.ASSIGN)
        # &, &=, &&
        elif znak == '&':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.ANDEQ)
            elif sljedeći == '&':
                lex.čitaj()
                yield lex.token(Tokeni.LAND)
            else:
                yield lex.token(Tokeni.BITAND)
        # |, |=, ||
        elif znak == '|':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.CRTAEQ)
            elif sljedeći == '|':
                lex.čitaj()
                yield lex.token(Tokeni.LOR)
            else:
                yield lex.token(Tokeni.BITOR)
        # ^, ^=
        elif znak == '^':
            sljedeći = lex.pogledaj()
            if sljedeći == '=':
                lex.čitaj()
                yield lex.token(Tokeni.POTEQ)
            else:
                yield lex.token(Tokeni.BITEXCLOR)
        # ?
        elif znak == '?':
            yield lex.token(Tokeni.CONDQ)
        # :
        elif znak == ':':
            yield lex.token(Tokeni.CONDDOT)