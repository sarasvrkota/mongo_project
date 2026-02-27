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
dev_cols = ['ResponseId', 'MainBranch', 'Age', 'Employment', 'RemoteWork', 'EdLevel', 'Country', 'YearsCodePro', 'LearnCode', 'OrgSize', 'SOVisitFreq', 'ConvertedCompYearly', 'TimeSearching','JobSat', 'Industry']
tech_cols = ['ResponseId', 'LanguageHaveWorkedWith', 'DatabaseHaveWorkedWith', 'PlatformHaveWorkedWith', 'AISelect', 'AISearchDevHaveWorkedWith','AISearchDevWantToWorkWith', 'WebframeHaveWorkedWith']





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

    podaci = df[lista_kolona].copy()
    podaci = podaci.dropna(subset=['ResponseId'])

    # TRANSFORMACIJA 1 --- pretrvori u int
    if 'YearsCodePro' in podaci.columns:
        print("  -> Pretvaram 'YearsCodePro' u brojeve (int)...")
        podaci['YearsCodePro'] = podaci['YearsCodePro'].apply(ocisti_godine_staza)

    # TRANSFORMACIJA 2 --  split po ;
    for col in lista_kolona:
        if podaci[col].dtype == 'object' and col != 'ResponseId':
            if podaci[col].str.contains(';', na=False).any():
                print(f"  -> Pretvaram kolonu '{col}' u niz...")
                podaci[col] = podaci[col].apply(pretvori_u_niz)

    # Konverzija u recnik za MongoDB
    data_records = podaci.to_dict(orient="records")

    if data_records:
        db[naziv_kolekcije].drop()
        db[naziv_kolekcije].insert_many(data_records)
        print(f"Uspešno ubačeno u '{naziv_kolekcije}'.")





uvoz_u_kolekciju("developers", dev_cols)
uvoz_u_kolekciju("technologies", tech_cols)


print("\nGotovo! 'YearsCodePro' je sada brojčani tip (int), a tehnologije su nizovi.")
client.close()