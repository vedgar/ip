from Lekser import *
from collections import ChainMap
class Program(AST('naredbe')):
    def izvrši(self):

        tipovi = ChainMap()
        vrijednosti = ChainMap()

        rezultati = []
        for naredba in self.naredbe: 
            rezultati.append(naredba.izvrši(tipovi, vrijednosti))

        for tip in tipovi:
            if(tip.sadržaj == 'main'  and tipovi[tip].tip.vrijednost(None, None) == int):
                tipovi[tip].izvrijedni(tipovi, vrijednosti, [])
                return

        raise GreškaIzvođenja("nema main funkcije")

class PrintFunkcija(AST('print')):
    def izvrši(izraz, imena, vrijednosti):
        for p in izraz.print:
            if (isinstance(p.vrijednost(imena, vrijednosti), list) and not isinstance(p.vrijednost(imena,vrijednosti)[0],str) and len(p.vrijednost(imena, vrijednosti)) > 1):
                print("Veličina polja ", p.vrijednost(imena, vrijednosti)[0], ", elementi: ", ", ".join("{}".format(x[0]) for x in p.vrijednost(imena, vrijednosti)[1:]))
            else:
                print (p, p.vrijednost(imena, vrijednosti)[0])

class DeklaracijaFunkcije(AST('tip ime varijable')):
    def izvrši(izraz, imena, vrijednosti):

        #ako već postoji od prije, provjeri slažu li se argumenti
        if (izraz.ime in imena):
            izraz.provjeri(imena, vrijednosti)
        else:
            #registriraj sebe u function and variable namespace
            imena[izraz.ime] = izraz
            #funkcija = Funkcija(izraz.tip, izraz.ime, izraz.varijable, "")
            #funkcija.izvrši(imena, vrijednosti)

    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        raise GreškaIzvođenja("ne može se izvrijedniti samo deklarirana funkcija")

    def provjeri(izraz, imena, vrijednosti):
        postojeća = imena[izraz.ime]
        if (izraz.tip != postojeća.tip):
            raise GreškaIzvođenja("nisu kompatibilni povratni tipovi iste funkcije")
        if (len(izraz.varijable) != len(postojeća.varijable)):
            raise GreškaIzvođenja("različiti broj argumenata za istu funkciju")
        for i in range (0, len(izraz.varijable)):
            if (izraz.varijable[i].tip != postojeća.varijable[i].tip):
                raise GreškaIzvođenja("nekompatibilni tipovi argumenata iste funkcije")
        
class DefinicijaFunkcije(AST('tip ime varijable tijelo')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.ime in imena and isinstance(imena[izraz.ime], DefinicijaFunkcije)):
            raise GreškaIzvođenja("Ne smiju postojati dvije definicije iste funkcije!")
        else:
            #registriraj sebe u function and variable namespace
            imena[izraz.ime] = izraz

            izraz.funkcija = Funkcija(izraz.tip, izraz.ime, izraz.varijable, izraz.tijelo)
            izraz.funkcija.izvrši(imena, vrijednosti)
    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        return izraz.funkcija.izvrijedni(imena, vrijednosti, argumenti)


