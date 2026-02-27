import pandas as pd
from pymongo import MongoClient

#   MongoDB konekcija
client = MongoClient("mongodb://localhost:27017/")
db = client.dev

csv_file_path = "survey_results_public.csv"

# 2. CSV faj
try:
    df = pd.read_csv(csv_file_path, on_bad_lines="skip")
    print("Fajl uspešno učitan.")
except FileNotFoundError:
    print(f"Greška: Fajl '{csv_file_path}' nije pronađen.")
    exit()

# kolone -- prostiranje?
dev_cols2 = ['AISearchDevHaveWorkedWith','LanguageHaveWorkedWith', 'AISelect','DatabaseHaveWorkedWith','ResponseId', 'MainBranch', 'Age', 'Employment', 'RemoteWork', 'EdLevel', 'Country', 'YearsCodePro', 'LearnCode', 'OrgSize', 'SOVisitFreq', 'ConvertedCompYearly', 'TimeSearching','JobSat', 'Industry']
tech_cols2 = ['ResponseId', 'LanguageHaveWorkedWith', 'DatabaseHaveWorkedWith', 'PlatformHaveWorkedWith', 'AISelect', 'AISearchDevHaveWorkedWith','AISearchDevWantToWorkWith', 'WebframeHaveWorkedWith']





def ocisti_godine_staza(vrednost):
    # string u int
    if pd.isna(vrednost):
        return None
    vrednost = str(vrednost).lower()
    if 'less than 1 year' in vrednost:
        return 0
    if 'more than 50 years' in vrednost:
        return 51
    try:
        return int(vrednost)
    except ValueError:
        return None

def pretvori_u_niz(vrednost):
    #Pretvara string sa ; u Python listu
    if pd.isna(vrednost):
        return []
    return str(vrednost).split(';')

# ###################################

# Funkcija za uvoz sa transformacijom
def uvoz_u_kolekciju(naziv_kolekcije, lista_kolona):
    print(f"Priprema kolekcije '{naziv_kolekcije}'...")

    # 1. AKO JE DEVELOPERS2, PRVO IZRAČUNAJ NOVU KOLONU
    if naziv_kolekcije == "developers2":
        dodaj_nivo_iskustva_i_sacuvaj()
        # Osiguravamo da je nova kolona u spisku za kopiranje
        if 'levelExperience' not in lista_kolona:
            lista_kolona.append('levelExperience')

    # 2. Napravi kopiju podataka
    podaci = df[lista_kolona].copy()
    podaci = podaci.dropna(subset=['ResponseId'])

    # 3. TRANSFORMACIJA 1 --- YearsCodePro u int
    if 'YearsCodePro' in podaci.columns:
        print("  -> Pretvaram 'YearsCodePro' u brojeve (int)...")
        podaci['YearsCodePro'] = podaci['YearsCodePro'].apply(ocisti_godine_staza)

    # 4. TRANSFORMACIJA 2 -- split po ; (preskačemo levelExperience)
    for col in lista_kolona:
        # Ne diramo levelExperience jer je on već čist string
        if col == 'levelExperience':
            continue

        if podaci[col].dtype == 'object' and col != 'ResponseId':
            if podaci[col].str.contains(';', na=False).any():
                print(f"  -> Pretvaram kolonu '{col}' u niz...")
                podaci[col] = podaci[col].apply(pretvori_u_niz)

    # 5. Konverzija u rečnik i UPIS
    data_records = podaci.to_dict(orient="records")

    if data_records:
        db[naziv_kolekcije].drop()  # Briše staru, ubacuje novu sa levelExperience
        db[naziv_kolekcije].insert_many(data_records)
        print(f"Uspešno ubačeno u '{naziv_kolekcije}'.")






# prviiiiii

def kreiraj_statistiku_drzava():
    print("Računam preciznu statistiku (5-10 god iskustva) za MongoDB...")

    # 1. Čistimo godine staža u glavnom DataFrame-u pre računanja
    df['YearsCodePro_Clean'] = df['YearsCodePro'].apply(ocisti_godine_staza)

    # 2. Filtriramo: validna plata I iskustvo 5-10 godina
    mask = (df['ConvertedCompYearly'] > 0) & \
           (df['YearsCodePro_Clean'] >= 5) & \
           (df['YearsCodePro_Clean'] <= 10)

    plate_df = df[mask].copy()

    # 3. Grupisanje po Country i EdLevel(Suma i Broj ljudi)
    stats = plate_df.groupby(['Country', 'EdLevel']).agg({
        'ConvertedCompYearly': 'sum',
        'ResponseId': 'count'
    }).reset_index()

    stats.columns = ['country', 'edLevel', 'totalSalarySum', 'devCountInGroup']

    # 4. Slanje u MongoDB
    db["country_stats"].drop()
    db["country_stats"].insert_many(stats.to_dict(orient="records"))

    # Sloyeni indeks
    db["country_stats"].create_index([("country", 1), ("edLevel", 1)])
    print("Kolekcija 'country_stats' je optimizovana za 5-10 godina iskustva.")


