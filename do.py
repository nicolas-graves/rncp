import os
import glob
import requests
import zipfile
import pandas as pd
from icecream import ic
from pandas import IndexSlice as idx

data_id = "682f07fb-4cf5-46e7-a362-b27fada965c1"
url = f"https://www.data.gouv.fr/fr/datasets/r/{data_id}"
zip_filename = f"data/{data_id}.zip"


def local_file(dataset):
    return glob.glob(f"data/export_fiches_CSV_{dataset.capitalize()}_*.csv")[0]


os.makedirs("data", exist_ok=True)
if not ic(os.path.exists(zip_filename)):
    print(f"Downloading {zip_filename}...")
    response = requests.get(url)
    with open(zip_filename, "wb") as f:
        f.write(response.content)

if not ic(os.path.exists(local_file("standard"))):
    print(f"Extracting {zip_filename}...")
    with zipfile.ZipFile(zip_filename, "r") as z:
        z.extractall("data")

standard = pd.read_csv(
    local_file("standard"),
    sep=";",
    usecols=[
        "Numero_Fiche",
        "Abrege_Libelle",
        "Intitule",
        "Actif",
        "Nomenclature_Europe_Niveau",
    ],
    index_col=["Numero_Fiche", "Actif", "Abrege_Libelle", "Nomenclature_Europe_Niveau"],
)

rome = pd.read_csv(
    local_file("rome"),
    sep=";",
    usecols=["Numero_Fiche", "Codes_Rome_Code"],  # Codes_Rome_Libelle
    index_col=["Numero_Fiche"],
)

ministeres_certificateurs = {
    "MINISTERE DE L'EDUCATION NATIONALE ET DE LA JEUNESSE": "MENJ",
    "SECRETARIAT D'ETAT AUPRES DU PREMIER MINISTRE CHARGE DE LA MER": "MMer",
    "MINISTERE DE LA TRANSITION ECOLOGIQUE ET DE LA COHESION DES TERRITOIRES": "MMer",
    "MINISTERE DE L'AGRICULTURE ET DE LA SOUVERAINETE ALIMENTAIRE": "MASA",
    "MINISTERE DE L'ENSEIGNEMENT SUPERIEUR ET DE LA RECHERCHE": "MESR",
    "MINISTERE DU TRAVAIL DU PLEIN EMPLOI ET DE L' INSERTION": "MTPEI",
    "MINISTERE DES SPORTS ET DES JEUX OLYMPIQUES ET PARALYMPIQUES": "MSport",
    "MINISTERE DE LA SANTE ET DE LA PREVENTION": "MSante",
    "MINISTERE DE LA JUSTICE": "MJustice",
    "MINISTERE DES ARMEES": "MArmees",
    "MINISTERE DE L' INTERIEUR ET DES OUTRE-MER": "MInterieur",
    "MINISTERE DE LA CULTURE": "MCulture",
}

certificateurs = pd.read_csv(
    local_file("certificateurs"),
    sep=";",
    usecols=["Numero_Fiche", "Nom_Certificateur"],  # Siret_Certificateur
    index_col=["Numero_Fiche"],
)

df = standard.xs("ACTIVE", level="Actif")
# ["CAP", "CAPA", "BAC PRO", "BTS", "BTSA", "BTSMarit", "TP", "BP", "BMA", "BPJEPS", "CPJEPS", "DE", "DMA"])
df = df.loc[idx[:, :, ["NIV3", "NIV4", "NIV5"]], :]
df = (
    df.join(rome, on="Numero_Fiche")
    .join(certificateurs, on="Numero_Fiche")
    .set_index("Nom_Certificateur", append=True)
    .set_index("Intitule", append=True)
    .set_index("Codes_Rome_Code", append=True)
)

df = df.loc[idx[:, :, :, list(ministeres_certificateurs.keys())]].rename(
    ministeres_certificateurs, level="Nom_Certificateur"
)

df.index.names = ["Fiche", "Libellé", "Niveau", "Certificateur", "Intitulé", "ROME"]

os.makedirs("outputs", exist_ok=True)
df.to_excel("outputs/filtered_data.xlsx")
