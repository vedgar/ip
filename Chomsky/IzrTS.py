from TS import TuringovStroj, prikaz
from itertools import islice, product

def ibeta(w):
    assert set(w) <= {'*', '/'}
    return tuple(map(len, ''.join(w).split('/')))

the_func = None
def doit(func):
    global the_func
    if the_func: raise RuntimeError('More than one function decorated!')
    the_func = func
    func()

def Scizr():
    T = TuringovStroj.iz_tablice('''i   r   z   _   *
                                  0 +   +   +   -1  !
                                  1 r+2 z+2 *-  i.  i+
                                  2 !   !   !   .   i+''')
    riječ = ''
    for _ in range(29):
        print(' ', riječ, end='\t')
        riječ = T.rezultat(riječ)

def I24():
    T = TuringovStroj.iz_tablice('''*   /   _
                                  0 /+1 +2  !
                                  1 _+  _+2 !
                                  2 _-3 -5  +
                                  3 !   *+4 -
                                  4 !   !   /+2
                                  5 !   _+6 -
                                  6 !   _+7 + 
                                  7 _+  _+8 !
                                  8 _+  !   .''')
    # for konf in T.izračunavanje('*/***/**/***'): prikaz(*konf)
    for n in range(15):
        for w in product(T.abeceda, repeat=n):
            v = T.rezultat(w)
            if v is not None: print(ibeta(w), v, sep='\t')

def I22():
    T = TuringovStroj.iz_tablice('''*   /    _   $   #
                                  0 $+1 *+10 !   !   !
                                  1 _+  _+2  !   !   !
                                  2 +   !    #-3 !   !
                                  3 -   !    +4  !   !
                                  4 _-5 !    !   !   _-9
                                  5 !   !    -   *+6 !
                                  6 !   !    $+7 !   !
                                  7 _-5 !    +   !   _-8
                                  8 !   !    -   _.  !
                                  9 !   !    -   _.  !
                                 10 +   !    -11 !   !
                                 11 _.  !    !   !   !''')
    print(T.rezultat('**/****'))

def Grafplus():
    T = TuringovStroj.iz_tablice('''a   b   c   _
                                  0 _+1 _+2 !   .
                                  1 +   +2  +3  !
                                  2 !   +   +3  !
                                  3 !   !   +   -4
                                  4 !   !   _-5 !
                                  5 -6  -6  -6  .
                                  6 -   -   -   +0''')
    print(T.prihvaća('aababbcccccc'))
    # for konf in T.izračunavanje('aababbcccccc'): prikaz(*konf)

def OAL3():
    T = TuringovStroj.iz_tablice('''a  b  c  _ A  B C
                                 0 A+1 !  !  . ! +4 !
                                  1 + B+2 !  ! !  + !
                                  2 !  + C-3 ! !  ! +
                                  3 -  -  -  - +0 - -
                                  4 !  !  !  . !  + +''')
    for n in range(13):
        for w in product(T.abeceda, repeat=n):
            if T.prihvaća(w): print(''.join(w))

def double():
    T = TuringovStroj.iz_tablice('''*   _   $   #
                                 0  $+1 .   !   !
                                 1  +   *+2 !   !
                                 2  -   -   +3  !
                                 3  #+  -4  !   !
                                 4  -   !   *+6 *+5
                                 5  +   *-4 !   !
                                 6  +   -7  !   !
                                 7  _.  !   !   !''')
    for konf in T.izračunavanje('*' * 4): prikaz(*konf)
    # print(T.rezultat('******'))

def Raštegorac6():
    T = TuringovStroj.iz_tablice('''*   /   _   $   #
                                  0 #+4 +1  !   !   !
                                  1 +2  !   !   !   !
                                  2 +   !   .   !   !
                                  4 +   +5  !   !   !
                                  5 $-6 !   !   +   !
                                  6 !   +7  !   -   !
                                  7 -   !   !   +8  ! 
                                  8 #+4 +9  !   !   !
                                  9 +10 !   !   +   !
                                 10 +   !   .   !   !''')
    for konf in T.izračunavanje('/*****'): prikaz(*konf); input()
    print(T.rezultat('/**'))

def Delić():
    T = TuringovStroj.iz_tablice(''' *   /   _   #
                                 0  /+1  +2d !   !
                                 1   +  _+2r !   ! 
                                 2r  +   !  #-3  !
                                 3   -   !   +4  ! 
                                 4   _-5 !   +   !
                                 5   _+4 +6  -   !
                                 6   .   !   +   !
                                 2d  +8  !   !   !
                                 8   +   !   .   !''')
    print(T.rezultat('/'))

def Avirović():
    T = TuringovStroj.iz_tablice('''i   z   r   _   $
                                 0  +   +   +   -1  !
                                 1  r+2 $-1 z+2 i+2 i+3
                                 2  !   !   !   .   i+
                                 3  !   !   !   i.  i+''')
    w = ''
    for _ in range(20): print(w := T.rezultat(w))

def Staroverški():
    T = TuringovStroj.iz_tablice('''i   z   r   _   #
                                 0  +   +   +   #-1 !
                                 1  r.  i-4 z.  !   !
                                 4  r.  i-1 z.  !   !''')
    print(T.rezultat('z'))

