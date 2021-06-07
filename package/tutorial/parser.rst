Sintaksna analiza
=================

Naš program (niz znakova) pretvorili smo u niz tokena --- sada je vrijeme da taj niz obogatimo dodatnom strukturom. Nizovi su linearni, a nama trebaju grafovi u više dimenzija, koji predstavljaju kako se tokeni slažu u semantički smislene cjeline. U ogromnom broju slučajeva ti grafovi su zapravo stabla, i zovu se apstraktna sintaksna stabla (AST).

U nizu tokena ``BROJ'5'`` ``PLUS'+'`` ``BROJ'12'`` dobivenom leksičkom analizom ``5+12``, tokeni nisu ravnopravni: u izvjesnom smislu ovaj ``PLUS`` je "iznad", predstavlja *vrstu* izraza s kojom radimo (zbroj), a ``BROJ``\ evi su samo operandi, koji dolaze u igru tek nakon što znamo o kojoj vrsti izraza se radi. Čak njihov sintaksni identitet može ovisiti o onom što se očekuje na danom mjestu: recimo, u programskom jeziku C, nakon ``if`` i otvorene zagrade dolazi uvjet, a onda nakon zatvorene dolazi naredba. Svaki uvjet je ujedno i naredba, ali ne i obrnuto. Dakle, na najvišoj razini možemo reći "aha, radi se o ``if``-naredbi, ``IF`` ``OTV`` ``uvjet`` ``ZATV`` ``naredba``", a onda ``uvjet`` i ``naredba`` predstavljaju dijelove koji se na nižim razinama popunjavaju tokenima koji se nalaze između odgovarajućih mjesta. Recimo, ``if(i==3)break;`` bi se moglo prikazati kao

