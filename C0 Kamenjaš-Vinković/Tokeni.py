from pj import *

class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Tokeni(enum.Enum):
    #separatori
    OOTV, OZATV, UOTV, UZATV, VOTV, VZATV, ZAREZ = '()[]{},'
    SEP = ';'
    #unarni operatori
    USKL, TILDA, MINUS, ZVJ = '!~-*'
    #binarni operatori
    TOCKA, STRELICA, SLASH, MOD, PLUS, LSHIFT, RSHIFT = '.', '->', '/', '%', '+', '<<', '>>'
    LESS, LESSEQ, GRTEQ, GRT, EQ, DISEQ, BITAND, BITEXCLOR, BITOR = '<', '<=', '>=', '>', '==', '!=', '&', '^', '|'
    LAND, LOR, CONDQ, CONDDOT = '&&', '||', '?', ':'
    #operatori pridruzivanja
    PLUSEQ, MINUSEQ, ZVJEQ, SLASHEQ, MODEQ, LSHIFTEQ, RSHIFTEQ, ASSIGN = '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '='
    ANDEQ, POTEQ, CRTAEQ = '&=', '^=', '|='
    #postfiksni operatori
    DECR, INCR = '--', '++'
    #escape sekvence
    NRED, NTAB, NVERTTAB, BACKSP, RET, FFEED, ALERT = '\n', '\t', '\v', '\b', '\r', '\f', '\a'
    QUOTE, DBLQUOTE, ESCSLASH = '\'', '\"', '\\'
    #komentari
    COMMENT, COM_BEGIN, COM_END = '//', '/*', '*/'
    # statementi
    IF, ELSE, WHILE, FOR, ASSERT, ERROR = 'if', 'else', 'while', 'for', 'assert', 'error'
    # misc
    ALLOC, ALLOCA = 'alloc', 'alloc_array'
    PRINT = 'print'
    class IDENTIFIER(Token):
        def vrijednost(self, imena, vrijednosti): 
            try: return vrijednosti[self]
            except KeyError: self.nedeklaracija()
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class DECIMALNI(Token):
        def vrijednost(self, imena, vrijednosti): 
            return int(self.sadržaj)
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class HEKSADEKADSKI(Token):
        def vrijednost(self, imena, vrijednosti):
            return hex(self.sadržaj)
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class CHRLIT(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj[1 : len(self.sadržaj) - 1]
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class STRLIT(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj[1 : len(self.sadržaj) - 1]
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class BOOLEAN(Token):
        def vrijednost(self, imena, vrijednosti):
            return self.sadržaj == 'true'
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class NULL(Token):
        def vrijednost(self, imena, vrijednosti):
            return None
        def izvrši(self, imena, vrijednosti):
            self.vrijednost(imena, vrijednosti)
    class BREAK(Token):
        def izvrši(self, imena, vrijednosti):
            raise BreakException
    class CONTINUE(Token):
        def izvrši(self, imena, vrijednosti):
            raise ContinueException
    class RETURN(Token):
        def izvrši(self, imena, vrijednosti):
            raise ReturnException
    class INT(Token):
        def vrijednost(self, imena, vrijednosti):
            return int
    class BOOL(Token):
        def vrijednost(self, imena, vrijednosti):
            return bool
    class CHAR(Token):
        def vrijednost(self, imena, vrijednosti):
            return str
    class STRING(Token):
        def vrijednost(self, imena, vrijednosti):
            return str
    class VOID(Token):
        def vrijednost(self, imena, vrijednosti):
            return
    class POINTER(Token):
        def vrijednost(self, imena, vrijednosti):
            return
    class ARRAY(Token):
        def vrijednost(self, imena, vrijednosti):
            return
    