def Žanić():
    T = TuringovStroj.iz_tablice('''i   z   r   _   $
                                 0  +1  $+1 +1  !   !
                                 1  +   +   +   $-2 i.
                                 2  r+3 i-  z+3 !   i+1
                                 3  +   +   +   !   _.''')
    print(T.rezultat('zz'))

def Živković():
    T = TuringovStroj.iz_tablice('''i   z   r   _
                                 R  +D  +D  +   i-I
                                 D  +   +   +   -L
                                 I  .   .   i-  .
                                 L  z.  r.  i-  !''')
    print(T.rezultat('r'))

def Čižić():
    T = TuringovStroj.iz_tablice('''i   z   r   _   $
                                  0 +1  $+1 +1  +1  !
                                  1 +   +   +   -2  !
                                  2 r.  i-  z.  i.  i+3
                                  3 +   !   !   i.  !''')
    print(T.rezultat('zzzzz'))

def Fabulić():
    T = TuringovStroj.iz_tablice('''i   z   r   _
                                 0  +1  +1  +1  i.
                                 1  +   +   +   -2
                                 2  r.  +3  z.  !
                                 3  !   !   !   i.''')
    print(T.rezultat('iiiz'))

def Martinjak():
    T = TuringovStroj.iz_tablice('''i   z   r   _   ž
                                 0  +1  ž+1 +1  i.  !
                                 1  +   +   +   -3  !
                                 3  r.  i-  z.  !   i+2 
                                 2  +   +   +   i.  !''')
    print(T.rezultat('izizzzz'))

def Požgaj():
    T = TuringovStroj.iz_tablice('''i   z   r   _   a   b   c
                                 0  a+1 b+1 c+1 .   !   !   !
                                 1  +   +   +   -2  !   !   !
                                 2  _-3 i.  z.  !   _.  i.  z.
                                 3  r-  i.  z.  !   r.  i.  z.''')
    print(T.rezultat('zz'))

def Španić():
    T = TuringovStroj.iz_tablice('''i   z   r   _   ž
                                 0  +1  ž+1 +1  !   !
                                 1  +   +   +   -2  !
                                 2  r.  i-  z.  !   i+4
                                 4  +   !   !   i.  !''')
    print(T.rezultat('ziz'))

def Gaurina():
    T = TuringovStroj.iz_tablice('''i   z   r   _   *
                                 0  +   +   +   -1  !
                                 1  z+2 r+2 *-  !   -3
                                 2  !   !   !   .   i-
                                 3  !   !   !   .   i+''')
    print(T.rezultat('izr'))

def Kozjak():
    T = TuringovStroj.iz_tablice('''i   z   r   _   
                                 0  +1  +2  +1  !
                                 1  +   +   +   -3
                                 2  +1  +   +1  i-4
                                 3  r.  i-  z.  !
                                 4  .   i-  !   !''')
    print(T.rezultat('zzirzzr'))

def Đurić():
    T = TuringovStroj.iz_tablice('''i   z   r   _
                                 0  +1  +2  +2  !
                                 1  +   +2  +2  -4
                                 2  +   +   +   -3
                                 3  z-  r.  i.  !
                                 4  _-5 !   !   !
                                 5  z-  .   !   .''')
    print(T.rezultat('zriz'))

def Buljubašić():
    T = TuringovStroj.iz_tablice('''1   2   3   _
                                 0  +   +   +   -1
                                 1  -2  1.  2.  !
                                 2  +4  +3  +5  !
                                 3  3-  1.  !   !
                                 4  3-  1.  2-5 !
                                 5  3-  .   2-  !''')
    print(T.rezultat('1111'))

def D21():
    T = TuringovStroj.iz_tablice('''*    /    _
                                 q0 +    +q1  !
                                 q1 +    +q2  !
                                 q2 +    !    . ''')
    for n in range(6):
        for w in product('*/', repeat=n):
            if T.prihvaća(w): print(''.join(w))

def D24():
    T = TuringovStroj.iz_tablice('''*   /   _   x   $
                                 s  !   !   !   !   +0
                                 0  x+1 !   !   +   !
                                 1  +   +2  !   !   !
                                 2  x+3 !   .   +   !
                                 3  -4  !   -5  !   !
                                 4  -   -   !   -   +0
                                 5  !   +6  !   -   !
                                 6  .   !   !   !   !''')
    T.abeceda.add('$')
    for konf in T.izračunavanje('$**/*'): 
        prikaz(*konf)
        input()

    raise SystemExit
    for n in range(9):
        for w in map(''.join, product('*/', repeat=n)):
            if T.prihvaća('$' + w): print(w)

def D41():
    T = TuringovStroj.iz_tablice('''a   b   _   c   d   e   f
                                 0  e+1 f+1 .   !   !   !   !
                                 1  +2  +2  !   !   !   !   !
                                 2  +1  +1  -3  !   !   !   !
                                 3  _-4 _-4 !   !   !   !   !
                                 4  -   -   !   +5  +5  +5  +5
                                 5  c+6 d+6 !   !   !   a+7 b+7
                                 6  +   +   -3  !   !   !   !
                                 7  !   !   .   a+  b+  !   !''')
    for konf in T.izračunavanje('aa'): prikaz(*konf)
    raise SystemExit
    for n in range(6):
        for w in product('ab', repeat=n):
            print(w, T.rezultat(w))

