import json
import sys

import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.graph_objects as go
from dash import html, ctx
from dash.dependencies import Input, Output
from flask import Flask
from shapely.geometry import Point

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


class Cord:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

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
        return f"{self.coordinates}"


class NFS:
    def __init__(self, name, kind, location, personal=None):
        self.name = name or f"{kind} {location}"
        self.kind = kind
        self.location = location
        self.personal = personal
        self.color = {"notfallstation": "blue", "stroke_unit": "green", "fire_station": "red"}[self.kind]


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

        # data.extend([NFS(x.get("tags", {}).get("name"), "fire_station", Location(Cord(x.get("lat"), x.get("lon")), "CH")) for x in elements])
        # lat und lon waren nicht in nodes
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
                        # print(cord)
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
                        # print(cord)
                data.append(NFS(name, "fire_station", Location(cord, "LU")))

        # data.extend([NFS(x.get("tags", {}).get("name"), "fire_station", Location(Cord(x.get("lat"), x.get("lon")), "LU")) for x in ["elements"])

    return data


# Diagramme im Dashboard generieren
# Positionen in OpenStreetMap erzeugen
def get_fig(data, criteria, speed):
    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=[x.location.coordinates.lat for x in data],
            lon=[x.location.coordinates.lon for x in data],
            marker=dict(size=15, color=[x.color for x in data]),
            text=[f"Name: {x.name}<br>Kind: {x.kind}" for x in data],
            textfont=dict(size=16)
        )
    )
    if criteria == "minutes":
        d = {"geometry": [x.location.coordinates.to_Point() for x in data]}
        gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

        cgeo = (
            gdf.set_crs("epsg:4326")
                .pipe(lambda d: d.to_crs(d.estimate_utm_crs()))["geometry"]
                .centroid.buffer(speed*250)  # 12.5km (50 km/h, 15 Minuten = 12.5km)
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
        with open("daten/population_lu_gemeinde.json") as f:
            pop_data = json.load(f)["data"]

        # for notfalzentrum in notfalzentren:
        #   pop_remaining = notfalzentrum.personalbestand * 50
        #  nächste_gemainde = None
        # for gemeinde in gemeinden:
        #    lat/long vergleichen und nächste auswählen
        #   ausser es hat eine farbe
        # nächste_gemainde.farbe = "irgendöpis"

        fig.add_trace(
            go.Choroplethmapbox(
                geojson=json.load(open("daten/borders.geojson")),
                locations=[f'relation/{x["osm_id"]}' for x in pop_data],
                z=[x["population"] for x in pop_data],
            )
        )

        fig.update_layout(
            height=1500,
            width=2500,
            margin={"r": 10, "t": 10, "b": 10, "l": 10},
            autosize=True,
            mapbox=dict(style="open-street-map", center=dict(lat=47.95, lon=7.45), zoom=7, uirevision=len(data)),
            # Deaktivierung der automatischen Rückkehr zur Standardposition
        )

    elif criteria == "full_coverage":
        print("HELLO")
        with open("daten/countries.geojson") as f:
            borders = json.load(f)
            for e in borders["features"]:
                if e["properties"]["ADMIN"] == "Switzerland":
                    border_switzerland = {"features": [e]}
                    break

        fig.add_trace(
            go.Choroplethmapbox(
                geojson=border_switzerland,
                colorscale="Viridis",  # Farbskala für den Float-Fill
                colorbar=dict(
                    title="Float-Fill",
                )
            )
        )
    elif criteria == "borders":
        with open("daten/population_lu_gemeinde.json") as f:
            pop_data = json.load(f)["data"]

        print(data)
        print(pop_data)

        fig.add_trace(
            go.Choroplethmapbox(
                geojson=json.load(open("daten/borders.geojson")),
                locations=[f'relation/{x["osm_id"]}' for x in pop_data],
                z=[x["population"] for x in pop_data],
            )
        )

    # open street map mit Standardposition
    fig.update_layout(
        height=1500,
        width=2500,
        margin={"r": 10, "t": 10, "b": 10, "l": 10},
        autosize=True,
        mapbox=dict(style="open-street-map", center=dict(lat=47.95, lon=7.45), zoom=7, uirevision=len(data)),
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
        }
    },
)
def update_map(all_inputs):
    data = open_data()
    c = ctx.args_grouping["all_inputs"]

    data = filter_data_based_on_criteria(data, c.emergency_type.value)

    dropdown = [{"label": "15 Minuten", "value": 'minutes'},
                {"label": "Vollständige Abdeckung", "value": 'full_coverage'}]

    if c.emergency_type.value == "notfallstation":
        dropdown.extend([{"label": "Einzugsfläche 600km^2", "value": 'area'},
                         {"label": "Grösse der Notfallstation", "value": 'population'}])
    elif c.emergency_type.value == "fire_station":
        dropdown.append({"label": "Gemeindegrenzen", "value": 'borders'})

    return get_fig(data, c.criteria.value, c.criteria_slider.value), \
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
    list_items = [html.Li(station['institut']) for station in top_5_data]
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

    trace = [
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "notfallstation"]),
               len([x for x in data_country2 if x.kind == "notfallstation"])],
            name='Medizinische Notfallstation'
        ),
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "stroke_unit"]),
               len([x for x in data_country2 if x.kind == "stroke_unit"])],
            name='Schlaganfallzentrum'
        ),
        go.Bar(
            x=[country1, country2],
            y=[len([x for x in data_country1 if x.kind == "fire_station"]),
               len([x for x in data_country2 if x.kind == "fire_station"])],
            name='Feuerwehrstützpunkt'
        )
    ]

    return {
        'data': trace,
        'layout': go.Layout(
            barmode='stack',
            title='Anzahl Notfallstationen',  # Titel des Charts
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
