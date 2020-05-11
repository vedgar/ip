from Parser import *

#Lista programa se leksira, parsira i interpretira
#svaki program mora imati main funkciju, svaka funkcija ima svoj doseg
#definirana je pomoćna print funkcija, može primiti više izraza (npr. print(a, b)),
#a za svaki izraz ispiše njega i njegovu vrijednost
#za provjeru vrijednosti se također može koristiti i assert

if __name__ == '__main__':
    programi = [r"""

    int piUsingIsPrime(int a); //Deklaracija funkcije

    bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int factor = 3; factor <= n/factor; factor += 2) {
        if (n % factor == 0)
        return false;
    }
    return true;
    }
    /* Funkcija koja za broj n vraća broj prostih brojeva od 1 do n */
    int piUsingIsPrime(int n) {
    int primeCount = 0;
    for (int i = 2; i <= n; i++)
        //if (isPrime(i) == true) //Poziv funkcije isPrime, deklarirane gore
        primeCount++;
    return primeCount;
    }
    //Funkcija vraća reverz broja
    int reverseInt(int n) {
        int reversedNumber = 0;
        int remainder;
        while(n != 0)
        {
            remainder = n%10;
            reversedNumber = reversedNumber*10 + remainder;
            n /= 10;
        }
        return reversedNumber;
    }

    int main() {
           int a;
           int b;
           int c;
           c += a += 8;

        assert(c == 8);
        print(reverseInt(257));
        assert(reverseInt(257) == 752);
        print(piUsingIsPrime(10));
       return 2;
    }
    """, r"""

    int x(bool a);

    int x(bool aaa); //dozvoljena redeklaracija, nije bitno što su različita imena argumenata

    int x(bool a) {}

    int x(bool a) {} //greška, nije dozvoljena redefinicija

    int main() {
        return 0;
    }
    """, r"""
    int main() {
        int a;
        {
            int a = 0; //greška, redeklaracija varijable
        }
        return 0;
    }
    """, r"""
    int main() {
        int a;
        {
            int c;
        }
        c = 3; //greška, izvan dosega
        return 0;
    }
    """, r"""
    int main() {
        int a;
        for ( ; a < 4; a++) {   //dozvoljeno je izostaviti i prvi i treći argument
            if (a == 3) break;
            for(int b = 0; b < 3; ) {
                if (b % 2 == 0) {
                    b += 1;
                }
                else {
                    print(a, b);
                    b += 1;
                }
            }
        }
        return 0;
    }
    """, r"""
    int main() {
        int a; //svakoj je varijabli automatski dodijeljena defaultna vrijednost
        int c;
        while (a < 5) {
            if (a % 2 == 0) {
                c = ~c;
            }
            else c = c << a;
            print(c);
            a++;
        }
        //return 'c'; //greška
    } //funkcija ne mora imati povratu vrijednost, bitno je da nije pogrešnog tipa
    """, r"""
        int main() { //prioriteti operatora
            //bool b = "b";  greška
            bool a = true;
            int c = a ? 2 : -1;
            print(c);
            int d = c == 2 ? 2 + 6*3 : 8;
            print(d);

            if (c == 2 && d == 20)
                string f = "van dosega";

            //print(f); //greška
            string f;
            if (c == 2 && d == 20)
                print(f = "u dosegu");
        }
    """, r"""
        int main() {
            int[] a ;
            int[] b;
            int[] c = alloc_array(int, 9);
            a = alloc_array(int, 7);
            a[0] = 6;
            a[5] += 3;
            b = a;
            b[4] = -7;
            b[3]-=1;
            c[8] = a[5] *= 4;
            print(a);
            print(c);
        }
    """]

    for program in programi:
        try:
            print("IZVRŠAVANJE PROGRAMA")
            tokeni = list(Lekser(program))
            #print(*tokeni)
            program = C0Parser.parsiraj(tokeni)
            #print(program)
            program.izvrši()
            print("------------")
        except Greška as ex:
            print('GREŠKA:', ex)
            print("------------")
