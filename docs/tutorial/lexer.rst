Leksička analiza
================

Program (izvorni kod) nam je najčešće zadan kao string, dakle niz
znakova Unikoda. Prvo što trebamo učiniti s njime je prepoznati osnovne
podnizove koji predstavljaju podlogu za dalju obradu. Ti podnizovi
tvore *tokene*. Iako može biti beskonačno mnogo tokena (npr. u mnogim
programskim jezicima, svako legalno ime varijable je mogući token),
ključno je da se svi oni razvrstavaju u konačno mnogo *tipova*.

Tipovi tokena su ono što zapravo upravlja kasnijom fazom sintaksne
analize programa. To znači da, idealno, u sintaksnoj analizi ne bi
smjelo biti bitno koji je točno niz znakova na određenom mjestu u
programu (to zovemo *sadržaj* tokena), već samo njegov tip. Odnosno,
ako je program sintaksno ispravan, ostat će takav i ako bilo koji token
u njemu zamijenimo tokenom drugog sadržaja a istog tipa (recimo, broj
``3`` zamijenimo brojem ``58``, ili ime varijable ``xy`` zamijenimo imenom ``t``).

Pored tipa i sadržaja, tokeni prepoznati u izvornom kodu imaju brojne metapodatke koji kazuju gdje token počinje (u kojem retku odnosno stupcu izvornog koda), gdje završava, je li uspješno obrađen od strane sintaksnog analizatora itd. No svaki token mora imati tip i sadržaj, koji su na tokenu ``t`` dostupni kao ``t.tip`` i ``t.sadržaj``.

Tipovi tokena
-------------

Da bismo započeli leksičku analizu, moramo definirati enumeraciju --- klasu koja nabraja sve moguće tipove tokena. U vepru postoji bazna klasa ``TipoviTokena`` nasljeđivanjem od koje dobijemo svu potrebnu funkcionalnost. Evo primjera::

        from vepar import *
        
        class T(TipoviTokena):
            PLUS = '+'
            MINUS, PUTA, KROZ = '-*/'
            STRELICA, RAZLIČITO = '->', '!='
            class BROJ(Token):
                def vrijednost(t): return int(t.sadržaj)
            class I(Token):
                literal = 'i'
                def vrijednost(t): return 1j
            class IME(Token): pass

Upravo navedeni primjer pokazuje nekoliko mogućnosti za definiranje tokena, od jednostavnijih prema složenijima.

* obične inertne tokene koji uvijek (ili gotovo uvijek) imaju isti sadržaj (*literale*) definiramo navođenjem tipa lijevo od ``=`` i sadržaja desno. Dakle, token tipa ``T.PLUS`` ima podrazumijevani sadržaj ``'+'``.
* više literala možemo definirati koristeći Pythonovo ugrađeno raspakiravanje stringova (za jednoznakovne tokene) i slogova (za višeznakovne). Dakle, token tipa ``T.PUTA`` ima podrazumijevani sadržaj ``'*'``, a token tipa ``T.RAZLIČITO`` ima podrazumijevani sadržaj ``'!='``.
* tokene koji nisu inertni (imaju metode koje sudjeluju u semantičkoj analizi) definiramo kao unutarnje klase koje nasljeđuju klasu ``Token``. Tako ``T.BROJ`` nema podrazumijevani sadržaj, ali jednom kad ga prepoznamo i podvrgnemo semantičkoj analizi, moći ćemo iz njegovog sadržaja dobiti njegovu *vrijednost* kao Pythonov ``int``.
* ako želimo neinertni literal (ima metode za semantičku analizu, a također ima konstantni sadržaj), možemo takvoj unutarnjoj klasi dati atribut ``literal``. Tako se za potrebe prepoznavanja ``T.I`` ponaša kao da je definiran s ``I = 'i'``, a u semantičkoj analizi za bilo koji token ``t`` tipa ``T.I`` možemo pozvati ``t.vrijednost()`` i dobiti Pythonov kompleksni broj ``1j`` (imaginarnu jedinicu).
* u suprotnom smjeru, ako želimo inertni token bez podrazumijevanog sadržaja, možemo jednostavno definirati unutarnju klasu s ``pass`` (ili ``...`` ako želimo signalizirati da je situacija privremena i da ćemo kasnije možda dodati neku semantiku za taj tip tokena).

