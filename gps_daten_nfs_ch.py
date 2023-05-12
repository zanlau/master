import json
import requests
import urllib.parse
from openpyxl import load_workbook


wb = load_workbook('daten/notfallstationen_ch_copy.xlsx')
worksheet = wb['Standorte 2021 KZP21']

stations = []

for row in worksheet.iter_rows(min_row=2): #von erster Spalte über alle Elemente iterieren
    address = f"{row[8].value}, {row[9].value}"
    print(address)
    url = f'https://nominatim.openstreetmap.org/search/{urllib.parse.quote(address)}?format=json'
    response = requests.get(url).json()
    stations.append({
        "lat": response[0]["lat"],
        "lon": response[0]["lon"],
        "institut": row[7].value,
        "stand_address": row[8].value,
        "stand_ort": row[9].value
    })

data = {
    "source": "BFS - Bundesamt für Statistik",
    "data": stations
}

with open('daten/notfallstationen_ch.json', 'w') as f:
    json.dump(data, f, indent=4)