from TS import TuringovStroj, prikaz
from itertools import islice

def doit(func): func()

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
    for konf in T.izračunavanje('*/***/**/***'): prikaz(*konf)

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
    T = TuringovStroj.iz_tablice('''a   b   c   _   1   2   3
                                 0  1+1 !   !   !   !   +4  !
                                 1  +   2+2 !   !   !   +   !
                                 2  !   +   3-3 !   !   !   +
                                 3  -   -   !   !   +0  -   -
                                 4  !   !   !   .   !   +   +''')
    print(T.prihvaća('aaabbbccc'))

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
                                 0   /+1 +2d  !   !
                                 1   +   _+2r !   ! 
                                 2r  +   !   #-3 !
                                 3   -   !   +4  ! 
                                 4   _-5 !   +   !
                                 5   _+4 +6  -   !
                                 6   .   !   +   !
                                 2d  +8  !   !   !
                                 8   +   !   .   !''')
    print(T.rezultat('/'))

def Hanić():
    T = TuringovStroj.iz_tablice('''i   z   r   _
                                 0  _+3 +1  +1  !
                                 1  +   +   +   -2
                                 2  z-  r.  i.  !
                                 3  +4  +4  +4  .
                                 4  +   +   +   -5
                                 5  z-  r-6 i-6 z+7
                                 6  -   -   -   i.
                                 7  !   +   !   -8
                                 8  !   _.  !   !''')
    print(T.rezultat('izii'))

def Basioli():
    T = TuringovStroj.iz_tablice('''i   z   r   _   $
                                 0  +1  $+3 +1  i.  !
                                 1  +   +   +   -2  !
                                 2  r.  i-  z.  !   !
                                 3  -5  +   -5  i-4 !
                                 4  !   i-  !   !   i.
                                 5  !   -   !   !   z+6
                                 6  +1  +   +1  !   !''')
    print(T.rezultat('zzzz'))

def Avirović():
    T = TuringovStroj.iz_tablice('''i   z   r   _   $
                                 0  +   +   +   -1  !
                                 1  r+2 $-1 z+2 i+2 i+3
                                 2  !   !   !   .   i+
                                 3  !   !   !   i.  i+''')
    print(T.rezultat('ziz'))
    # for konf in T.izračunavanje(''): prikaz(*konf); input()

def Bogdanić():
    T = TuringovStroj.iz_tablice('''i   z   r   _   #
                                 0  +1  +1  +1  !   ! 
                                 1  +   +   +   -3  !''')

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

def Vasung():
    T = TuringovStroj.iz_tablice('''i   z   r   _   
                                 A  +B  +B  +B  -
                                 B  +   +   +   -C
                                 C  r. i-C  z.  i.''')
    print(T.rezultat('zz'))

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

def Radenić():
    T = TuringovStroj.iz_tablice('''i    z   r    _   I   R   $
                                 0  I+1  $+z R+1  i.  !   !   !
                                 1  +    +   +    -3  !   !   !
                                 3  r-4  i-  z-4  !   r.  z.  !
                                 z  +1   +   +1   i-2 !   !   !
                                 2  !    i-  !    !   !   !   i.
                                 4  -    -   -    !   i.  r.  z.''')
    print(T.rezultat('ziz'))

@doit
def Kocijan():
    T = TuringovStroj.iz_tablice('''i    z    r    _    R
                                 q0 +q1  +q1  R+p1 !    !
                                 q1 +    +    +    -q2  !
                                 p1 +p3  +p1  +p3  i-p2 !
                                 q2 z.   r.   i-   !    !
                                 p2 !    !    i-   !    r.
                                 p3 +    +    +    -p4  !
                                 p4 z-p5 r-p5 i-   !    !
                                 p5 !    !    -    !    r.''')
    # print(T.rezultat('rrr'))
    for konf in T.izračunavanje('rrr'): prikaz(*konf); input()
