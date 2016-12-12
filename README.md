# Interpretacija programa

Repozitorij za kod koji ćemo pisati.

    >>> import ip
    >>> ip.leksička_analiza('''\
    glavnica *= 1 + 0.02*vrijeme  # pribroji kamatu
    ''')
    NAME'glavnica'
    STAREQUAL'*='
    NUMBER'1'
    PLUS'+'
    NUMBER'0.02'
    STAR'*'
    NAME'vrijeme'
    COMMENT'# pribroji kamatu'
    NEWLINE'\n'
    >>> ip.sintaksna_analiza('2 <= 3')
    ['eval_input', ['testlist', ['test', ['or_test', ['and_test', ['not_test', ['comparison', 
      ['expr', ['xor_expr', ['and_expr', ['shift_expr', ['arith_expr', ['term', ['factor', ['power', ['atom_expr', ['atom', 'NUMBER:2']]]]]]]]]], 
      ['comp_op', 'LESSEQUAL:<='],
      ['expr', ['xor_expr', ['and_expr', ['shift_expr', ['arith_expr', ['term', ['factor', ['power', ['atom_expr', ['atom', 'NUMBER:3']]]]]]]]]]
    ]]]]]]]
