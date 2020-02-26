import tokenize, io, keyword, parser, ast, dis

def tokeni(string):
    lex = tokenize.tokenize(io.BytesIO(string.encode('utf8')).readline)
    for tok in list(lex)[1:-1]:
        if keyword.iskeyword(tok.string): tip = tok.string.upper()
        else: tip = tokenize.tok_name[tok.exact_type]
        print(tip + repr(tok.string))

def stablo_parsiranja(string):
    def ispis(t, razina, nastavak=False):
        if not nastavak: print(end=' '*2*razina)
        if len(t) == 2:
            if isinstance(t[~0], str):
                tip, sadržaj = t
                if keyword.iskeyword(sadržaj): tip = sadržaj.upper()
                else: tip = tokenize.tok_name[tip]
                print(tip + repr(sadržaj))
            else:
                print(t[0] - 256, end=' > ')
                ispis(t[1], razina, True)
        else:
            print(t[0] - 256)
            for podstablo in t[1:]:
                ispis(podstablo, razina + 1)
    ispis(parser.suite(string).tolist(), 0)

def apstraktno_sintaksno_stablo(string):
    print(ast.dump(ast.parse(string)))

bytecode = dis.dis
    