Lexer
-----

*Lexer* je funkcija (*generator* u Pythonu) koja prolazi kroz ulazni
string i redom daje (``yield``) tokene koje u njemu prepoznaje. Vepar zahtijeva da bude dekorirana
s ``@lexer``. Jedini argument joj se obično zove ``lex``, i predstavlja objekt klase ``Tokenizer`` čije metode pomažu pri leksičkoj analizi. Ovdje navodimo samo najčešće načine korištenja ``lex``\ a --- za potpunije informacije pogledajte dokumentaciju (recimo pomoću ``help(Tokenizer)``).

Lexer najčešće počinje linijom poput ``for znak in lex:``, dakle sastoji se od petlje koja u svakom prolazu varijabli ``znak`` pridružuje sljedeći znak ulaza. Nakon toga obično slijedi grananje s obzirom na to koji odnosno kakav znak smo našli. To utvrđujemo najčešće običnom usporedbom poput ``znak == '$'`` ili pozivom metode klase ``str`` poput ``znak.islower()`` (što se može zapisati i kao ``str.islower(znak)``). Često korištene metode ovdje su:

``str.isspace``
        Je li znak bjelina, poput razmaka, tabulatora, prelaska u novi red i sličnog.
``str.isalpha``
        Je li znak slovo, poput ``A``, ``č``, ``ǉ``, ili ``是``. Ako želite samo ASCII-slova, provjerite ``znak in string.ascii_letters``, ali najčešće za tim nema potrebe. Trudite se biti inkluzivni!
``str.isdecimal``
        Je li znak znamenka u dekadskom sustavu. Opet, za ASCII-znamenke možete pitati ``znak in string.digits``.

Mnoge ``lex``\ ove metode primaju argument imena ``uvjet``. On može biti pojedini znak koji se traži, metoda oblika ``str.is...`` poput ovih upravo navedenih, bilo koja funkcija (možete je i sami napisati, bilo preko ``def`` ili ``lambda``) koja prima znak i vraća ``bool``; ili pak skup takvih, interpretiran kao disjunkcija. Recimo, ``{str.islower, str.isdecimal, '_', '$'}`` znači "ili malo slovo, ili dekadska znamenka, ili donja crta, ili znak dolara".

Metode lexera
-------------

Raznim metodama možemo unutar jednog prolaza pročitati i više znakova. Ovdje su neke.

``lex.zvijezda(uvjet)``, skraćeno ``lex * uvjet``
        čita nula ili više znakova (od trenutne pozicije) koji ispunjavaju uvjet
``lex.plus(uvjet)``, skraćeno ``lex + uvjet``
        čita jedan ili više znakova (od trenutne pozicije) koji ispunjavaju uvjet; prijavljuje grešku ako takvih nema
``lex.pročitaj_do(uvjet, *, uključivo=True, više_redova=False)``, skraćeno ``lex - uvjet`` ili ``lex <= uvjet``, ili pak ``lex < uvjet`` za ``uključivo=False``
        čita znakove dok ne naiđe na prvi znak koji ispunjava uvjet, prijavljuje grešku ako takvog nema; ``uključivo`` kazuje hoće li pročitati i taj znak, a ``više_redova`` hoće li tražiti znak i u kasnijim recima a ne samo u trenutnom