kreiraj_statistiku_drzava()
###############################################################################################


#ZA SEDMI UPIT
def kreiraj_org_size_computed():
    print("Generišem optimizovanu kolekciju za OrgSize statistiku...")

    # 1.
    # Uzimam samo redove gde imam sve potrebne podatke
    df_clean = df.dropna(subset=['OrgSize', 'YearsCodePro', 'Age', 'LanguageHaveWorkedWith']).copy()
    df_clean['YearsCodePro'] = df_clean['YearsCodePro'].apply(ocisti_godine_staza)
    df_clean['LangList'] = df_clean['LanguageHaveWorkedWith'].apply(pretvori_u_niz)

    # 2. Explode jezika (svaki jezik postaje poseban red)
    df_exploded = df_clean.explode('LangList')

    # 3 Racunam statistiku po grupi (OrgSize, Jezik, Age)
    # Kao ono prvo grupisanje iz agregacije
    stats = df_exploded.groupby(['OrgSize', 'LangList', 'Age']).agg({
        'YearsCodePro': 'mean',
        'ResponseId': 'count'
    }).reset_index()

    stats.columns = ['orgSize', 'jezik', 'age', 'avgExp', 'count']


    db["org_size_computed"].drop()
    db["org_size_computed"].insert_many(stats.to_dict(orient="records"))

    # Indeks
    db["org_size_computed"].create_index([("orgSize", 1), ("count", -1)])
    print("Kolekcija 'org_size_computed'  kreiranaaa")


# Poziv
kreiraj_org_size_computed()


#ZA OSMI UPIT
def optimizuj_so_migraciju():
    print("Računam unapred statistiku za StackOverflow posete...")

    # Filtriram 2 grupe
    ciljane_grupe = ["Daily or almost daily", "A few times per month or weekly"]
    df_filtered = df[df['SOVisitFreq'].isin(ciljane_grupe)].copy()

    # Čistim podatke
    df_filtered['YearsCodePro'] = df_filtered['YearsCodePro'].apply(ocisti_godine_staza)
    df_filtered = df_filtered.dropna(subset=['ConvertedCompYearly', 'YearsCodePro', 'Country'])

    # Agregacija
    so_stats = df_filtered.groupby(['Country', 'SOVisitFreq']).agg({
        'ConvertedCompYearly': 'mean',
        'YearsCodePro': 'mean',
        'ResponseId': 'count'
    }).reset_index()

    so_stats.columns = ['country', 'visitFreq', 'avgSalary', 'avgExp', 'count']

    # Slanje u novu kolekciju
    db["so_migration_stats"].drop()
    db["so_migration_stats"].insert_many(so_stats.to_dict(orient="records"))
    print("Kolekcija 'so_migration_stats' je spremna.")


optimizuj_so_migraciju()

#DEVETI UPIT PRORACUNAVANJE DODATO NOVO POLJE U KOLEKCIJU DEVELOPERS2 levelExperience
# DEVETI UPIT PRORACUNAVANJE
def dodaj_nivo_iskustva_i_sacuvaj():
    global dev_cols2

    print("Računam nivo iskustva (preskačem NaN vrednosti, ali zadržavam redove)...")

    # 1. Pretvaramo YearsCodePro u brojeve (tamo gde ne može, biće NaN)
    df['YearsCodePro_Tmp'] = df['YearsCodePro'].apply(ocisti_godine_staza)

    # 2. Definisanje logike kategorizacije
    def kategorisi(godine):
        # Ovde ne moramo brinuti o NaN jer ćemo funkciju pozvati samo nad brojevima
        if godine <= 2:
            return "Junior (0-2 god)"
        elif godine <= 8:
            return "Mid (3-8 god)"
        else:
            return "Senior (9+ god)"

    # 3. PRIMENA SAMO NAD VREDNOSTIMA KOJE NISU NaN
    # Kreiramo masku za redove koji imaju validan broj godina
    mask = df['YearsCodePro_Tmp'].notna()

    # Primenjujemo kategorizaciju samo na te redove, ostali ostaju NaN (double/null)
    df.loc[mask, 'levelExperience'] = df.loc[mask, 'YearsCodePro_Tmp'].apply(kategorisi)

    # 4. Dodavanje u listu za uvoz
    if 'levelExperience' not in dev_cols2:
        dev_cols2.append('levelExperience')
        print("  -> Kolona 'levelExperience' je dodata (sa NaN gde nema podataka).")





uvoz_u_kolekciju("developers2", dev_cols2)
uvoz_u_kolekciju("technologies2", tech_cols2)


print("\nGotovo! 'YearsCodePro' je sada brojčani tip (int), a tehnologije su nizovi.")














client.close()