.. code-block:: text

        Ako:                   @[Znakovi #1–#13]
          uvjet = Jednakost:   @[Znakovi #4–#7]
            lijevo = IME'i'    @[Znak #4]
            desno = BROJ'3'    @[Znak #7]
          onda = BREAK'break'  @[Znakovi #9–#13]

Ta ideja razina odnosno slaganja tokena u stabla, ključna je za sintaksnu analizu. Uglavnom ćemo dalje raditi s aritmetičkim izrazima jer su nam bliski, ali sve se može primijeniti na sintaksnu analizu brojnih formalnih jezika.

Beskontekstne gramatike
-----------------------

Formalizam koji nam omogućuje koncizno zapisivanje sintaksne strukture našeg jezika zove se *beskontekstna gramatika* (skraćeno BKG, engleski *context-free grammar*). BKG se sastoji od jednog ili više pravila oblika ``varijabla -> riječ``, gdje je ``riječ`` konačni niz varijabli i tipova tokena. Pravilo predstavlja jednu moguću realizaciju niza tokena koji pripada jeziku određenom tom varijablom (kažemo da varijabla *izvodi* niz tokena). Više pravila za istu varijablu često se piše u skraćenom obliku kao ``varijabla -> riječ1 | riječ2``. 

Recimo, ako hoćemo reprezentirati zbrojeve jednog do tri broja, mogli bismo napisati gramatiku s 3 pravila

.. code-block:: text

        # zbroj -> BROJ | BROJ PLUS BROJ | BROJ PLUS BROJ PLUS BROJ

--- ali što ako hoćemo proizvoljno mnogo pribrojnika? U tom slučaju možemo koristiti rekurzivno pravilo

.. code-block:: text

        # zbroj -> BROJ | BROJ PLUS zbroj

samo, naravno, moramo paziti da uvijek imamo i pravilo koje završava rekurziju.

Što se samog vepra tiče, ne moramo pisati BKG (u Pythonu pravila pišemo u komentare), ali iskustvo pokazuje da je tako puno lakše napisati sintaksni analizator (parser).

Razine prioriteta
-----------------

Pribrojnici u ``zbroj``\ u ne moraju biti ``BROJ``\ evi. Recimo, za ulazni string ``5+8*12`` dobijemo niz tokena ``BROJ'5'`` ``PLUS'+'`` ``BROJ'8'`` ``PUTA'*'`` ``BROJ'12'``, te znamo (na osnovi dogovora o prioritetu operacija) da predstavlja zbroj broja ``5`` i umnoška brojeva ``8`` i ``12``. (Također predstavlja i broj ``101``, ali o tome tek u sljedećoj fazi.) Dakle, cilj nam je proizvesti nešto poput ``Zbroj(lijevo=BROJ'5', desno=Umnožak(lijevo=BROJ'8', desno=BROJ'12'))``, ili, kako to vepar zna "stabloliko" prikazati:

.. code-block:: text

        Zbroj:                @[Znakovi #1–#6]
          prvi = BROJ'5'      @[Znak #1]
          drugi = Umnožak:    @[Znakovi #3–#6]
            prvi = BROJ'8'    @[Znak #3]
            drugi = BROJ'12'  @[Znakovi #5–#6]

Da bismo to zapisali u našoj BKG, moramo uvesti još jednu varijablu. U tom kontekstu ona se obično zove "član" (*term*), jer nam se ne da pisati "pribrojnik" zbog duljine.

.. code-block:: text

        # izraz -> član | član PLUS izraz
        # član -> BROJ | BROJ PUTA član

Vidimo da smo preimenovali i početnu varijablu iz ``zbroj`` u ``izraz``. Vepru nije previše bitno: ako postoji varijabla imena ``start``, od nje kreće sintaksna analiza, a ako ne, kreće od prve varijable.

Sada je jasno kako bismo dodali još razina prioriteta: možete za vježbu dodati potenciranje. No što je sa zagradama? One nam omogućavaju da u član umjesto ``BROJ``\ a utrpamo cijeli izraz, samo ga moramo staviti u zagrade. Dakle

.. code-block:: text

        # izraz -> član | član PLUS izraz
        # član -> faktor | faktor PUTA član
        # faktor -> BROJ | OTV izraz ZATV

Parser
------

Ovo je već dovoljno komplicirana BKG da je zanimljivo vidjeti kako bi izgledao parser za nju. Parser pišemo kao potklasu veprove klase ``Parser``, čije metode (uglavnom) odgovaraju varijablama gramatike. Svaka metoda prima instancu parsera koja se uobičajeno zove ``p``, ali nitko vam ne brani da pišete tradicionalno ``self`` ili kakvo god ime želite.

Parser ima slično sučelje kao lexer, što se tiče "konzumiranja" tokena:

``p.vidi(T.TIP)``, skraćeno ``p > T.TIP``
        ako bi sljedeći pročitani token bio tipa ``T.TIP``, vraća ga (ali ne čita), inače vraća ``nenavedeno``
``p.nužno(T.TIP)``, skraćeno ``p >> T.TIP``
        čita sljedeći token koji mora biti tipa ``T.TIP``, i vraća ga; inače prijavljuje grešku
``p.slijedi(T.TIP)``, skraćeno ``p >= T.TIP``
        čita sljedeći token (i vraća ga) ako i samo ako je tipa ``T.TIP``; inače vraća ``nenavedeno``.

Umjesto ``T.TIP`` može stajati i skup tipova tokena, koji se shvaća kao disjunkcija.

Za razliku od lexera, gdje možemo čitati bilo kakve znakove (npr. s ``next``) pa ih poslije zgurati nekamo kao dio ``lex.sadržaj``\ a, parser mora svaki token *razriješiti* jednom od gornjih metoda; inače ćemo dobiti sintaksnu grešku. Nju možemo i sami prijaviti pomoću ``raise p.greška(poruka)``; kao i za leksičku grešku, poruku ne moramo navesti ako smo zadovoljni veprovom konstrukcijom poruke. Također, grešku ćemo dobiti ako stanemo prije kraja (jer, opet, nismo razriješili sve tokene); možemo zamisliti da nakon svih lexerovih tokena postoji još jedan token tipa ``KRAJ``, koji ne smijemo pročitati (pročitat će ga vepar na kraju parsiranja) ali ga možemo koristiti (operatorom ``>``) za upravljanje sintaksnom analizom: recimo, ``while not p > KRAJ:``.

Objekt ``nenavedeno`` je specijalni singleton koji predstavlja odsustvo tokena u ASTu (iz tehničkih razloga ne koristi se Pythonov ``None``). Važno je da je lažan (dok su svi tokeni istiniti) pa se može koristiti za grananje potpuno jednako kao ``None``.

Primjer
-------

Na primjer, zadnji red u našoj BKG može se kodirati kao ::

                def faktor(p):
                    if p >= T.OTV:
                        u_zagradi = p.izraz()
                        p >> T.ZATV
                        return u_zagradi
                    else: return p >> T.BROJ

Pomoću "morž-operatora" ``:=`` možemo određene rezultate gornjih metoda iskoristiti za grananje, a ujedno ih i zapamtiti za kasnije vraćanje. Recimo, ako iz nekog razloga želimo zamijeniti grane u upravo napisanoj metodi, imat ćemo ::

                def faktor(p):
                    if broj := p >= T.BROJ: return broj
                    p >> T.OTV
                    u_zagradi = p.izraz()
                    p >> T.ZATV
                    return u_zagradi

Sve je to lijepo ako sve mogućnosti za neku varijablu počinju različitim tokenima: tako smo odmah znali koje pravilo za faktor trebamo slijediti ovisno o tome jesmo li započeli faktor tokenom tipa ``T.OTV`` ili tokenom tipa ``T.BROJ``. (Ponekad je potrebno gledati više od jednog tokena unaprijed, ali vepar to ne podržava jednostavno; prvenstveno jer vodi do jezika koji su i ljudima teški za razumijevanje. Stručnim rječnikom, veprovo parsiranje je **LL(1)**.) No kako napisati metodu ``izraz``? Imamo dvije mogućnosti, i obje počinju ``član``\ om. U tom slučaju možemo *faktorizirati*, odnosno "izlučiti" ``član`` slijeva. Drugim riječima, možemo sigurno pročitati ``član``, i onda donijeti odluku što dalje ovisno o tome slijedi li ``PLUS`` ili ne. ::

        def izraz(p):
            prvi = p.član()
            if p >= T.PLUS:
                drugi = p.izraz()
                return Zbroj(prvi, drugi)
            else: return prvi

Sasvim je isto za ``član``: napišite sami za vježbu. Sada od te tri metode možemo sklopiti klasu: važno je da metoda ``izraz`` bude prva, kako bi vepar znao da od nje počinje. Alternativno, mogli bismo je preimenovati u ``start``, ali vjerojatno je svejedno dobro da bude prva. ::

        class P(Parser):
            def izraz(p): ...   # prepišite odozgo
            def član(p): ...    # napišite sami po uzoru na izraz
            def faktor(p): ...  # prepišite jednu od varijanti odozgo

Da bismo mogli doista pokrenuti parser, trebamo još implementirati ASTove ``Zbroj`` i ``Umnožak``. Zapravo, dovoljno je samo navesti atribute, a metode i anotacije možemo dodati kasnije. ::

        class Zbroj(AST):
            lijevo: ...
            desno: ...

        class Umnožak(Zbroj): pass

Trebali bismo svaku klasu koja predstavlja AST naslijediti od klase ``AST``, ali zapravo, s obzirom na to da imaju iste atribute, možemo jednu naslijediti od druge. Sada napokon možemo vidjeti 1D i 2D prikaz našeg stabla:

.. code-block:: text

        >>> P('5+8*12')
        Zbroj(prvi=BROJ'5', drugi=Umnožak(prvi=BROJ'8', drugi=BROJ'12'))

        >>> prikaz(_)
        Zbroj:  @[Znakovi #1–#6]
          prvi = BROJ'5'  @[Znak #1]
          drugi = Umnožak:  @[Znakovi #3–#6]
            prvi = BROJ'8'  @[Znak #3]
            drugi = BROJ'12'  @[Znakovi #5–#6]

Iterativno parsiranje
---------------------

Dosad korišteni (rekurzivni) način pisanja parsera je izuzetno jednostavan (samo prepisujemo pravila gramatike u Python), ali ne radi uvijek, a i kada radi, ponekad ne daje intuitivne rezultate.

Lako je vidjeti (isprobajte) da će upravo napisani parser ``2+3+4``
parsirati na isti način kao ``2+(3+4)`` (kažemo da je ``PLUS`` *desno
asociran*), a ne na isti način kao ``(2+3)+4``. U ovom slučaju nije
toliko bitno jer je zbrajanje asocijativna operacija pa će rezultat
biti isti, ali to ne odgovara baš onome kako smo učili u školi (da
je zbrajanje *lijevo asocirano*); i naravno, imali bismo problema pri
uvođenju oduzimanja, jer ``6-3-2`` nije isto što i ``6-(3-2)`` čak
ni po vrijednosti. Dakle, moramo naučiti parsirati i lijevo asocirane
operatore.

Na prvi pogled, vrlo je jednostavno: samo umjesto ``član PLUS izraz`` u drugo pravilo za ``izraz`` napišemo ``izraz PLUS član``. Iako matematički sasvim točno, to nam ne pomaže za pisanje parsera, jer bi rekurzivna paradigma koju smo dosad koristili zahtijevala da unutar metode ``izraz`` prvo pozovemo metodu ``izraz``, što bi naravno dovelo do rušenja zbog beskonačne rekurzije. Taj fenomen se u teoriji parsiranja zove *lijeva rekurzija* (*left recursion*).

Možemo li bez rekurzije parsirati to? Sjetimo se gramatičkih sustava. Po lemi o fiksnoj točki (lijevolinearno), rješenje od ``izraz = izraz PLUS član | član`` je ``izraz = član (PLUS član)*``. Drugim riječima, samo trebamo pročitati ``član``, i onda nakon toga nula ili više puta (u neograničenoj petlji) čitati ``PLUS`` i ``član`` sve dok možemo. ::
        
        def izraz(p):
            stablo = p.član()
            while p > T.PLUS:
                p >> T.PLUS
                novi = p.član()
                stablo = Zbroj(stablo, novi)
            return stablo

Naravno, koristeći ``>=``, cijela petlja se u jednoj liniji može zapisati kao::

            while p >= T.PLUS: stablo = Zbroj(stablo, p.član())

Asociranost
-----------

Potrebno je neko vrijeme da se priviknete na takav način pisanja, ali jednom kad uspijete, vidjet ćete da istu tehniku možete primijeniti na mnogo mjesta. Na primjer, iterativno možete parsirati i *višemjesne* (asocijativne) operatore --- gdje ne želite stablo povećavati u dubinu nego u širinu, držeći sve operande kao neposrednu djecu osnovnog operatora (npr. u listi). ::

        def izraz(p):
            pribrojnici = [p.član()]
            while p >= T.PLUS: pribrojnici.append(p.član())
            return Zbroj(pribrojnici)

Zadnji napisani kod ima jedan problem: uvijek vraća ``Zbroj``, čak i kad nikakvog zbrajanja nema (onda će lista biti duljine 1). Da to izbjegnete, možete koristiti alternativni konstruktor ASTova, ``return Zbroj.ili_samo(pribrojnici)``. Način na koji to radi je ono što biste očekivali: ako ``A`` ima točno jedan atribut, i njegova vrijednost je lista s jednim elementom ``[w]``, tada ``A.ili_samo([w])`` umjesto ``A([w])`` vraća ``w``.

Jednostavnom zamjenom ``while`` s ``if``, možete implementirati i *neasocirane* operatore, koji uopće nemaju rekurzivna pravila: recimo, da smo imali pravilo ``izraz -> član | član PLUS član``, bili bi dozvoljeni samo zbrojevi jednog ili dva pribrojnika, i za bilo koji veći broj pribrojnika morali bismo eksplicitno koristiti zagrade.

Idealno, svaka metoda parsera bi trebala koristiti samo rekurzivni
ili samo iterativni pristup. Doista, asociranost je svojstvo *razine
prioriteta*, ne pojedinog operatora. Recimo, ako imamo ``+`` i ``-`` na
istoj razini prioriteta kao što je uobičajeno, ne može ``+`` biti desno
a ``-`` lijevo asociran: tada bi ``6-2+3`` bio dvoznačan (mogao bi imati
vrijednost ``1`` ili ``7``), dok ``6+2-3`` ne bi uopće imao značenje.

Drugim riječima, da bismo parsirali ``a$b¤c``, moramo odlučiti "kome ide ``b``". Ako su operatori ``$`` i ``¤`` različitog prioriteta, dohvatit će ga onaj koji je većeg prioriteta. Ali ako su na istoj razini, tada asociranost te razine određuje rezultat: ako je asocirana lijevo, to je ``(a$b)¤c``, a ako je asocirana desno, to je ``a$(b¤c)``.

U istu paradigmu možemo uklopiti i unarne operatore, zamišljajući da su prefiksni operatori "desno asocirani" (rekurzivno parsirani), dok su postfiksni "lijevo asocirani" (iterativno parsirani). I opet, u skladu s upravo navedenim argumentom, ne možemo imati prefiksne i postfiksne operatore na istoj razini prioriteta, jer ne bismo znali kako parsirati ``$b¤`` ("kome ide ``b``").
