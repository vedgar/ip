from collections import ChainMap
from ASTs import *

class C0Parser(Parser):

    def prog(self):
        if self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR, Tokeni.VOID}:
            tip = self.zadnji
            ime = self.pročitaj(Tokeni.IDENTIFIER)
            self.pročitaj(Tokeni.OOTV)

            varijable = []
            while not self >> Tokeni.OZATV:
                if (not self >> {Tokeni.INT, Tokeni.BOOL, Tokeni.STRING, Tokeni.CHAR}):
                    raise SintaksnaGreška("pogrešna inicijalizacija")

                tipVar = self.zadnji
                imeVar = self.pročitaj(Tokeni.IDENTIFIER)
                if (not self.pogledaj() ** Tokeni.OZATV):
                    self.pročitaj(Tokeni.ZAREZ)
                
                varijable.append(Varijabla(tipVar, imeVar))

            if (self.pogledaj() ** Tokeni.SEP): #samo deklaracija funkcije
                self.pročitaj(Tokeni.SEP)
                return DeklaracijaFunkcije(tip, ime, varijable)

            self.pročitaj(Tokeni.VOTV)
            tijelo = []
            while not self >> Tokeni.VZATV: tijelo.append(self.stmt())
            return DefinicijaFunkcije(tip, ime, varijable, tijelo)

    def stmt(self):
        if self >> Tokeni.IF:
            self.pročitaj(Tokeni.OOTV)
            uvjet = self.expression()
            self.pročitaj(Tokeni.OZATV)
            tijeloIf = self.stmt()
            idući = self.pogledaj()
            if idući ** Tokeni.ELSE:
                self.pročitaj(Tokeni.ELSE)
                tijeloElse = self.stmt()
                return IfElse(uvjet, tijeloIf, tijeloElse)
            else:
                return If(uvjet, tijeloIf)
        if self >> Tokeni.WHILE:
            self.pročitaj(Tokeni.OOTV)
            uvjet = self.expression()
            self.pročitaj(Tokeni.OZATV)
            tijeloWhile = self.stmt()
            return While(uvjet, tijeloWhile)

        if self >> Tokeni.FOR:
            self.pročitaj(Tokeni.OOTV)
            deklaracija = ""
            if (not self.pogledaj() ** Tokeni.SEP):
                deklaracija = self.simple()
            self.pročitaj(Tokeni.SEP)
            uvjet = self.expression()
            self.pročitaj(Tokeni.SEP)
            
            inkrement = ""
            if (not self.pogledaj() ** Tokeni.OZATV):
                inkrement = self.simple()
 
            self.pročitaj(Tokeni.OZATV)
            tijeloFor = self.stmt()
            return For(deklaracija, uvjet, inkrement, tijeloFor)

        if self >> Tokeni.RETURN:
            povratnaVrijednost = ""
            if (not self.pogledaj() ** Tokeni.SEP):
                povratnaVrijednost = self.expression()
            self.pročitaj(Tokeni.SEP)
            return Return(povratnaVrijednost)
        if self >> Tokeni.BREAK:
            br = self.zadnji
            self.pročitaj(Tokeni.SEP)
            return br
        if self >> Tokeni.CONTINUE:
            con = self.zadnji
            self.pročitaj(Tokeni.SEP)
            return con
        if self >> Tokeni.ASSERT:
            self.pročitaj(Tokeni.OOTV)
            izraz = self.expression()
            self.pročitaj(Tokeni.OZATV)
            self.pročitaj(Tokeni.SEP)
            return Assert(izraz)

        if self >> Tokeni.ERROR:
            self.pročitaj(Tokeni.OOTV)
            izraz = self.expression()
            self.pročitaj(Tokeni.OZATV)
            self.pročitaj(Tokeni.SEP)
            return Error(izraz)

        if self >> Tokeni.VOTV:
            blok = []
            while not self >> Tokeni.VZATV: blok.append(self.stmt())
            return Blok(blok)
        else:
            simple = self.simple()
            self.pročitaj(Tokeni.SEP)
            return simple

    def simple(self): 
        if self >> primitivniTipovi:
            tip = self.zadnji
            varijabla = self.pročitaj(Tokeni.IDENTIFIER)
            if self >> Tokeni.ASSIGN:
                var = Varijabla(tip, varijabla)
                desna = self.expression()
                return Deklaracija(var, desna)
            else:
                return Varijabla(tip, varijabla)
        else:
            return self.expression()

    def expression(self):
        trenutni = self.logički()

        while True:
            if self >> Tokeni.CONDQ:
                prviUvjet = self.expression()
                self.pročitaj(Tokeni.CONDDOT)
                drugiUvjet = self.expression()
                trenutni = TernarniOperator(trenutni, prviUvjet, drugiUvjet)
            else: return trenutni

        else:
            self.greška()

    def logički(self):
        trenutni = self.bitwise()
        while True:
            if self >> {Tokeni.LAND, Tokeni.LOR}:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.bitwise(), operacija)
            else: return trenutni

    def bitwise(self):
        trenutni = self.equality()
        while True:
            if self >> {Tokeni.BITAND, Tokeni.BITEXCLOR, Tokeni.BITOR}:
                operacija = self.zadnji
                trenutni = BitwiseOperacija(trenutni, self.equality(), operacija)
            else: return trenutni

    def equality(self):
        trenutni = self.comparison()
        while True:
            if self >> {Tokeni.EQ, Tokeni.DISEQ}:
                operacija = self.zadnji
                trenutni = Equality(trenutni, self.comparison(), operacija)
            else: return trenutni

    def comparison(self):
        trenutni = self.shifts()
        while True:
            if self >> {Tokeni.LESS, Tokeni.LESSEQ, Tokeni.GRT, Tokeni.GRTEQ}:
                operacija = self.zadnji
                trenutni = Comparison(trenutni, self.shifts(), operacija)
            else: return trenutni

    def shifts(self):
        trenutni = self.add()
        while True:
            if self >> {Tokeni.LSHIFT, Tokeni.RSHIFT}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.add(), operacija)
            else: return trenutni

    def add(self):
        trenutni = self.factor()
        while True:
            if self >> {Tokeni.PLUS, Tokeni.MINUS}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.factor(), operacija)
            else: return trenutni

    def factor(self):
        trenutni = self.assign()
        while True:
            if self >> {Tokeni.ZVJ, Tokeni.SLASH, Tokeni.MOD}:
                operacija = self.zadnji
                trenutni = BinarnaOperacija(trenutni, self.assign(), operacija)
                
            else: return trenutni
    def assign(self):
        trenutni = self.allocate()

        while True:
            if self >> assignOperators:
                operacija = self.zadnji
                trenutni = Assignment(trenutni, self.expression(), operacija)
            else: break
        
        return trenutni
    
    def allocate(self):
        trenutni = self.allocarray()
        if self >> Tokeni.ALLOC:
            self.pročitaj(Tokeni.OOTV)
            if self >> primitivniTipovi:
                tip = self.zadnji
                self.pročitaj(Tokeni.OZATV)
                trenutni = Alociraj(tip) 
            else:
               self.zadnji.neočekivan()
              
        return trenutni         

    def allocarray(self):
        trenutni = self.unaries()
        if self >> Tokeni.ALLOCA:
            self.pročitaj(Tokeni.OOTV)
            if self >> primitivniTipovi:
                tip = self.zadnji
                self.pročitaj(Tokeni.ZAREZ)
                koliko = self.expression()
                self.pročitaj(Tokeni.OZATV)
                trenutni = AlocirajArray(tip, koliko)
            else:
                self.zadnji.neočekivan()
        return trenutni

    def unaries(self):
        if self >> Tokeni.USKL:
            iza = self.expression()
            return Negacija(iza)
        if self >> Tokeni.TILDA:
            iza = self.expression()
            return Tilda(iza)
        if self >> Tokeni.MINUS:
            iza = self.expression()
            return Minus(iza)
        if self >> Tokeni.ZVJ:
            iza = self.base()
            trenutni = Dereferenciraj(iza)
            return trenutni        
        
        baza = self.base()
        return baza

    def base(self):
        if self >> Tokeni.OOTV:
            u_zagradi = self.expression()
            self.pročitaj(Tokeni.OZATV)
            return u_zagradi
        if self >> Tokeni.IDENTIFIER:
            #može biti identifier, može biti poziv funkcije ako slijedi otvorena zagrada iza
            ime = self.zadnji
            if (self.pogledaj() ** Tokeni.OOTV):
                self.pročitaj(Tokeni.OOTV)
                varijable = []
                while not self >> Tokeni.OZATV:
                    imeVar = self.expression()
                    if (not self.pogledaj() ** Tokeni.OZATV):
                        self.pročitaj(Tokeni.ZAREZ)
                    varijable.append(imeVar)
                return IzvrijedniFunkciju(ime, varijable)
            
            if (self.pogledaj() ** Tokeni.INCR or self.pogledaj() ** Tokeni.DECR):
                trenutni = self.zadnji
                while True:
                    if self >> Tokeni.INCR:
                        trenutni = Inkrement(ime)
                    elif self >> Tokeni.DECR:
                        trenutni = Dekrement(ime)
                    else: 
                        break
                return trenutni

            if self >> Tokeni.UOTV:
                trenutni = self.expression()
                self.pročitaj(Tokeni.UZATV)
                trenutni = Dohvati(ime, trenutni)
                return trenutni

            else:
                return ime
        if self >> Tokeni.PRINT:
            #print funkcija
            self.pročitaj(Tokeni.OOTV)
            varijable = []
            while not self >> Tokeni.OZATV:
                imeVar = self.expression()
                if (not self.pogledaj() ** Tokeni.OZATV):
                    self.pročitaj(Tokeni.ZAREZ)
                
                varijable.append(imeVar)
            return PrintFunkcija(varijable)
        if self >> osnovniIzrazi:
            trenutni = self.zadnji
            return trenutni

    def start(self):
        naredbe = [self.prog()]
        while not self >> E.KRAJ:
            naredbe.append(self.prog())
        return Program(naredbe)