class Funkcija(AST('tip ime varijable tijelo')):
    def izvrši(izraz, imena, vrijednosti):

        #svaka funkcija ima svoj scope
        varijableUFunkciji = ChainMap()
        vrijednostiUFunkciji = ChainMap()
        #dodaj sve već postojeće funkcije u scope
        for key in imena.keys():
            varijableUFunkciji[key] = imena[key]
        
        for varijabla in izraz.varijable:
            varijabla.izvrši(varijableUFunkciji, vrijednostiUFunkciji)
            
        izraz.varijableF = varijableUFunkciji
        izraz.vrijednostiF = vrijednostiUFunkciji

    def izvrijedni(izraz, imena, vrijednosti, argumenti):
        if (len(argumenti) != len(izraz.varijable)):
            raise SemantičkaGreška("neispravan broj argumenata kod poziva funkcije")
        for i in range(0, len(argumenti)):
            if (not isinstance(argumenti[i], izraz.varijable[i].tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                raise SemantičkaGreška("neispravan tip argumenta")
            izraz.vrijednostiF[izraz.varijable[i].ime] = argumenti[i]

        izraz.varijableF = izraz.varijableF.new_child()
        izraz.vrijednostiF = izraz.vrijednostiF.new_child()
        
        for naredba in izraz.tijelo:
            try:
                naredba.izvrši(izraz.varijableF, izraz.vrijednostiF)
            except ReturnException as ex:
                #provjera još jel ispravan povratni tip
                povratna = ex.message
                temp = povratna
                if (povratna is None):
                    if (not izraz.tip ** Tokeni.VOID):
                        raise SemantičkaGreška("povratna vrijednost funkcije mora biti void")
                else: #tip povratne vrijednosti se mora slagati s tipom povratne vrijednosti funkcije
                    if(isinstance (povratna, list)):
                        temp = povratna[0]
                    if (not isinstance( temp, izraz.tip.vrijednost(izraz.varijableF, izraz.vrijednostiF))):
                            raise SemantičkaGreška("nekompatibilni povratni tip s povratnim tipom funkcije")

                    izraz.varijableF = izraz.varijableF.parents
                    izraz.vrijednostiF = izraz.vrijednostiF.parents
                return povratna

        izraz.varijableF = izraz.varijableF.parents
        izraz.vrijednostiF = izraz.vrijednostiF.parents
            

class IzvrijedniFunkciju(AST('imeFunkcije argumenti')):
    def izvrši(izraz, imena, vrijednosti):
        #funkcija mora biti deklarirana prije poziva
        if (not izraz.imeFunkcije in imena):
            raise SemantičkaGreška("poziv nepostojeće funkcije!")
        evaluiraniArgumenti = []
        for argument in izraz.argumenti:
            if (isinstance(argument.vrijednost(imena, vrijednosti), list)): 
                evaluiraniArgumenti.append(argument.vrijednost(imena, vrijednosti)[0]) #možda još ovo promijeniti
            else: 
                evaluiraniArgumenti.append(argument.vrijednost(imena, vrijednosti))
        return imena[izraz.imeFunkcije].izvrijedni(imena, vrijednosti, evaluiraniArgumenti) 

    def vrijednost(izraz, imena, vrijednosti):
        return izraz.izvrši(imena, vrijednosti)

class If(AST('uvjet naredba')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.vrijednost(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredba.izvrši(imena, vrijednosti)

        if (isinstance(izraz.naredba, Deklaracija)): #pobriši ju iz namespace-a
            del vrijednosti[izraz.naredba.varijabla.ime]
            del imena[izraz.naredba.varijabla.ime]
        


class IfElse(AST('uvjet naredbaIf naredbaElse')):
    def izvrši(izraz, imena, vrijednosti):
        if (izraz.uvjet.vrijednost(imena, vrijednosti)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            izraz.naredbaIf.izvrši(imena, vrijednosti)

            if (isinstance(izraz.naredbaIf, Deklaracija)): #pobriši ju iz namespace-a
                del vrijednosti[izraz.naredbaIf.varijabla.ime]
                del imena[izraz.naredbaIf.varijabla.ime]
        else:
            izraz.naredbaElse.izvrši(imena, vrijednosti)

            if (isinstance(izraz.naredbaElse, Deklaracija)): #pobriši ju iz namespace-a
                del vrijednosti[izraz.naredbaElse.varijabla.ime]
                del imena[izraz.naredbaElse.varijabla.ime]
        
class Assert(AST('uvjet')):
    def izvrši(izraz, imena, vrijednosti):
        value = izraz.uvjet.vrijednost(imena, vrijednosti)
        if (not isinstance(value, bool)):
            raise GreškaIzvođenja("u assert statement mora ići izraz koji ima bool vrijednost")
        if (not value):
            print("Provjera izraza nije prošla!", izraz)
            raise GreškaIzvođenja()

class Error(AST('poruka')):
    def izvrši(izraz, imena, vrijednosti):
        message = izraz.poruka.vrijednost(imena, vrijednosti)
        if (not isinstance(message, str)):
            raise GreškaIzvođenja("u error može ići samo string")
        print (message)
        raise GreškaIzvođenja()

class Blok(AST('blok')):
    def izvrši(izraz, imena, vrijednosti):
        #uđi jednu razinu niže sa scope-om
        novaImena = imena.new_child()

        #izvrši svaku od naredbi u bloku
        for naredba in izraz.blok:
            naredba.izvrši(novaImena, vrijednosti)

        #pobriši iz vrijednosti sve parove koji se ne pojavljuju u imenima
        for key in novaImena.keys():
            if (not key in imena):
                del vrijednosti[key]

class While(AST('uvjet tijeloWhile')):
    def izvrši(izraz, imena, vrijednosti):
        while (izraz.uvjet.vrijednost(imena, vrijednosti)):
            try:
                izraz.tijeloWhile.izvrši(imena, vrijednosti)
            except BreakException: break
            except ContinueException: continue

class For(AST('s1 e s2 s3')):
    def izvrši(izraz, imena, vrijednosti):

        if (not izraz.s1 == ""):
            if (isinstance(izraz.s1, Deklaracija)):
                ime = izraz.s1.varijabla.ime
            izraz.s1.izvrši(imena, vrijednosti)

        while (izraz.e.vrijednost(imena, vrijednosti)):
            try:
                izraz.s3.izvrši(imena, vrijednosti)
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise SemantičkaGreška("nije dopušteno deklarirati varijablu")
                    izraz.s2.izvrši(imena, vrijednosti)
            except BreakException: break
            except ContinueException: 
                if (not izraz.s2 == ""):
                    if (isinstance(izraz.s2, Deklaracija)):
                        raise SemantičkaGreška("nije dopoušteno deklarirati varijablu")
                    izraz.s2.izvrši(imena, vrijednosti)
                continue
            except ReturnException as e:
                if (not izraz.s1 == "" and isinstance(izraz.s1, Deklaracija)):
                    del vrijednosti[ime]
                    del imena[ime]
                raise ReturnException(e.message)

        if (not izraz.s1 == "" and isinstance(izraz.s1, Deklaracija)):
            del vrijednosti[ime]
            del imena[ime]


            
class Return(AST('povratnaVrijednost')):
    def vrijednost(izraz, imena, vrijednosti):
        if (izraz.povratnaVrijednost == ""):
            return None
        else:
            try:
                return izraz.povratnaVrijednost.vrijednost(imena, vrijednosti)
            except SemantičkaGreška: raise GreškaIzvođenja("varijabla nije nigdje inicijalizirana", izraz.povratnaVrijednost)
    
    def izvrši(izraz, imena, vrijednosti):
        raise ReturnException(izraz.vrijednost(imena, vrijednosti))


class Varijabla(AST('tip ime')):
    def izvrši(izraz, imena, vrijednosti):

        #ako već postoji ova varijabla, digni grešku
        if (izraz.ime in imena):
            izraz.ime.redeklaracija()

        imena[izraz.ime] = izraz.tip
        #svakoj se varijabli daje defaultna vrijednost
        if izraz.tip ** Tokeni.INT:
            vrijednosti[izraz.ime] = [0]
        elif izraz.tip ** Tokeni.CHAR:
            vrijednosti[izraz.ime] = ['\0']
        elif izraz.tip ** Tokeni.STRING:
            vrijednosti[izraz.ime] = [""]
        elif izraz.tip ** Tokeni.BOOL:
            vrijednosti[izraz.ime] = [False]
        elif izraz.tip ** Tokeni.POINTER:
            # N kao NULL
            vrijednosti[izraz.ime] = [['N' + izraz.tip.sadržaj]]
        elif izraz.tip ** Tokeni.ARRAY:
            vrijednosti[izraz.ime] = [0, [izraz.tip.sadržaj]]
        def vrijednost(izraz, imena, vrijednosti): 
            return izraz

class Deklaracija(AST('varijabla vrijedn')):
    def izvrši(izraz, imena, vrijednosti):

        izraz.varijabla.izvrši(imena, vrijednosti)

        #vidi da li se evaluirati izraz na lijevoj strani
        izraz.varijabla.ime.vrijednost(imena, vrijednosti)

        value = izraz.vrijedn.vrijednost(imena, vrijednosti)

        if (isinstance(value, list) and len(value) < 2):
            value = value[0]     

        if izraz.varijabla.tip ** Tokeni.POINTER:
            try:
                value = value[0]
            except: raise GreškaIzvođenja("Neispravna adresa")
            # provjeri tip pointera
            tip = izraz.varijabla.tip.sadržaj
            if(tip == 'int*'):
                if(not isinstance(value, int)):
                    raise GreškaIzvođenja("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'char*'):
                if(not isinstance(value, str) or len(value)!=1):
                    raise GreškaIzvođenja("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'bool*'):
                if(not isinstance(value, bool)):
                    raise GreškaIzvođenja("Nekompatibilan tip pointera, očekujem " + tip)
            elif(tip == 'string*'):
                if(not isinstance(value, str)):
                    raise GreškaIzvođenja("Nekompatibilan tip pointera, očekujem " + tip)
            else: raise GreškaIzvođenja("Nepoznat tip pointera")
            value = [value]

        elif izraz.varijabla.tip ** Tokeni.ARRAY:
            try:
                if(len(value) < 2):
                    raise GreškaIzvođenja("Neispravno polje")
            except: raise GreškaIzvođenja("Neispravno polje")
            # provjeri tip pointera
            tip = izraz.varijabla.tip.sadržaj
            if(tip == 'int[]'):
                if(not isinstance(value[1][0], int)):
                    raise GreškaIzvođenja("Nekompatibilan tip polja, očekujem " + tip)
            elif(tip == 'char[]'):
                if(not isinstance(value[1][0], str) or len(value)!=1):
                    raise GreškaIzvođenja("Nekompatibilan tip polja, očekujem " + tip)
            elif(tip == 'bool[]'):
                if(not isinstance(value[1][0], bool)):
                    raise GreškaIzvođenja("Nekompatibilan tip polja, očekujem " + tip)
            elif(tip == 'string[]'):
                if(not isinstance(value[1][0], str)):
                    raise GreškaIzvođenja("Nekompatibilan tip polja, očekujem " + tip)
            else: raise GreškaIzvođenja("Nepoznat tip polja")                

        elif (not isinstance(value, izraz.varijabla.tip.vrijednost(imena, vrijednosti))):
                raise SemantičkaGreška("nekompatibilni tipovi")
        if(len(vrijednosti[izraz.varijabla.ime]) < 2):
            vrijednosti[izraz.varijabla.ime][0] = value
        else: vrijednosti[izraz.varijabla.ime] = value


class Assignment(AST('lijevaStrana desnaStrana operator')):
    """Pridruživanje van inicijalizacije varijabli. Podržava sve operatore pridruživanja"""
    def vrijednost(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if isinstance(lijevi, list) and len(lijevi) < 2:
            lijevi = lijevi[0]
        
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if isinstance(desni, list) and len(desni) < 2:
            desni = desni[0]
        
        if(isinstance(izraz.lijevaStrana, Dohvati)):
            nešto = izraz.lijevaStrana.odakle.vrijednost(imena, vrijednosti)

        if (isinstance(lijevi, int)):
            if (not isinstance(desni, int)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else: 
                left = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena, vrijednosti, True)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)

        elif (isinstance(lijevi, str) and len(lijevi) == 1):
            if (not (isinstance(lijevi, str) and len(lijevi) == 1)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return [izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1:-1]]

        elif isinstance(lijevi, bool):
            if (not isinstance(desni, bool)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return bool(izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0])

        elif isinstance(lijevi, str):
            if (not isinstance(desni, str)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        elif isinstance(lijevi, list) and len(lijevi) >= 2:
            # onda je array
            if(not isinstance(desni, list) or len(desni) < 2):
                raise GreškaIzvođenja("Nekompatibilni tipovi")
            else:
                # dohvati tip polja
                try:
                    tipl = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1][0][:-2]
                except: tipl = type(izraz.lijevaStrana.vrijednost(imena, vrijednosti)[1][0]).__name__

                try:
                    tipr = izraz.desnaStrana.vrijednost(imena, vrijednosti)[1][0][:-2]
                except: tipr= type(izraz.desnaStrana.vrijednost(imena, vrijednosti)[1][0]).__name__
                
                # provjeri da su isti s lijeve i desne strane
                if(tipl != tipr):
                    raise GreškaIzvođenja("Nekompatibilan tip polja, očekujem " + tipl + "[], dobio " + tipr + "[].")
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator, imena, vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)     


        elif isinstance(lijevi, list):
            if (not isinstance(desni, list)):
                raise GreškaIzvođenja("Nekompatibilni tipovi")
            else:
                # provjeri tip pointera
                try:
                    tipl = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0][0][1:-1]
                except: tipl = izraz.lijevaStrana.tip.sadržaj

                try:
                    tipr = izraz.desnaStrana.vrijednost(imena, vrijednosti)[0][0][1:-1]
                except: tipr = izraz.desnaStrana.tip.sadržaj

                if(tipl != tipr):
                    raise GreškaIzvođenja("Nekompatibilan tip pointera, očekujem " + tipl + "*, dobio " + tipr + "*.")
                Assignment.pridruži(izraz.lijevaStrana, desni, izraz.operator,imena,  vrijednosti, False)
                return izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        else:
            raise SemantičkaGreška("Ne znam assignati operande ovog tipa!")

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

    def pridruži(lijevo, desno, operator,imena,  vrijednosti, je_int):
        lijevo_val = lijevo.vrijednost(imena, vrijednosti)
        if (isinstance(lijevo_val, list)) :
            if(len(lijevo_val) < 2):
                lijevo_val = lijevo_val[0]
        if operator ** Tokeni.ASSIGN:
            lijevo_val = desno
        elif je_int:
            if operator ** Tokeni.PLUSEQ:
                lijevo_val = lijevo_val + desno
            elif operator ** Tokeni.MINUSEQ:
                lijevo_val = lijevo_val - desno
            elif operator ** Tokeni.ZVJEQ:
                lijevo_val = lijevo_val * desno
            elif operator ** Tokeni.SLASHEQ:
                lijevo_val = int(lijevo_val/desno)
            elif operator ** Tokeni.MODEQ:
                lijevo_val = lijevo_val % desno
            elif operator ** Tokeni.LSHIFTEQ:
                lijevo_val = lijevo_val << desno
            elif operator ** Tokeni.RSHIFTEQ:
                lijevo_val = lijevo_val >> desno
            elif operator ** Tokeni.ANDEQ:
                lijevo_val = lijevo_val & desno
            elif operator ** Tokeni.POTEQ:
                lijevo_val = lijevo_val ^ desno
            elif operator ** Tokeni.CRTAEQ:
                lijevo_val = lijevo_val | desno
        else: 
            raise SemantičkaGreška("Ovaj tip ne podržava operator " + operator.sadržaj + ".")
        if(isinstance(lijevo.vrijednost(imena, vrijednosti), list) and len(lijevo.vrijednost(imena, vrijednosti)) < 2):
            lijevo.vrijednost(imena, vrijednosti)[0] = lijevo_val
        elif(isinstance(lijevo.vrijednost(imena, vrijednosti), list)): 
            lijevo.vrijednost(imena, vrijednosti)[:] = lijevo_val[:]
        else: vrijednosti[lijevo] = lijevo_val

class Comparison(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(lijevi, list)):
            lijevi = lijevi[0]
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(desni, list)):
            desni = desni[0]

        #dozvoljeni su samo int i char
        if ((isinstance(lijevi, int) and isinstance(desni, int))
            or (isinstance(lijevi, str) and len(lijevi) == 1 and
             isinstance(desni, str) and len(desni) == 1)):
        
            if (type(lijevi) != type(desni)):
                raise SemantičkaGreška("neispravno uspoređivanje")

            if izraz.operator ** Tokeni.LESS: return lijevi < desni
            elif izraz.operator ** Tokeni.LESSEQ: return lijevi <= desni
            elif izraz.operator ** Tokeni.GRT: return lijevi > desni
            elif izraz.operator ** Tokeni.GRTEQ: return lijevi >= desni
            else: assert not 'slučaj'
        else:
            raise SemantičkaGreška("neispravna usporedba")
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)
        

class Equality(AST('lijevaStrana desnaStrana operator')):
    def vrijednost(izraz, imena, vrijednosti):

        lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(lijevi, list)):
            lijevi = lijevi[0]
        desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(desni, list)):
            desni = desni[0]
        
        if (type(lijevi) != type(desni)):
            raise SemantičkaGreška("neispravno uspoređivanje")

        if izraz.operator ** Tokeni.EQ: return lijevi == desni
        elif izraz.operator ** Tokeni.DISEQ: return lijevi != desni
        else: assert not 'slučaj'
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)


class BinarnaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            if(isinstance(lijevi, list)):
                lijevi = lijevi[0]
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            if(isinstance(desni, list)):
                desni = desni[0]

        except ValueError:
            raise SemantičkaGreška("neispravna binarna operacija")
        
        if izraz.operacija ** Tokeni.PLUS:
            rezultat = lijevi + desni
        elif izraz.operacija ** Tokeni.MINUS:
            rezultat = lijevi - desni
        elif izraz.operacija ** Tokeni.ZVJ:
            rezultat = lijevi * desni
        elif izraz.operacija ** Tokeni.SLASH:
            rezultat = int(lijevi / desni)
        elif izraz.operacija ** Tokeni.MOD:
            rezultat = lijevi % desni
        elif izraz.operacija ** Tokeni.LSHIFT:
            rezultat = lijevi << desni
        elif izraz.operacija ** Tokeni.RSHIFT:
            rezultat = lijevi >> desni                

        return rezultat
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class BitwiseOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        try:
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
            lijevi = lijevi[0]
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
            desni = desni[0]
        except ValueError:
            raise SemantičkaGreška("neispravna bitwise operacija")
        
        if izraz.operacija ** Tokeni.BITAND:
            rezultat = lijevi & desni
        elif izraz.operacija ** Tokeni.BITOR:
            rezultat = lijevi | desni 
        elif izraz.operacija ** Tokeni.BITEXCLOR:
            rezultat = lijevi ^ desni

        return rezultat

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class LogičkaOperacija(AST('lijevaStrana desnaStrana operacija')):
    def vrijednost(izraz, imena, vrijednosti):
        # prvo evaluiraj lijevu stranu, ovisno o njenoj vrijednosti evaluiraj desnu
        if(isinstance(izraz.lijevaStrana.vrijednost(imena, vrijednosti), list)):
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0]
        else: lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if(not isinstance(lijevi, bool)):
            raise SemantičkaGreška("neispravna logička operacija")

        if izraz.operacija ** Tokeni.LAND:
            if (lijevi is False): return False

        elif izraz.operacija ** Tokeni.LOR:
            if (lijevi is True): return True
            
        if(isinstance(izraz.desnaStrana.vrijednost(imena, vrijednosti), list)):
            desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)[0]
        else: desni = izraz.desnaStrana.vrijednost(imena, vrijednosti)
        if(not isinstance(desni, bool)):
            raise SemantičkaGreška("neispravna logička operacija")
        
        if izraz.operacija ** Tokeni.LAND:
            rezultat = bool(lijevi and desni)
        elif izraz.operacija ** Tokeni.LOR:
            rezultat = bool(lijevi or desni)             
        return rezultat  
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)
    

