import json
import sys
import copy
import re

import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.graph_objects as go
from dash import html, ctx
from dash.dependencies import Input, Output
from flask import Flask
from shapely.geometry import Point
from scipy import spatial


import view

if dash.__version__ != "2.10.2":
    print("dash version 2.10.2 required!")
    sys.exit()


server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "Dashboard Notfallversorgungen"

app.layout = view.layout


@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return view.render_tab1()
    elif tab == 'tab-2':
        return view.render_tab2()

# Klassen, damit nicht immer der ganze Code für erneut eingegeben werden muss
class Cord:
    def __init__(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def to_Point(self):
        return Point(self.lon, self.lat)

    def __str__(self):
        return f"{self.lat} {self.lon}"


class Location:
    def __init__(self, coordinates, country, city=None, postcode=None, street=None, housenumber=None):
        self.coordinates = coordinates
        self.country = country
        self.city = city
        self.postcode = postcode
        self.street = street
        self.housenumber = housenumber

    def __str__(self):
        return re.sub(' +', ' ',
                      f'{self.country or ""} {self.city or ""} {self.postcode or ""} {self.street or ""} {self.housenumber or ""}')


class NFS:
    PERSONAL_OCCUPANCY_FACTOR = 50
    POPULATION_EMERGENCY_USAGE_FACTOR = 0.125

    def __init__(self, name, kind, location, personal=None):
        self.name = name or f"{kind} {location}"
        self.kind = kind
        self.location = location
        self.personal = personal
        if self.personal:
            self._occupancy = personal * self.PERSONAL_OCCUPANCY_FACTOR
        self.color = \
        {"notfallstation": "blue", "stroke_unit": "green", "fire_station": "red", "air_ambulance": "yellow", "emed": "black"}[self.kind]

    def __str__(self):
        return f"{self.name}: {self.kind} {self.location}"

    __repr__ = __str__

    # Berechnung für Einzugsgebiete anhand der Grösse der Notfallstation
    def remaining_occupancy(self, population=None):
        if population:
            population = int(population * self.POPULATION_EMERGENCY_USAGE_FACTOR)
            if val := bool((self._occupancy - population) >= 0):
                self._occupancy -= population
                return True
            return False
        return bool(self._occupancy)


def open_data():
    data = []
    with open("daten/notfallstationen_ch.json") as f:
        data.extend(
            [NFS(x["institut"], "notfallstation", Location(Cord(x["lat"], x["lon"]), "CH"), x["personal_bestand"]) for x
             in json.load(f)["data"]])
    with open("daten/notfallstationen_lu.json") as f:
        data.extend(
            [NFS(x["institut"], "notfallstation", Location(Cord(x["lat"], x["lon"]), "LU"), x["personal_bestand"]) for x
             in json.load(f)["data"]])
    with open("daten/stroke_units_ch.json") as f:
        data.extend(
            [NFS(x["institut"], "stroke_unit", Location(Cord(x["lat"], x["lon"]), "CH")) for x in json.load(f)["data"]])
    with open("daten/stroke_untis_lu.json") as f:
        data.extend(
            [NFS(x["institut"], "stroke_unit", Location(Cord(x["lat"], x["lon"]), "LU")) for x in json.load(f)["data"]])
    with open("daten/fire_station_ch.json") as f:
        elements = json.load(f)["elements"]

        # um lat und lon zu finden muss man in den nodes suchen gehen
        for s in elements:
            name = s.get("tags", {}).get("name")
            if name or s.get("tags", {}).get("amenity") == "fire_station":
                try:
                    cord = Cord(s["lat"], s["lon"])
                except KeyError:
                    # No Coordinates found in node
                    if cords := [(i["lat"], i["lon"])
                                 for i in elements
                                 for node in s.get("nodes", [])
                                 if i["id"] == node]:
                        cord = Cord(sum(x[0] for x in cords) / len(cords), sum(x[1] for x in cords) / len(cords))
                data.append(NFS(name, "fire_station", Location(cord, "CH")))

    with open("daten/fire_station_lu.json") as f:
        elements = json.load(f)["elements"]

        for s in elements:
            name = s.get("tags", {}).get("name")
            if name or s.get("tags", {}).get("amenity") == "fire_station":
                try:
                    cord = Cord(s["lat"], s["lon"])
                except KeyError:
                    # No Coordinates found in node
                    if cords := [(i["lat"], i["lon"])
                                 for i in elements
                                 for node in s.get("nodes", [])
                                 if i["id"] == node]:
                        cord = Cord(sum(x[0] for x in cords) / len(cords), sum(x[1] for x in cords) / len(cords))
                data.append(NFS(name, "fire_station", Location(cord, "LU")))

    return data

# Daten für Luftrettung hinzufügen
def open_air_ambulance_data():
    data_air = []
    with open("daten/air_ambulance_ch.json") as f:
        data_air.extend(
            [NFS(x["institut"], "air_ambulance", Location(Cord(x["lat"], x["lon"]), "CH")) for x in
             json.load(f)["data"]])
    with open("daten/air_ambulance_lu.json") as f:
        data_air.extend(
            [NFS(x["institut"], "air_ambulance", Location(Cord(x["lat"], x["lon"]), "LU")) for x in
             json.load(f)["data"]])
    return data_air

# Daten für eNotfallmedizin
def open_emed_data():
    with open("daten/country_center.json") as f:
        data_emed.extend(
            [NFS(x["country"], "eMedizin", Location(Cord(x["lat"], x["lon"]))) for x in
             json.load(f)["data"]])
    return data_emed


# Diagramme / Karte im Dashboard generieren
# Positionen in OpenStreetMap erzeugen
def get_fig(data, criteria, speed, aad, emed):
    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=[x.location.coordinates.lat for x in data],
            lon=[x.location.coordinates.lon for x in data],
            marker=dict(size=15, color=[x.color for x in data]),
            text=[f"Name: {x.name}<br>Kind: {x.kind}" for x in data],
            textfont=dict(size=20)
        )
    )

    if aad:
        fig.add_trace(
            go.Scattermapbox(
                lat=[x.location.coordinates.lat for x in aad],
                lon=[x.location.coordinates.lon for x in aad],
                marker=dict(size=15, color=[x.color for x in aad]),
                text=[f"Name: {x.name}<br>Kind: {x.kind}" for x in aad],
                textfont=dict(size=20),
            )
        )
        d = {"geometry": [x.location.coordinates.to_Point() for x in aad]}
        gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

        cgeo = (
            gdf.set_crs("epsg:4326")
                .pipe(lambda d: d.to_crs(d.estimate_utm_crs()))["geometry"]
                .centroid.buffer(60000)  # vollständige Abdeckung
                .to_crs("epsg:4326")
                .__geo_interface__
        )
        fig.update_layout(
            mapbox={
                "layers": [
                    {"source": cgeo, "color": "yellow", "type": "fill", "opacity": .2},
                ],
            }
        )

    if criteria == "minutes":
        d = {"geometry": [x.location.coordinates.to_Point() for x in data]}
        gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

        cgeo = (
            gdf.set_crs("epsg:4326")
                .pipe(lambda d: d.to_crs(d.estimate_utm_crs()))["geometry"]
                .centroid.buffer(speed*250)  # 12.5km (50 km/h, 15 Minuten = 12.5km) - berechnet in Grad
                .to_crs("epsg:4326")
                .__geo_interface__
        )
        fig.update_layout(
            mapbox={
                "layers": [
                    {"source": cgeo, "color": "PaleTurquoise", "type": "fill", "opacity": .5},
                    {"source": cgeo, "color": "black", "type": "line", "opacity": 0.1},
                ]
            }
        )

    elif criteria == "area":
        # prep geometry
        d = {"geometry": [x.location.coordinates.to_Point() for x in data]}
        gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

        cgeo = (
            gdf.set_crs("epsg:4326")
                .pipe(lambda d: d.to_crs(d.estimate_utm_crs()))["geometry"]
                .centroid.buffer(13819)  # 600km^2 Fläche
                .to_crs("epsg:4326")
                .__geo_interface__
        )
        fig.update_layout(
            mapbox={
                "layers": [
                    {"source": cgeo, "color": "PaleTurquoise", "type": "fill", "opacity": .5},
                    {"source": cgeo, "color": "black", "type": "line", "opacity": 0.1},
                ]
            }
        )


    elif criteria == "population":
        pop_data = open_population_data()

        municipality = [(x["lat"], x["lon"]) for x in pop_data]
        max_distance = 5 #jumping verhindern (5km)
        while municipality:
            found = False
            for i, nfs in enumerate(data):
                tree = spatial.KDTree(municipality)
                distance, index = tree.query([(nfs.location.coordinates.lat, nfs.location.coordinates.lon)])
                if distance[0] <= (max_distance/40000*360):
                    g = municipality[index[0]]
                    for p in pop_data:
                        if (p["lat"], p["lon"]) == g:
                            break

                    if nfs.remaining_occupancy(int(p["number"])):
                        p["nfs_name"] = nfs.name
                        p["nfs"] = i
                        found = True
                        municipality.pop(index[0])

                    if not municipality:
                        break
            if not found:
                max_distance += 1

        fig.add_trace(
            go.Choroplethmapbox(
                name="",
                geojson=json.load(open("daten/borders.geojson")),
                locations=[f'relation/{x["osm_id"]}' for x in pop_data],
                z=[x.get("nfs", -1) for i, x in enumerate(pop_data)],
                text=[x.get("nfs_name", "UNKNOWN") for x in pop_data],
                hovertemplate='%{text}',
                colorscale="Turbo",
                showscale=False,
                marker=dict(opacity=0.7)
            )
        )


    elif criteria == "full_coverage":
        pop_data = open_population_data()

        municipality = [(x["lat"], x["lon"]) for x in pop_data]
        max_distance = 5 #jumping verhindern (5km Start, dann immer +1km)
        while municipality:
            found = False
            for i, nfs in enumerate(data):
                tree = spatial.KDTree(municipality)
                distance, index = tree.query([(nfs.location.coordinates.lat, nfs.location.coordinates.lon)])
                if distance[0] <= (max_distance/40000*360):
                    g = municipality.pop(index[0])
                    for p in pop_data:
                        if (p["lat"], p["lon"]) == g:
                            p["nfs"] = i
                            p["nfs_name"] = nfs.name
                            found = True
                            break
                    if not municipality:
                        break
            if not found:
                max_distance += 1


        fig.add_trace(
            go.Choroplethmapbox(
                name="",
                geojson=json.load(open("daten/borders.geojson")),
                locations=[f'relation/{x["osm_id"]}' for x in pop_data],
                z=[x.get("nfs", -1) for x in pop_data],
                text=[x.get("nfs_name", "UNKNOWN") for x in pop_data],
                hovertemplate='%{text}',
                colorscale="Turbo",
                showscale=False,
                marker=dict(opacity=0.7)
            )
        )
        fig.update_traces(showlegend=False)


    elif criteria == "borders":
        pop_data = map_nfs_to_municipality(data, open_population_data())

        fig.add_trace(
            go.Choroplethmapbox(
                name="",
                geojson=json.load(open("daten/borders.geojson")),
                locations=[f'relation/{x["osm_id"]}' for x in pop_data if "nfs" in x],
                z=[x.get("nfs", -1) for x in pop_data if "nfs" in x],
                text=[x.get("nfs_name", "UNKNOWN") for x in pop_data if "nfs" in x],
                hovertemplate='%{text}',
                colorscale="Turbo",
                showscale=False,
                marker=dict(opacity=0.7)
            )
        )


    # open street map mit Standardposition
    fig.update_layout(
        height=1300,
        margin={"r": 10, "t": 10, "b": 10, "l": 10},
        autosize=True,
        mapbox=dict(style="open-street-map", center=dict(lat=47.95, lon=7.45), zoom=7, uirevision=len(data)),
        hoverlabel=dict(font=dict(size=20)),
        showlegend=False
        # Deaktivierung der automatischen Rückkehr zur Standardposition
    )
    return fig


