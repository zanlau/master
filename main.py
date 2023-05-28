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

def graph(id): return dcc.Graph(id=id, figure={})

#Interaktionsmöglichkeiten
def emergency_dropdown(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "Medizinische Notfallstation", "value": 'nfs'},
                            {"label": "Feuerwehrstützpunkt", "value": 'fire_station'},
                            {"label": "Schlaganfallzentrum", "value": 'stroke'}],
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

#Diagramme im Dashboard generieren
#Positionen in OpenStreetMap erzeugen
def get_fig(emergency_type):
    with open("daten/notfallstationen_ch.json") as f1:
        data_1 = json.load(f1)
    with open("daten/notfallstationen_lu.json") as f2:
        data_2 = json.load(f2)
    with open("daten/stroke_units_ch.json") as f3:
        data_3 = json.load(f3)
    with open("daten/stroke_untis_lu.json") as f4:
        data_4 = json.load(f4)
    with open("daten/fire_station_ch.json") as f5:
        data_5 = json.load(f5)
        data_5["data"] = data_5.pop("elements")
    with open("daten/fire_station_lu.json") as f6:
        data_6 = json.load(f6)
        data_6["data"] = data_6.pop("elements")

    colors = ["blue", "green", "red"]

    fig = go.Figure()

    fig.add_trace(
            go.Scattermapbox(
                lat=[x["lat"] for x in data_1["data"]] + [x["lat"] for x in data_2["data"]]
                    + [x["lat"] for x in data_3["data"]] + [x["lat"] for x in data_4["data"]]
                    + [x.get("lat", None) for x in data_5["data"]] + [x.get("lat", None) for x in data_6["data"]],
                lon=[x["lon"] for x in data_1["data"]] + [x["lon"] for x in data_2["data"]]
                    + [x["lon"] for x in data_3["data"]] + [x["lon"] for x in data_4["data"]]
                    + [x.get("lon", None) for x in data_5["data"]] + [x.get("lon", None) for x in data_6["data"]],
                mode="markers",
                marker=dict(size=15, color=[colors[0]] * len(data_1["data"])
                                                              + [colors[0]] * len(data_2["data"])
                                                              + [colors[1]] * len(data_3["data"])
                                                              + [colors[1]] * len(data_4["data"])
                                                              + [colors[2]] * len(data_5["data"])
                                                              + [colors[2]] * len(data_6["data"])),
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



def filter_data_based_on_criteria(emergency_type):
    # Filter basierend auf Notfallart + Laden der Daten
    if emergency_type == 'Medizinische Notfallstation':
        df_1 = pd.read_json("daten/notfallstationen_ch.json")
        df_2 = pd.read_json("daten/notfallstationen_lu.json")
        return pd.concat([df_1, df_2])
    elif emergency_type == 'Schlaganfallzentrum':
        df_3 = pd.read_json("daten/stroke_units_ch.json")
        df_4 = pd.read_json("daten/stroke_untis_lu.json")
        return pd.concat([df_3, df_4])
    elif emergency_type == 'Feuerwehrstützpunkt':
        df_5 = pd.read_json("daten/fire_station_ch.json")
        df_6 = pd.read_json("daten/fire_station_lu.json")
        return pd.concat([df_5, df_6])
    raise "Keine gültige Notfallart" #wenn keine der obigen Arten


@app.callback(
    Output("graph", "figure"),
    inputs={
        "all_inputs": {
            "emergency_type": Input("emergency_type", "value"),
            "my_interval": Input("criteria", "value")
        }
    },
)
def update_bar_chart(all_inputs):
    #data = filter_data_based_on_criteria(value)
    c = ctx.args_grouping.all_inputs
    if c.emergency_type.triggered:
        print(f"{c.emergency_type.value}")
    elif c.my_interval.triggered:
        print(f"{c.my_interval.value}")
    fig = get_fig(c.emergency_type.value)
    return fig

if __name__ == '__main__':
    app.run_server()