class TernarniOperator(AST('lijevaStrana prviUvjet drugiUvjet')):
    def vrijednost(izraz, imena, vrijednosti):
        if (isinstance(izraz.lijevaStrana.vrijednost(imena, vrijednosti), list)):
            lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)[0]
        else: lijevi = izraz.lijevaStrana.vrijednost(imena, vrijednosti)
        if (isinstance(izraz.prviUvjet.vrijednost(imena, vrijednosti), list)): 
            prvi = izraz.prviUvjet.vrijednost(imena, vrijednosti)[0]
        else: prvi = izraz.prviUvjet.vrijednost(imena, vrijednosti)
        if (isinstance(izraz.drugiUvjet.vrijednost(imena, vrijednosti), list)): 
            drugi = izraz.drugiUvjet.vrijednost(imena, vrijednosti)[0]
        else: drugi = izraz.drugiUvjet.vrijednost(imena, vrijednosti)
        
        if(lijevi):
            return prvi
        else:
            return drugi
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Negacija(AST('iza')):
    """Negacija izraza."""
    def vrijednost(izraz, imena, vrijednosti):
        value = izraz.iza.vrijednost(imena, vrijednosti)[0]
        if (not isinstance(value, bool)):
            raise SemantičkaGreška("unarna negacija se izvršava samo na boolu")
        return [not value]
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)


