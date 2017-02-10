# Interpretacija programa

Repozitorij za kod koji ćemo pisati.

## Kolokvij

https://docs.google.com/document/d/1BPhfKM4EWemdv8xsirQBiGM9p08_eaV9iYwv3QASkqw/pub

link za predaju rješenja: http://ted.math.hr (bilo bi dobro da ga testirate i prije kolokvija, svakako prijavite mailom ako ne radi).

Prethodno si lokalno skinite čitav repozitorij, te radite na lokalnoj kopiji. U 15 sati dodat ću još dvije datoteke u repozitorij, Z1.py i Z2.py, koje ćete također trebati skinuti i u njima pisati rješenja. Ostale datoteke se neće mijenjati.

## cheat sheet
KA.py
=====
Kartezijev_produkt: pomoćna funkcija, koristiti kod specificiranja domene i kodomene,
                    te kod Kartezijevih konstrukcija s konačnim automatima

funkcija: pomoćna, služi za provjeravanje da smo doista dobili funkciju sa
          traženom domenom i kodomenom

petorka: služi samo za rastavljanje na pet sastavnih dijelova KA, kad im hoćemo
         pridružiti imena

KonačniAutomat:

  definicija: slaže konačni automat iz pet njegovih "matematičkih" komponenti

  iz_tablice: pomoćna metoda, praktično zadavanje konačnog automata za testove

  ispiši, slučajni_testovi, log, debug: pomoćne, za debugiranje

  prihvaća: metoda koja rješava problem prihvaćanja za konačne automate (Ac_KA)

  provjeri: korisna pomoćna funkcija, za provjeru pridržava li se automat specifikacije

Kartezijeva_konstrukcija_{unija, presjek}: bitno razumjeti kako se matematičke
  konstrukcije pišu u Pythonu

    δ = {}
    for r1, r2 in Q:
       for a in Σ:
          δ[(r1, r2), a] = δ1[r1, a], δ2[r2, a]

    return klasa(stanja=stanja, abeceda=abeceda, prijelaz=prijelaz, ...)

prirodni: pomoćna funkcija, služi za pretvaranje RI u KA

NKA.py:
======

fset: pomoćna klasa, koristiti umjesto set za skupove koji su elementi nekih drugih
      skupova

partitivni_{generator, skup}: pomoćne funkcije za generiranje svih podskupova

relacija: analogno kao funkcija, prima skupove i vraća je li zadani argument relacija
          između tih skupova

kolabiraj, funkcija_iz_relacije, relacija_iz_funkcije: pomoćne za pretvaranje
  između funkcijskog i relacijskog zadavanja NKA

unija_familije: pomoćna za funkciju dolazna

dolazna, ε_zatvorenje: korisne funkcije za jedan nedeterministički prijelaz NKA

disjunktna_unija, ε_proširenje: korisno za dodavanje novih elemenata u skup

NedeterminističkiKonačniAutomat:
  analogno kao KonačniAutomat:
    bitne metode: definicija, iz_konačnog_automata, prihvaća, partitivna_konstrukcija
    (.funkcija_prijelaza je pomoćna stvar, za pretvaranje rel<->fun)

optimizirana_partitivna_konstrukcija: bitna razlika u odnosu na partitivna_konstrukcija
  je što ne konstruira čitav partitivni skup, već samo dohvatljiva stanja

označi, označi1, novo: pomoćne funkcije, za nedeterministička_*

  označi: dodaje dodatnu oznaku na stanja, u svrhu disjunktifikacije

  novo: stvara novu oznaku za stanje, koja sigurno nije u zadanom skupu

    Δ = set()
    for q in Q:
        for α in Σ:
            Δ.add((q, α, δ[q, α]))

RI.py
=====

osnovni izrazi i konstrukcije:

prazan: RI prazan skup

epsilon: RI {''}

Elementaran(znak): RI {znak}

Unija(ri1, ri2): RI ri1|ri2

Konkatenacija(ri1, ri2): RI ri1ri2

KleeneZvijezda(ri): RI ri*

(KleenePlus i KleeneUpitnik su implementirani pomoću KleeneZvijezda)

bitno: implementacije svojstava (pozitivan, beskonačan, prazan, trivijalan,...)
       korištenje NKA.nedeterministička_* za pretvaranje RI->NKA->KA
         (na razini pseudokoda)

početak: korisno za debug

## primjer leksičke i sintaksne analize

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
