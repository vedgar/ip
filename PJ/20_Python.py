import tokenize, io, keyword, ast, dis, warnings, textwrap

def tokeni(string):
    lex = tokenize.tokenize(io.BytesIO(string.encode('utf8')).readline)
    for tok in list(lex)[1:-1]:
        if keyword.iskeyword(tok.string): tip = tok.string.upper()
        else: tip = tokenize.tok_name[tok.exact_type]
        print('\t' + tip + repr(tok.string))

def stablo_parsiranja(string):
    warnings.simplefilter('ignore')
    try: import parser
    except ImportError: return print(textwrap.dedent('''\
        U verziji 3.10 Python je prešao na novi parser, koji više nije
        zasnovan na beskontekstnoj gramatici (i nije dostupan kroz
        Pythonovu standardnu biblioteku). To je u skladu s onim što smo
        rekli na nastavi, da sve više parsera producira direktno AST umjesto
        stabala parsiranja. Više o razlozima možete pročitati u PEP617.
        Ako ipak želite vidjeti stablo parsiranja za gornji komad koda, 
        pokrenite ovaj program pod Pythonom 3.9 ili nižim.'''))
    def ispis(t, razina, nastavak=False):
        if not nastavak: print(end=' '*2*razina)
        if len(t) == 2:
            if isinstance(t[~0], str):
                tip, sadržaj = t
                if keyword.iskeyword(sadržaj): tip = sadržaj.upper()
                else: tip = tokenize.tok_name[tip]
                print(tip + repr(sadržaj))
            else:
                print(t[0] - 256, end='>')
                ispis(t[1], razina, True)
        else:
            print(t[0] - 256)
            for podstablo in t[1:]:
                ispis(podstablo, razina + 1)
    ispis(parser.suite(string).tolist(), 0)

def apstablo(string): print(ast.dump(ast.parse(string)))

def bytecode(string): dis.dis(string)

if __name__ == '__main__':
    primjer = 'for x in 2, 3: print(x)'
    print(primjer)
    for funkcija in tokeni, stablo_parsiranja, apstablo, bytecode:
        print(funkcija.__name__.center(75, '-'))
        funkcija(primjer)
        print()

# Module:
#     body = [...]:
#         For:
#             target = Name(id='x', ctx=Store())
#             iter = Tuple(elts=[Num(n=2), Num(n=3)], ctx=Load())
#             body = [...]
#                 Expr:
#                     value = Call:
#                         func = Name(id='print', ctx=Load())
#                         args = [Name(id='x', ctx=Load())]
#                         keywords = []
#             orelse = []

