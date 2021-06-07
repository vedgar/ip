Semantička analiza
==================

Već smo vidjeli kako deklarirati ASTove u poglavlju o sintaksnoj analizi. Ponovimo: pišemo ih kao potklase veprove klase ``AST``, navodeći odmah ispod toga deklaracije njihovih atributa. Primjer::

        class Petlja(AST):
            uvjet: 'logički_izraz'
            tijelo: 'naredba|Blok'

Anotacije (ovo iza dvotočke u deklaracijama) mogu biti proizvoljne, vepar ih ne čita. Pristojno je napisati ili varijablu gramatike (metodu parsera) koja vraća nešto što može doći na to mjesto, ili tip (klasu) ASTa koji se direktno može tamo staviti. Anotacije treba pisati kao stringove, osim ako ćete jako paziti na poredak tako da ne koristite ništa što već nije definirano. (Možete i ``from __future__ import annotations`` na početku ako ne želite paziti na to.) Kao što rekoh, vepra nije briga što ćete tamo napisati: ``atribut: ...`` je sasvim u redu ako vam se ne da razmišljati, ali slično kao za BKG, pažljiv dizajn ASTova i njegova dokumentacija kroz tipove atributa vrlo je korisna stepenica u uspješnoj implementaciji semantičkog analizatora.

Krenuvši od korijena (to je AST kojeg stvara početna varijabla gramatike) i slijedeći atribute, prije ili kasnije doći ćemo do *listova*, što su najčešće tokeni. Dualno, možemo zamisliti ASTove kao nekakve obrasce u koje parser slaže tokene koje lexer generira, kako bi prikazao sintaksnu strukturu programa. Obilascima ASTova (koristeći najčešće rekurzivne metode) sada možemo učiniti sljedeći korak i našem programu "udahnuti dušu" odnosno dati mu nekakvu semantiku.

S ASTovima možemo raditi praktički što god želimo: pretvarati ih u jednostavnije ili po nekom drugom kriteriju bolje ASTove (optimizacija), preslikavati ih u nekakvu međureprezentaciju, bajtkod ili čak strojni kod (kompilacija), ili ih direktno preslikavati u stvarni svijet efekata i izlaznih vrijednosti (izvršavanje/evaluacija). Ovo je mjesto gdje vepar prestaje biti rigidni *framework* i postaje biblioteka raznih alata za koje se pokazuje da su često korisni u semantičkim analizama mnogih jezika. Događa se inverzija kontrole: dok je pri leksičkoj i sintaksnoj analizi vepar sam po potrebi pozivao lexer i metode parsera, i od njih slagao ASTove, sada ASTovi sami brinu za svoju kontrolu toka, eventualno koristeći veprove strukture i pozivajući njegove pomoćne funkcije tamo gdje je potrebno.

Tako ovdje samo navodimo dobre prakse za neke najčešće obrasce semantičke analize; prostor mogućnosti ovdje je daleko veći nego što se to u ovakvom tutorialu može opisati.

Evaluacija
----------

Metode pišemo na pojedinim ASTovima, pozivajući (iste ili različite) metode na drugim ASTovima koji su najčešće neposredni potomci početnog, sve dok ne dođemo do poziva metode na tokenu u listu ASTa, koja predstavlja bazu rekurzije. Recimo, u klasi ``Zbroj`` mogli bismo napisati metodu ::

        def vrijednost(self):
            return self.lijevo.vrijednost() + self.desno.vrijednost()

i sasvim analogno (napišite sami!) za ``Umnožak``, što bi zajedno s metodom ``vrijednost`` na ``BROJ``\ evima (koju smo napisali u poglavlju o leksičkoj analizi) dalo da napokon možemo dobiti ::

        >>> P('5+8*12').vrijednost()
        101

Prilično analogno, samo bez povratne vrijednosti, možemo *izvršavati* naredbe u programima. Recimo, ``Petlja`` definirana na početku ovog poglavlja mogla bi imati metodu ::

        def izvrši(self):
            while self.uvjet.vrijednost(): self.tijelo.izvrši()

(pod pretpostavkom da sve što metoda parsera ``logički_izraz`` može vratiti ima metodu ``vrijednost`` koja vraća ``bool``, te da svaka ``naredba``, kao i ``Blok``, imaju metodu ``izvrši``). Implementacija bloka naredbi bila bi u tom slučaju ::

        class Blok(AST):
            naredbe: 'naredba*'
            def izvrši(self):
                for naredba in self.naredbe(): naredba.izvrši()

