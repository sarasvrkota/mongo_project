Stack Overflow Data Analysis: MongoDB & Metabase Optimization
Ovaj projekat se bavi analizom Stack Overflow ankete koristeći NoSQL (MongoDB) bazu podataka. Glavni fokus je na transformaciji nestrukturiranih podataka u optimizovane kolekcije spremne za naprednu analitiku.

## Tehnologije i Alati
Python (Pandas): Za ETL (Extract, Transform, Load) proces i čišćenje podataka.

MongoDB: Primarna NoSQL baza podataka.

Studio 3T: GUI alat za upravljanje MongoDB bazom i testiranje upita.

Docker: Korišćen za kontejnerizaciju i brzo pokretanje Metabase platforme.

Metabase: Alat za vizuelizaciju podataka i kreiranje dashboard-a.

# Ključni koraci projekta
## Čišćenje i Transformacija (Python)
Sirovi podaci iz CSV fajla su procesuirani kako bi odgovarali NoSQL formatu:

Konverzija tipova: Polje YearsCodePro je očišćeno od tekstualnih vrednosti (npr. "Less than 1 year") i pretvoreno u integer.

Nizovi (Arrays): Polja sa višestrukim odgovorima (jezici, baze) razbijena su iz stringa sa tačka-zarezom (;) u Python liste radi lakše pretrage u Mongu.

Kategorizacija: Kreirano je novo polje levelExperience koje deli developere na Junior, Mid i Senior kategorije.

## Modelovanje i Optimizacija 
Umesto korišćenja samo jedne ogromne kolekcije, kreirane su specifične kolekcije za optimizaciju upita:

developers2 i technologies2: Osnovne, očišćene kolekcije.

country_stats: Unapred agregirani podaci o platama po državama i nivou obrazovanja.

org_size_computed: Kolekcija optimizovana za upite o veličini organizacije i jezicima.

so_migration_stats: Kolekcija za analizu učestalosti poseta Stack Overflow-u.

## Indeksiranje
U skripti su implementirani složeni indeksi (Compound Indexes) kako bi se ubrzalo filtriranje:

Python
db["country_stats"].create_index([("country", 1), ("edLevel", 1)])
db["org_size_computed"].create_index([("orgSize", 1), ("count", -1)])
4. Vizuelizacija (Metabase & Docker)
Metabase je podignut unutar Docker kontejnera radi lakše prenosivosti. Povezan je sa MongoDB bazom kako bi se prikazali ključni trendovi.

# Kako pokrenuti
Pokrenite MongoDB lokalno (port 27017).

Instalirajte zavisnosti: pip install pandas pymongo.

Pokrenite Python skriptu za uvoz i transformaciju podataka.

Pokrenite Metabase preko Dockera:

Bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
Pristupite na localhost:3000 i povežite se na dev bazu.