def filter_data_based_on_criteria(data, kind):
    if kind:
        return [x for x in data if x.kind == kind]
    return data



@app.callback(
    Output("graph", "figure"),
    Output("criteria_slider_div", "style"),
    Output("criteria", "options"),
    inputs={
        "all_inputs": {
            "criteria_slider": Input("criteria_slider", "value"),
            "emergency_type": Input("emergency_type", "value"),
            "criteria": Input("criteria", "value"),
            "air_ambulance_button": Input("air_ambulance", "value"),
            "emed_button": Input("emed", "value")
        }
    },
)
def update_map(all_inputs):
    data = open_data()
    c = ctx.args_grouping["all_inputs"]

    air_ambulance_data = None
    emed_data = None
    data = filter_data_based_on_criteria(data, c.emergency_type.value)

    dropdown = [{"label": "15 Minuten", "value": 'minutes'},
                {"label": "Vollständige Abdeckung", "value": 'full_coverage'}]

    button = [{"label": "Luftrettung", "value": "air_ambulance"}]
    button2 = [{"label": "eNotfallmedizin", "value": "emed"}]

    # Dropdown je nach Art der Notfallversorgung anpassen.
    if c.emergency_type.value == "notfallstation":
        dropdown.extend([{"label": "Einzugsfläche 600km^2", "value": 'area'},
                         {"label": "Grösse der Notfallstation", "value": 'population'}])
    elif c.emergency_type.value == "fire_station":
        dropdown.append({"label": "Gemeindegrenzen", "value": 'borders'})

    if c.air_ambulance_button.get("value"):
        # Air Ambulance soll angezeigt werden
        air_ambulance_data = open_air_ambulance_data()

    if c.emed_button.get("value"):
        # eNotfall soll angezeigt werden
        emed_data = open_emed_data()

    return get_fig(data, c.criteria.value, c.criteria_slider.value, air_ambulance_data, emed_data), \
           view.slider_style(c.criteria.value == "minutes"), \
           dropdown


