.. vepar documentation master file, created by
   sphinx-quickstart on Thu May 20 07:26:27 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dokumentacija za vepar 2.0
==========================

.. toctree::
   :maxdepth: 2
   :caption: Sadržaj:

   tutorial/lexer
   tutorial/parser
   tutorial/semantic
   refer/modules
   refer/vepar
   refer/backend

Vepar vam omogućuje da koristeći Python pišete vlastite programske
jezike, prolazeći kroz uobičajene faze kao što su leksiranje,
parsiranje, proizvodnja apstraktnih sintaksnih stabala (AST),
optimizacija, generiranje bajtkoda za virtualni stroj, te izvršavanje
(interpretaciju u užem smislu).

Ne trebate znati puno Pythona za to: vepar je framework (poput
npr. Djanga) koji ima svoje konvencije i prilično rigidan uobičajeni
stil pisanja, iz kojih ćete rijetko trebati izaći. Ipak, poznavanje
Pythona sigurno će pomoći, jer ćete manje toga morati naučiti i
mnogi detalji u dizajnu imat će vam više smisla.

Iako se vepar može koristiti u profesionalnom okruženju, prvenstveno
je zamišljen kao akademski alat: cilj je naučiti što više o uobičajenim
tehnikama interpretacije programa, a ne napisati najbrži parser, ni
semantički analizator s najboljim mogućim oporavkom od grešaka, niti
generator strašno optimiziranog koda.

To je ujedno i glavna prednost vepra pred uobičajenim alatima kao što
su flex, yacc i LLVM: ne morajući cijelo vrijeme razmišljati o performansama,
vepar može puno bolje izložiti osnovne koncepte koji stoje u pozadini raznih
faza interpretacije programa, razdvajajući ih i tretirajući svaki zasebno.
Spoj toga i uobičajene Pythonove filozofije "sve je interaktivno, dinamično
i istraživo" predstavlja dobru podlogu za učenje.


Dodatno
=======

* :ref:`genindex`
