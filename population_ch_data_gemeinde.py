import json
import requests
import urllib.parse
from openpyxl import load_workbook


wb = load_workbook('daten/population_ch.xlsx')
worksheet = wb['Gemeinde']

municipality = []

for row in worksheet.iter_rows(min_row=2): #von erster Spalte über alle Elemente iterieren
    numbers = f"{row[1].value}".replace("/", " ")
    print(numbers)
    url = f'https://nominatim.openstreetmap.org/search/{urllib.parse.quote(numbers)}?format=json&countrycodes=ch'
    response = requests.get(url).json()
    print(response)

    for i, item in enumerate(response):
        osm_type = {"relation": "R", "node": "N", "way": "W"}[item["osm_type"]] #alle osm_types integrieren, da diese sonst nicht abgerufen werden können

        if osm_type == "R" or (osm_type == "N" and item["class"] == "place" and item["type"] == "village"):
            url2 = f'https://nominatim.openstreetmap.org/lookup?osm_ids={osm_type}{item["osm_id"]}&format=json'
            response2 = requests.get(url2).json()
            print(response2)
            address = response2[0]["address"]
            matchers = ["city", "town", "village", "municipality", "hamlet", "suburb"]
            if any(x in address for x in matchers) and address["country_code"] == "ch":
                municipality.append({
                    "lat": response[i]["lat"],
                    "lon": response[i]["lon"],
                    "number": row[0].value,
                    "name": row[1].value,
                    "population": row[2].value,
                    "osm_id": response[i]["osm_id"]
                })
                break
        print("NEXT TRY")
    else:
        print("AAAAAAAAAA")
        raise "AAAA"


data = {
    "source": "Bundesamt für Statistik - Bevölkerung"
              "https://www.pxweb.bfs.admin.ch/pxweb/de/px-x-0102010000_101/px-x-0102010000_101/px-x-0102010000_101.px",
    "data": municipality
}

with open('daten/population_ch_gemeinde.json', 'w') as f:
    json.dump(data, f, indent=4)