def load_data(country=None):
    data = []
    if country == "CH":
        with open("daten/notfallstationen_ch.json") as f:
            data.extend(json.load(f)["data"])
    elif country == "LU":
        with open("daten/notfallstationen_lu.json") as f:
            data.extend(json.load(f)["data"])
    else:
        with open("daten/notfallstationen_ch.json") as f:
            data.extend(json.load(f)["data"])
        with open("daten/notfallstationen_lu.json") as f:
            data.extend(json.load(f)["data"])
    return data


def get_top_5_notfallstationen(country):
    data = load_data(country)
    sorted_data = sorted(data, key=lambda x: x["personal_bestand"], reverse=True)
    top_5_data = sorted_data[:5]
    return top_5_data


@app.callback(
    Output('top_5_list', 'children'),
    Input('top_5_country_dropdown', 'value')
)
def update_top_5_list(country):
    print("update_top_5_list", country)
    top_5_data = get_top_5_notfallstationen(country)
    list_items = [html.Li(station['institut']) for station in top_5_data] # Liste mit Nummern voraus
    return list_items


@app.callback(
    Output("stacked_bar_chart", "figure"),
    [Input('dropdown1', 'value'),
     Input('dropdown2', 'value')],
)
def update_stacked_bar_chart(country1, country2):
    print("update_stacked_bar_chart", country1, country2)

    data = open_data()

    data_country1 = [x for x in data if x.location.country == country1]
    data_country2 = [x for x in data if x.location.country == country2]

    population_country1 = 8738791 # CH Total Bevölkerungsgrösse
    population_country2 = 660809 # LU Total Bevölkerungsgrösse

    # plotly.express nicht möglich auf Dash, deshalb go.Bar mit zeilenweiser Generierung
    trace = [
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "stroke_unit"]) / population_country1,
               len([x for x in data_country2 if x.kind == "stroke_unit"]) / population_country2],
            name='Schlaganfallzentrum',
            marker=dict(color='green')
        ),
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "fire_station"]) / population_country1,
               len([x for x in data_country2 if x.kind == "fire_station"]) / population_country2],
            name='Feuerwehrstützpunkt',
            marker=dict(color='red')
        ),
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "notfallstation"]) / population_country1,
               len([x for x in data_country2 if x.kind == "notfallstation"]) / population_country2],
            name='Medizinische Notfallstation',
            marker=dict(color='blue')
        )
    ]

    return {
        'data': trace,
        'layout': go.Layout(
            barmode='stack',
            xaxis=dict(title=dict(text='Land', font=dict(size=20))),  # Schriftgrösse der X-Achsenbeschriftung ändern
            yaxis=dict(title=dict(text='Anzahl Notfallstationen', font=dict(size=20))),  # Schriftgröße der Y-Achsenbeschriftung ändern
            font=dict(size=20),
            hoverlabel=dict(font=dict(size=20))
        )
    }


@app.callback(
    Output("coverage_pie_chart1", "figure"),
    Output("coverage_pie_chart2", "figure"),
    Input('coverage_pie_chart_emergency_type', 'value')
)
def update_pie_chart(emergency_type):
    print("update_pie_chart", emergency_type)

    # pie chart
    labels = ['Medizinische Notfallstation', 'Feuerwehrstützpunkt', 'Schlaganfallzentrum']
    values = [30, 40, 20]

    return {
               'data': [
                   go.Pie(
                       labels=labels,
                       values=values
                   )
               ],
               'layout': go.Layout(
                   title='Schweiz',
                   title_x=0.4,
                   height=700,
                   width=700
               )
           }, {
               'data': [
                   go.Pie(
                       labels=labels,
                       values=values
                   )
               ],
               'layout': go.Layout(
                   title='Luxemburg',
                   title_x=0.4,
                   height=700,
                   width=700
               )
           }


if __name__ == '__main__':
    app.run_server()
