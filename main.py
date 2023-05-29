import json
import random
import dash
import html
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, ctx
from dash.dependencies import Input, Output
from flask import Flask
from openpyxl import load_workbook
from plotly.subplots import make_subplots



def h1(text): return html.H1(text, style={'text-align': 'center'})

def h4(text): return html.H4(text, style={'text-align': 'left'})

#Interaktionsmöglichkeiten
def emergency_dropdown(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "Medizinische Notfallstation", "value": 'notfallstation'},
                            {"label": "Feuerwehrstützpunkt", "value": 'fire_station'},
                            {"label": "Schlaganfallzentrum", "value": 'stroke_unit'}],
                        multi=False,
                        value='emergency',
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

app.layout = html.Div(
    [
        h1("Einzugsgebiete von Notfallversorgungen"),

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
        ]),
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
        ]),
        row([
            dbc.Col(width=12, children=[
                dbc.Card([
                    dbc.CardHeader(children="Karte zur Bestimmung der Einzugsgebiete",
                        id="world_map_header"),
                    dcc.Graph(id = "graph"),
                    dcc.Interval(id="my_interval", interval=2000, n_intervals=0, disabled=False),
                ])
            ])
        ]),
    ]
)

class Cord:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class NFS:
    def __init__(self, kind, country, coordinates):
        self.kind = kind
        self.country = country
        self.coordinates = coordinates
        self.color = {"notfallstation": "blue", "stroke_unit": "green", "fire_station": "red"}[self.kind]

def open_data():
    data = []
    with open("daten/notfallstationen_ch.json") as f:
        data.extend([NFS("notfallstation", "CH", Cord(x["lat"], x["lon"])) for x in json.load(f)["data"]])
    with open("daten/notfallstationen_lu.json") as f:
        data.extend([NFS("notfallstation", "LU", Cord(x["lat"], x["lon"])) for x in json.load(f)["data"]])
    with open("daten/stroke_units_ch.json") as f:
        data.extend([NFS("stroke_unit", "CH", Cord(x["lat"], x["lon"])) for x in json.load(f)["data"]])
    with open("daten/stroke_untis_lu.json") as f:
        data.extend([NFS("stroke_unit", "LU", Cord(x["lat"], x["lon"])) for x in json.load(f)["data"]])
    with open("daten/fire_station_ch.json") as f:
        data.extend([NFS("fire_station", "CH", Cord(x.get("lat"), x.get("lon"))) for x in json.load(f)["elements"]])
    with open("daten/fire_station_lu.json") as f:
        data.extend([NFS("fire_station", "LU", Cord(x.get("lat"), x.get("lon"))) for x in json.load(f)["elements"]])
    return data


#Diagramme im Dashboard generieren
#Positionen in OpenStreetMap erzeugen
def get_fig(data):
    fig = go.Figure()

    fig.add_trace(
            go.Scattermapbox(
                lat=[x.coordinates.lat for x in data],
                lon=[x.coordinates.lon for x in data],
                mode="markers",
                marker=dict(size=15, color=[x.color for x in data]),
            )
        )

    # open street map mit Standardposition
    fig.update_layout(
            height=1500,
            width=2500,
            margin={"r": 10, "t": 10, "b": 10, "l": 10},
            autosize=False,
            mapbox=dict(style="open-street-map", center=dict(lat=47.95, lon=7.45), zoom=7, uirevision="true"), #Deaktivierung der automatischen Rückkehr zur Standardposition
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
            "emergency_type": Input("emergency_type", "value"),
            "my_interval": Input("criteria", "value")
        }
    },
)
def update_map(all_inputs):
    data = open_data()
    c = ctx.args_grouping.all_inputs
    if c.emergency_type.triggered:
        print(f"{c.emergency_type.value}")
        data = filter_data_based_on_criteria(data, c.emergency_type.value)
    elif c.my_interval.triggered:
        print(f"{c.my_interval.value}")

    return get_fig(data)


if __name__ == '__main__':
    app.run_server()