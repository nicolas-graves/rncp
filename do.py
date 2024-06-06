import os
import requests
import zipfile
import pandas as pd
from icecream import ic
from pandas import IndexSlice as idx

# URL of the ZIP file
url = "https://static.data.gouv.fr/resources/\
repertoire-national-des-certifications-professionnelles-et-repertoire-specifique/\
20240501-020200/export-fiches-csv-2024-05-01.zip"
zip_filename = "data/export-fiches-csv-2024-05-01.zip"
csv_filename = "data/export_fiches_CSV_Standard_2024_05_01.csv"

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Check if the ZIP file is already downloaded
if not os.path.exists(zip_filename):
    print("Downloading the ZIP file...")
    response = requests.get(url)
    with open(zip_filename, "wb") as f:
        f.write(response.content)
    print("Download completed.")
else:
    print("ZIP file already exists. Skipping download.")

# Extract the ZIP file if the CSV is not already extracted
if not os.path.exists(csv_filename):
    print("Extracting the ZIP file...")
    with zipfile.ZipFile(zip_filename, "r") as z:
        z.extractall("data")
    print("Extraction completed.")
else:
    print("CSV file already exists. Skipping extraction.")

# Load the CSV file into a pandas DataFrame
print("Loading the CSV file into a DataFrame...")
df = pd.read_csv(
    csv_filename,
    sep=";",
    usecols=["Numero_Fiche", "Abrege_Libelle", "Intitule", "Actif"],
    index_col=["Numero_Fiche", "Actif", "Abrege_Libelle"],
)

# Filtering the DataFrame
df = df.xs("ACTIVE", level="Actif")
ic(df)
df = df.loc[idx[:, ["CAP", "CAPA", "BAC PRO", "BTS", "BTSA", "TP", "BP"]], :]

# Export the filtered DataFrame to an Excel file
os.makedirs("outputs", exist_ok=True)
output_filename = "outputs/filtered_data.xlsx"
df.to_excel(output_filename)

print(f"Filtered data has been exported to '{output_filename}'.")
