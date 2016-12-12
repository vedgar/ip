import tokenize, io, types, parser, symbol, collections, token


class Token(types.SimpleNamespace):
    def __str__(self):
        return '{}{!r}'.format(self.vrsta, self.sadržaj)


def tokeni(ulaz):
    for token in tokenize.tokenize(io.BytesIO(ulaz.encode('utf8')).readline):
        t = Token()
        t.kod = token.type
        t.vrsta_kod = token.exact_type
        t.tip = tokenize.tok_name[token.type]
        t.vrsta = tokenize.tok_name[token.exact_type]
        t.sadržaj = token.string
        t.redak, t.stupac = token.start
        t.kraj_redak, t.kraj_stupac = token.end
        t.linija = token.line
        if t.tip not in {'ENCODING', 'ENDMARKER'}:
            yield t


def leksička_analiza(ulaz):
    try:
        for token in tokeni(ulaz):
            print(token)
    except tokenize.TokenError:
        print('Greška: nezavršen ulaz')


def uvrsti_simbole(stablo):
        korijen, *podstabla = stablo
        if korijen in symbol.sym_name:
            pravilo = [symbol.sym_name[korijen]]
            pravilo.extend(map(uvrsti_simbole, podstabla))
            return pravilo
        elif korijen in token.tok_name:
            sadržaj, = podstabla
            return token.tok_name[korijen] + ':' + sadržaj


def sintaksna_analiza(ulaz):
    for funkcija in parser.expr, parser.suite:
        try:
            stablo = funkcija(ulaz).tolist()
        except SyntaxError as greška:
            zadnja_greška = greška
        else:
            if stablo[-2:] == [[token.NEWLINE, ''], [token.ENDMARKER, '']]:
                del stablo[-2:]
            return uvrsti_simbole(stablo)
    poruka, (izvor, broj_linije, stupac, linija) = zadnja_greška.args
    print(linija + '^'.rjust(stupac) + ': greška')
