import json
import random
import dash
import html
import dash_bootstrap_components as dbc
from dash import dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from flask import Flask
from openpyxl import load_workbook
wb = load_workbook('daten/notfallstationen_ch.xlsx')
from plotly.subplots import make_subplots






def h1(text): return html.H1(text, style={'text-align': 'center'})

def h4(text): return html.H4(text, style={'text-align': 'left'})

def graph(id): return dcc.Graph(id=id, figure={})

#Interaction possibilities
def emergency_dropdown(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "Medizinische Notfallstation", "value": 'nfs'},
                            {"label": "Feuerwehrstützpunk", "value": 'fire_fighter'},
                            {"label": "Schlaganfallzentren", "value": 'stroke'}],
                        multi=False,
                        value='emergency',
                        style={"width": "40%"})

def area_criteria(id):
    return dcc.Dropdown(id=id,
                        options=[
                            {"label": "15 Minuten", "value": 'minutes'},
                            {"label": "Gebietsfläche", "value": 'kilometer'},
                            {"label": "Bevölkerungsgrösse", "value": 'population'}],
                        multi=False,
                        value='minutes',
                        style={"width": "40%"})

def row(children):
    return dbc.Row(children, style={"margin-bottom": "2rem"})


server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.layout = html.Div()
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
                        emergency_dropdown('emergency_art')
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
                        area_criteria('einzugsgebiete')
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

#create graphs in dashboard
#map in dash to deploy stations (OSM)
def get_fig():
    with open("daten/notfallstationen_ch.json") as f1, open("daten/notfallstationen_lu.json") as f2,\
            open("daten/stroke_unit_ch.json") as f3, open("daten/stroke_unit_lu.json") as f4,\
            open("daten/fire_station_ch.json") as f5, open("daten/fire_station_lu.json") as f6:
        data_1 = json.load(f1)
        data_2 = json.load(f2)
        data_3 = json.load(f3)
        data_4 = json.load(f4)
        data_5 = json.load(f5)
        data_6 = json.load(f6)


    fig = go.Figure()
    # blue point - should be in center of map , vhy is not ?
    fig.add_trace(
            go.Scattermapbox(
                lat=[x["lat"] for x in data_1["data"]] + [x["lat"] for x in data_2["data"]],
                lon=[x["lon"] for x in data_1["data"]] + [x["lon"] for x in data_2["data"]],
                mode="markers",
                marker=go.scattermapbox.Marker(size=15),
            )
        )

    # open street map with center at lat:lon
    fig.update_layout(
            height=1500,
            width=2500,
            margin={"r": 2, "t": 2, "b": 2, "l": 2},
            autosize=False,
            mapbox=dict(style="open-street-map", center=dict(lat=47.95, lon=7.45), zoom=7),
        )
    return fig

@app.callback(
    Output("graph", "figure"),
    Input("my_interval", "n_intervals"))
def update_bar_chart(dummy):
    return get_fig()


if __name__ == '__main__':
    app.run_server()