``lex.prirodni_broj(znak, nula=True)``
        čita prirodni broj (niz znamenaka bez vodećih nulâ) s početkom ``znak`` (najčešće znamo da dolazi prirodni broj tek kad vidimo prvu njegovu znamenku, ali ne uvijek --- tada možemo za prvi argument staviti ``''``); ``nula`` kazuje dozvoljavamo li čitanje ``0`` kao prirodnog broja

Također, razne metode su nam na raspolaganju ako želimo pročitati samo jedan znak.

``lex.čitaj()``, skraćeno ``next(lex)``
        čita i vraća sljedeći znak bez ikakve provjere; na kraju ulaza vraća ``''``
``lex.vidi(uvjet)``, skraćeno ``lex > uvjet``
        ispituje ispunjava li znak, koji bi sljedeći bio pročitan, uvjet
``lex.nužno(uvjet)``, skraćeno ``lex >> uvjet``
        čita sljedeći znak ako ispunjava uvjet, inače prijavljuje grešku
``lex.slijedi(uvjet)``, skraćeno ``lex >= uvjet``
        čita sljedeći znak ako i samo ako ispunjava uvjet; pokrata za ``if lex > uvjet: lex >> uvjet``.

----

Kad zaključimo da smo pročitali dovoljno znakova (što smo pročitali od zadnjeg stvorenog tokena možemo vidjeti u ``lex.sadržaj``), vrijeme je da od njih konstruiramo neki token. Na raspolaganju nam je nekoliko metoda.

``yield lex.token(T.TIP)``
        stvara i šalje dalje token tipa ``T.TIP`` i sadržaja ``lex.sadržaj``
``yield lex.literal(T, *, case=True)``
        stvara i šalje dalje literal onog tipa koji ima odgovarajući (pročitani) sadržaj; recimo ako je ``lex.sadržaj == '->'``, uz gore definirani ``T``, to bi odaslalo ``Token(T.STRELICA, '->')`` (skraćeno ``T.STRELICA'->'``); ako takvog nema prijavljuje grešku; ``case`` govori traži li sadržaj uzimajući u obzir razliku velikih i malih slova
``yield lex.literal_ili(T.DEFAULT)``
        kao ``lex.literal``, osim što ako takvog literala nema, vraća token tipa ``T.DEFAULT``
``lex.zanemari()``
        resetira ``lex.sadržaj``; možemo zamisliti da konstruira neki token, i uništi ga umjesto da ga pošalje dalje; česta linija u lexeru je ``if znak.isspace(): lex.zanemari()``, čime zanemarujemo bjeline u izvornom kodu (ali nam i dalje služe za razdvajanje tokena).

Ako želimo sami prijaviti grešku, to možemo učiniti pomoću ``raise lex.greška(poruka)`` (ne moramo navesti poruku ako vepar ima dovoljno podataka za konstrukciju dovoljno dobre poruke).

Primjer
-------

Jednom kad smo napisali lexer i dekorirali ga s ``@lexer``, možemo ga pozvati s nekim stringom da vidimo kako funkcionira i eventualno ispravimo greške. Evo jednog primjera s obzirom na gornji ``T``::

        @lexer
        def moj(lex):
            for znak in lex:
                if znak == '-':
                    if lex >= '>': yield lex.token(T.STRELICA)
                    else: yield lex.token(T.MINUS)
                elif znak == '!':
                    lex >> '='
                    yield lex.token(T.RAZLIČITO)
                elif znak.isdecimal():
                    lex.prirodni_broj(znak, nula=False)
                    yield lex.token(T.BROJ)
                else: yield lex.literal(T)

        >>> moj('-+->ii!=234/')

.. code-block:: text

        Tokenizacija: -+->ii!=234/
                        Znak #1        : MINUS'-'
                        Znak #2        : PLUS'+'
                        Znakovi #3–#4  : STRELICA'->'
                        Znak #5        : I'i'
                        Znak #6        : I'i'
                        Znakovi #7–#8  : RAZLIČITO'!='
                        Znakovi #9–#11 : BROJ'234'
                        Znak #12       : KROZ'/'