class Tilda(AST('iza')):
    """Bitwise unary complement"""
    def vrijednost(izraz, imena, vrijednosti):
        value = izraz.iza.vrijednost(imena, vrijednosti)[0]
        if (not isinstance(value, int)):
            raise SemantičkaGreška("bitwise unary complement se izvršava samo na intu")
        return [~value]
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Minus(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        if(isinstance(izraz.iza.vrijednost(imena, vrijednosti), list)):
            value = izraz.iza.vrijednost(imena, vrijednosti)[0]
        else: value = izraz.iza.vrijednost(imena, vrijednosti)
        if (not isinstance(value, int)):
            raise SemantičkaGreška("unarni minus se izvršava samo na intu")
        return [-value]
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dereferenciraj(AST('iza')):
    def vrijednost(izraz, imena, vrijednosti):
        argument = izraz.iza.vrijednost(imena, vrijednosti)
        if(isinstance(argument, list)):
            argument = argument[0]
        else: raise SemantičkaGreška("Ne znam dereferencirati nešto što nije pointer!")

        if(isinstance(argument, list)):
            if len(argument) == 0:
                raise SemantičkaGreška("Ne znam dereferencirati NULL!")
            return (izraz.iza.vrijednost(imena, vrijednosti))[0]
        else: raise SemantičkaGreška("Ne znam dereferencirati nešto što nije pointer!")
    
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dohvati(AST('odakle koga')):
    def vrijednost(izraz, imena, vrijednosti):
        if(int(izraz.koga.sadržaj) >= izraz.odakle.vrijednost(imena, vrijednosti)[0]):
            raise GreškaIzvođenja("Indeks izvan granica array-a")
        return (izraz.odakle.vrijednost(imena, vrijednosti))[int(izraz.koga.sadržaj)+1]
    


class Inkrement(AST('broj')):
    """Postfix inkrement, vraća inkrementirani broj"""
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        
        vrijednosti[izraz.broj][0] = lijevi[0] + 1
        return lijevi[0] + 1
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)

