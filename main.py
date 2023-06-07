import json
import random
import sys

import dash
import html
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, ctx
from dash.dependencies import Input, Output
import dash.dependencies as dependencies
from flask import Flask
from openpyxl import load_workbook
from plotly.subplots import make_subplots
from shapely.geometry import Point


if dash.__version__ != "2.10.2":
    print("dash version 2.10.2 required!")
    sys.exit()


def h1(text): return html.H1(text, style={'text-align': 'center'})


def h4(text): return html.H4(text, style={'text-align': 'left'})


# Interaktionsmöglichkeiten
def emergency_dropdown(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "Medizinische Notfallstation", "value": 'notfallstation'},
                            {"label": "Feuerwehrstützpunkt", "value": 'fire_station'},
                            {"label": "Schlaganfallzentrum", "value": 'stroke_unit'}],
                        multi=False,
                        value='emergency_type',
                        style={"width": "40%"})


def area_criteria(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "15 Minuten", "value": 'minutes'},
                            {"label": "Gebietsfläche", "value": 'area'},
                            {"label": "Bevölkerungsgrösse", "value": 'population'}],
                        multi=False,
                        value='criteria',
                        style={"width": "40%"})


def row(children):
    return dbc.Row(children, style={"margin-bottom": "2rem"})


server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "Dashboard Notfallversorgungen"

app.layout = html.Div([
    html.Div(style={'height': '10px'}), #Leerzeile einfüge
    h1("Einzugsgebiete von Notfallversorgungen"),
    html.Div(style={'height': '10px'}), #Leerzeile einfügen
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Karte mit Einzugsgebiete', value='tab-1'),
        dcc.Tab(label='Charts für Vergleiche', value='tab-2'),
    ]),
    html.Div(id='page-content')
])


@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Div(
                row([
                    dbc.Col(width=12, children=[
                        dbc.Card([
                            dbc.CardHeader(
                                "Notfallart"),
                            dbc.CardBody([
                                emergency_dropdown('emergency_type')
                            ])
                        ])
                    ])
                ])),
            html.Div(
                row([
                    dbc.Col(width=12, children=[
                        dbc.Card([
                            dbc.CardHeader(
                                "Kriterien der Einzugsgebiete"),
                            dbc.CardBody([
                                area_criteria('criteria')
                            ])
                        ])
                    ])
                ])),
            html.Div(
                row([
                    dbc.Col(width=12, children=[
                        dbc.Card([
                            dbc.CardHeader(children="Karte zur Bestimmung der Einzugsgebiete",
                                           id="world_map_header"),
                            dcc.Graph(id="graph"),
                            dcc.Interval(id="my_interval", interval=2000, n_intervals=0, disabled=False),
                        ])
                    ])
                ]))
        ])


    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                dbc.Col(width=2, children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Land 1"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='Dropdown 1',
                                options=[
                                    {'label': 'Schweiz', 'value': 'CH'},
                                    {'label': 'Luxemburg', 'value': 'LU'}
                                ],
                                value='option1'
                            ),
                            html.Div(id='dropdown1_output')
                        ])
                    ])
                ]),
                dbc.Col(width=2, children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Land 2"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='dropdown2',
                                options=[
                                    {'label': 'Schweiz', 'value': 'CH'},
                                    {'label': 'Luxemburg', 'value': 'LU'}
                                ],
                                value='option2'
                            ),
                            html.Div(id='dropdown2_output')
                        ])
                    ])
                ]),
            ], className='row'),
            dcc.Graph(
                id='stacked-bar-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=x_data,
                            y=y_data,
                            marker=dict(color='blue')  # Farbe der Balken
                        )
                    ],
                    'layout': go.Layout(
                        title='Anzahl Notfallstationen',  # Titel des Charts
                        xaxis=dict(title='Länder'),  # Beschriftung der x-Achse
                        yaxis=dict(title='Anzahl')  # Beschriftung der y-Achse
                    )
                }
            ),
            dbc.Col(width=4, children=[
                dbc.Card([
                    dbc.CardHeader("Abdeckung der Notfallversorgung"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='emergency_type',
                            options=[
                                {'label': 'Medizinische Notfallstation', 'value': 'NFS'},
                                {'label': 'Feuerwehrstützpunkt', 'value': 'fire_station'},
                                {'label': 'Schlaganfallzentrum', 'value': 'stroke_unit'}
                            ],
                            value='emergency_type'
                        ),
                        html.Div(id='emergency_type')
                    ])
                ])
            ]),
            html.Div([
                dcc.Graph(
                    id='pie-chart',
                    figure={
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
                    }
                )
            ], className='six columns', style={'display': 'inline-block'}),
            html.Div([
                dcc.Graph(
                    id='pie-chart2',
                    figure={
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
                )
        ], className='six columns', style={'display': 'inline-block'})
    ])



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
        data.extend([NFS(x["institut"], "notfallstation", Location(Cord(x["lat"], x["lon"]), "CH"), x["personal_bestand"]) for x in json.load(f)["data"]])
    with open("daten/notfallstationen_lu.json") as f:
        data.extend([NFS(x["institut"], "notfallstation", Location(Cord(x["lat"], x["lon"]), "LU"), x["personal_bestand"]) for x in json.load(f)["data"]])
    with open("daten/stroke_units_ch.json") as f:
        data.extend([NFS(x["institut"], "stroke_unit", Location(Cord(x["lat"], x["lon"]), "CH")) for x in json.load(f)["data"]])
    with open("daten/stroke_untis_lu.json") as f:
        data.extend([NFS(x["institut"], "stroke_unit", Location(Cord(x["lat"], x["lon"]), "LU")) for x in json.load(f)["data"]])
    with open("daten/fire_station_ch.json") as f:
        elements = json.load(f)["elements"]

        #data.extend([NFS(x.get("tags", {}).get("name"), "fire_station", Location(Cord(x.get("lat"), x.get("lon")), "CH")) for x in elements])

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
                        cord = Cord(sum(x[0] for x in cords)/len(cords), sum(x[1] for x in cords)/len(cords))
                        #print(cord)
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
                        cord = Cord(sum(x[0] for x in cords)/len(cords), sum(x[1] for x in cords)/len(cords))
                        #print(cord)
                data.append(NFS(name, "fire_station", Location(cord, "LU")))

        #data.extend([NFS(x.get("tags", {}).get("name"), "fire_station", Location(Cord(x.get("lat"), x.get("lon")), "LU")) for x in ["elements"])

    return data