def D23(): 
    T = TuringovStroj.iz_tablice('''a  b  c  _ C B A
                                 0 A+1 !  !  . ! ! !
                                  1 +2 +5 !  ! ! + !
                                  2 + B+3 !  ! ! + !
                                  3 !  + C+4 ! + ! !
                                  4 -  -  -  - - - +0
                                  5 !  !  +6 ! + ! !
                                  6 !  !  !  . ! ! !''')
    for n in range(13):
        for w in product('abc', repeat=n):
            if T.prihvaća(w): print(''.join(w))

def D24():
    T = TuringovStroj.iz_tablice('''*  /  _  p  x
                                 0 p+1 !  !  !  !
                                 1  + x+2 !  !  !
                                 2 x-3 !  .  !  +
                                 3 x+2 !  !  !  -''')
    for n in range(12):
        for w in product(T.abeceda, repeat=n):
            if T.prihvaća(w): print(tuple(map(len, ''.join(w).split('/'))))

def D54():
    T = TuringovStroj.iz_tablice('''*   _  $  x  y
                                 0 $+1  .  !  !  !
                                 1 x+2 *-6 !  +  +4
                                 2  +  y-3 !  !  +
                                 3  -   !  +1 -  -
                                 4  !  *-5 !  !  +
                                 5  !   ! *. *- *-
                                 6  !   ! *.  !  !''')
    for n in range(12):
        for w in map(''.join, product(T.abeceda, repeat=n)):
            if (r := T.rezultat(w)) is not None: print(w, r)

def Imrović_un2dec():
    T = TuringovStroj.iz_tablice('''*   0   1   2   3   4   5   6   7   8   9   _   D
                                 A 1+B  !   !   !   !   !   !   !   !   !   !  0.  0+ 
                                 B  +   !   !   !   !   !   !   !   !   !   !   -C  !
                                 C _-D  !   .   !   !   !   !   !   !   !   !   !   !
                                 D  -  1+E 2+E 3+E 4+E 5+E 6+E 7+E 8+E 9+E D-   !  1+A
                                 E  +B  !   !   !   !   !   !   !   !   !   !   .  0+''')
    for n in 0, 1, 2, 9, 10, 11, 12, 19, 20, 21, 22, 30, 98, 99, 100, 101, 102, 103, 1000:
        print(n, r := T.rezultat('*' * n), r == str(n), sep='\t')

def Imrović_un2bin():
    T = TuringovStroj.iz_tablice('''*   0   1   _   D
                                 A 1+B  !   !  0.  0+
                                 B  +   !   !   -C  !
                                 C _-D  !   .   !   !
                                 D  -  1+E D-   !  1+A
                                 E  +B  !   !   .  0+''')
    for n in range(129):
        print(n, r := T.rezultat('*' * n), '0b' + r == bin(n), sep='\t')

def Brigljević():
    T = TuringovStroj.iz_tablice('''*    0    1   _   $   #    z 
                                 A  $+B  !    !   0.  !   !    !
                                 B  +    !    !   *+C !   !    ! 
                                 C  !    !    !   0-D !   !    !
                                 D  #+E  -    -   !   +H  -    !
                                 E  !    +E   +E  -F  !   +E   !
                                 F  !    1+G  z-  !   !   1+G  !
                                 G  !    !    !   -D  !   !    0+
                                 H  !    #-Q0 #-Q1 -J !   +    !
                                 Q0 !    !    !   !   0+I -    !
                                 Q1 !    !    !   !   1+I -    !
                                 I  !    !    !   !   !   $+H  !
                                 J  !    !    !   !   _.  _-H  !''')
    #print(T.rezultat('*'))
    for i, konf in enumerate(T.izračunavanje('*')):
        if i > 30: break
        prikaz(*konf)

def Šantek():
    T = TuringovStroj.iz_tablice('''*   0   1   _   x   z
                                 A  1+B !   !   0.  !   !
                                 B  x-C !   !   .   !   !
                                 C  !   1+E z-  !   -   1+D
                                 D  !   !   !   !   0+E 0+
                                 E  !   !   !   -G  +   0+
                                 G  !   .   .   !   _-  !''')
    print(T.rezultat('***'))

    for i, konf in enumerate(T.izračunavanje('****')):
        if i > 30: break
        prikaz(*konf)

@doit
def Pešut():
    T = TuringovStroj.iz_tablice('''*   0   1  _   x   y
                                 A  1+B !   !  0.  !   !
                                 B  x-C !   !  .   !   !
                                 C  !   1+D y-E !  -   !
                                 D  x-C !   !   -H +   !
                                 E  !   1+I y-  !  !  1+G
                                 G  !   !   !   ! 0+D 0+
                                 H  !   .   .   ! _-   !
                                 I  !   !   !   !  +D 0+''')
    print(T.rezultat('********'))