class Dekrement(AST('broj')):
    """Postfix dekrement, vraća dekrementirani broj"""
    def vrijednost(izraz, imena, vrijednosti):
        lijevi = izraz.broj.vrijednost(imena, vrijednosti)
        vrijednosti[izraz.broj][0] = lijevi[0] - 1
        return lijevi[0] - 1
    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)
        
class Alociraj(AST('tip')):
    def vrijednost(izraz, imena, vrijednosti):
        if izraz.tip ** Tokeni.INT:
            return [[0]]
        elif izraz.tip ** Tokeni.CHAR:
            return [['\0']]
        elif izraz.tip ** Tokeni.STRING:
            return [[""]]
        elif izraz.tip ** Tokeni.BOOL:
            return [[False]]
        elif izraz.tip ** Tokeni.POINTER:
            return [[0]]
        else: raise SintaksnaGreška("Nepoznat tip!")

class AlocirajArray(AST('tip koliko')):
    # nema polja pointera
    def vrijednost(izraz, imena, vrijednosti):
        temp_list =[int(izraz.koliko.sadržaj)]

        if izraz.tip ** Tokeni.INT:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([0])
        elif izraz.tip ** Tokeni.CHAR:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append(['\0'])
        elif izraz.tip ** Tokeni.STRING:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([""])
        elif izraz.tip ** Tokeni.BOOL:
            for i in range(int(izraz.koliko.sadržaj)): temp_list.append([False])
        #elif izraz.tip ** Tokeni.POINTER:
        #    return [[[0]]*izraz.koliko]
        else: raise SintaksnaGreška("Nepoznat tip!")

        return temp_list