Memorija
--------

Što ako u izrazu imamo varijable? Treba nam (a) neki način da im pridijelimo vrijednost (naredbom pridruživanja, ili prijenosom izvana), (b) način da te vrijednosti učinimo dostupnom svakoj metodi ``vrijednost`` na svim ASTovima i Tokenima, te (c) način da vepru kažemo da prijavi suvislu grešku u slučaju nepostojanja (ili, u nekim slučajevima, redefinicije) tražene varijable.

Za (a) možemo koristiti Pythonov rječnik, ali u tom slučaju je komplicirano riješiti (c) (opet, zbog inverzije kontrole; vepar ne zna ništa o tome što mi radimo s tim rječnikom). Također, nezgodno je uvijek misliti jesu li ključevi u rječniku tokeni ili njihovi sadržaji (ponekad je bolje jedno, ponekad drugo). Sve te (i druge) probleme rješava ``Memorija``. To je klasa čije instance su specijalno prilagođene za praćenje metapodataka (vrijednosti, tipova, ...) raznih tokena, bilo direktno bilo po sadržaju. Pri konstrukciji možemo (a i ne moramo) navesti inicijalne podatke u obliku rječnika, druge memorije, ili čak objekta poput ``zip(imena, vrijednosti)``. Također možemo navesti opciju ``redefinicija=False`` (podrazumijevano je ``True``), čime zabranjujemo *rebinding* (ponovo pridruživanje) tokenima koji već postoje u memoriji. Naravno, ako su metapodaci promjenjivi Pythonovi objekti, možemo ih mijenjati bez obzira što smo tu naveli.

Kako riješiti (b)? *Low-tech* rješenje je jednostavno memoriju, jednom kad je konstruiramo, poslati kao argument u svaki poziv. To je sasvim izvedivo, ali zahtijeva puno mijenjanja (posebno ako se kasnije sjetimo da još nešto trebamo prenijeti na isti način), a i djeluje pomalo šašavo pisati da ``T.BROJ.vrijednost`` prima argument koji uopće ne koristi. Za to možemo koristiti `rt` (od *runtime*), veprov globalni objekt koji u svojim atributima drži sve potrebno za izvršavanje, pa tako i memoriju ako nam je potrebna. Dakle, samo treba negdje pri početku izvršavanja inicijalizirati ``rt.mem = Memorija()``, realizirati nekakvu naredbu pridruživanja poput ::

        class Pridruživanje(AST):
            čemu: 'IME'
            pridruženo: 'izraz'
            def izvrši(self):
                rt.mem[self.čemu] = self.pridruženo.vrijednost()

i klasi ``T.IME`` dodati metodu ::

        def vrijednost(t): return rt.mem[t]

Optimizacija
------------

Jedna konceptualno jednostavna operacija na ASTovima je optimizacija: od jednog ASTa napravimo drugi, najčešće tako da uklonimo neke nepotrebne dijelove. Recimo, uz globalnu definiciju ``nula = Token(T.BROJ, '0')``, mogli bismo u klasi ``Zbroj`` napisati ::

        def optim(self):
            if self.lijevo == nula: return self.desno.optim()
            elif self.desno == nula: return self.lijevo.optim()
            else: return self

ali to **nije dobra** metoda za optimizaciju, jer gleda samo "plitko" izraze do dubine 1: recimo, neće optimizirati ``(0+0)+5``. Bolje je rekurzivno optimizirati prvo potomke, što može otkriti neke obrasce koje možemo iskoristiti na osnovnoj razini::

        def optim(self):
            ol, od = self.lijevo.optim(), self.desno.optim()
            if ol == nula: return od
            elif od == nula: return ol
            else: return Zbroj(ol, od)

Alternativno, možemo i *mijenjati* ASTove direktno, što ima svoje prednosti poput čuvanja podataka o rasponu pojedinih ASTova, ali ima i mane jer je teže pisati rekurzivne funkcije koje mijenjaju svoje argumente. To se obično koristi u složenijim jezicima, gdje inkrementalna kompleksnost takvog postupka nije prevelika, a ogromnu većinu "gornjih slojeva" nećemo mijenjati optimizacijom, pa nema smisla da ih prepisujemo svaki put (tzv. lokalni ili *peephole* optimizatori).