# Diagramme im Dashboard generieren
# Positionen in OpenStreetMap erzeugen
def get_fig(data, criteria):
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

    if criteria == "area":
        # prep geometry
        d = {"geometry": [x.location.coordinates.to_Point() for x in data]}
        gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

        cgeo = (
            gdf.set_crs("epsg:4326")
                .pipe(lambda d: d.to_crs(d.estimate_utm_crs()))["geometry"]
                .centroid.buffer(13819) #600km^2 Fläche
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

        #for notfalzentrum in notfalzentren:
         #   pop_remaining = notfalzentrum.personalbestand * 50
          #  nächste_gemainde = None
           # for gemeinde in gemeinden:
            #    lat/long vergleichen und nächste auswählen
             #   ausser es hat eine farbe
            #nächste_gemainde.farbe = "irgendöpis"

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
    inputs={
        "all_inputs": {
            "my_interval": Input("my_interval", "value"),
            "emergency_type": Input("emergency_type", "value"),
            "criteria": Input("criteria", "value"),
        }
    },
)
def update_map(all_inputs):
    data = open_data()
    c = ctx.args_grouping["all_inputs"]
    if c.emergency_type.triggered:
        print(f"{c.emergency_type.value}")
        data = filter_data_based_on_criteria(data, c.emergency_type.value)
    elif c.criteria.triggered:
        print(f"{c.criteria.value}")
    elif c.my_interval.triggered:
        print(f"{c.my_interval.value}")

    print(len(data))

    return get_fig(data, c.criteria.value)

x_data = ['A', 'B', 'C', 'D']
y_data = [10, 8, 12, 6]

labels = ['Medizinische Notfallstation C', 'Feuerwehrstützpunkt', 'Schlaganfallzentrum']
values = [30, 40, 20]


if __name__ == '__main__':
    app.run_server()