import json
import requests
import urllib.parse
from openpyxl import load_workbook


wb = load_workbook('')
worksheet = wb['']

stations = []

for row in worksheet.iter_rows(min_row=?): #von erster Spalte über alle Elemente iterieren
    address = ?
    print(address)
    url = f'https://nominatim.openstreetmap.org/search/{urllib.parse.quote(address)}?format=json'
    response = requests.get(url).json()
    stations.append({
        "lat": response[0]["lat"],
        "lon": response[0]["lon"],
        "institut": ?,
        "stand_address": ?,
        "stand_ort": ?
    })

data = {
    "source": "?",
    "data": stations
}

with open('daten/notfallstationen_lu.json', 'w') as f:
    json.dump(data, f, indent=4)