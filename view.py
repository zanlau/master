import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
from dash_daq import ToggleSwitch


# Erstellung eines HTML Files zur besseren Übersicht des Codes


layout = html.Div([
    html.Div(style={'height': '10px'}),  # Leerzeile einfügen
    html.H1("Einzugsgebiete von Notfallversorgungen", style={'text-align': 'center'}),
    html.Div(style={'height': '10px'}),  # Leerzeile einfügen
    dcc.Tabs(id="tabs", value='tab-1', children=[ #2 Tabs für Übersichtlichkeit (1. für visuelle Bestimmung / 2. für Vergleiche)
        dcc.Tab(label='Karte mit Einzugsgebiete', value='tab-1'),
        dcc.Tab(label='Charts für Vergleiche', value='tab-2'),
    ]),
    html.Div(style={'height': '10px'}),  # Leerzeile einfügen
    html.Div(id='page-content', style={"height":"100%"})
    ],
    style={"font-size": "25px"},
)


def row(children):
    return dbc.Row(children, style={"margin-bottom": "2rem"})

def slider_style(display):
    return {"width": "40%", 'display': "block" if display else 'none'}

def emed_style(display):
    return {"width": "40%", 'display': "flex" if display else 'none'}

def render_tab1():
    return html.Div([
        html.Div(
            row([
                dbc.Col(children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Auswahl der Art der Notfallversorgung"),
                        dbc.CardBody([
                            dcc.Dropdown(id="emergency_type",
                                         options=[
                                             {"label": "Medizinische Notfallstation", "value": 'notfallstation'},
                                             {"label": "Feuerwehrstützpunkt", "value": 'fire_station'},
                                             {"label": "Schlaganfallzentrum", "value": 'stroke_unit'}],
                                         value=None,
                                         style={"width": "40%"}),
                            html.Div(
                                children=[
                                    html.Label('eNotfallmedizin', style={'font-size': '25px'}),
                                    ToggleSwitch(id='emed', value=0, style={"margin-left": "15px"}),
                                ],
                                id="emed_button", style=emed_style(False)
                            ),
                        ], style=dict(display='flex'))
                    ])
                ])
            ])),
        html.Div(
            row([
                dbc.Col(children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Kriterium für die Bestimmung der Einzugsgebiete"),
                        dbc.CardBody([
                            html.Div([
                                dcc.Dropdown(id='criteria',
                                             style={"width": "40%"}),
                                html.Div(
                                    children=[
                                        html.Label('Luftrettung', style={'font-size': '25px'}),
                                        ToggleSwitch(id='air_ambulance', value=0, style={"margin-left": "15px"}),
                                    ],
                                    id="air_ambulance_button",
                                    style={"display": "flex"}
                                ),
                                html.Div([
                                    html.P(
                                        "Mit dem Slider kann die Geschwindigkeit des Fahrzeugs gesteurt werden (Angaben in km/h)",
                                    style={'margin-left': '20px'}),
                                    dcc.Slider(0, 100, 5,
                                               value=50,
                                               id='criteria_slider'),
                                ], id="criteria_slider_div", style=slider_style(False)),
                            ], style=dict(display='flex'))
                        ])
                    ])
                ])
            ])),
        html.Div(
            row([
                dbc.Col(children=[
                    dbc.Card([
                        dbc.CardHeader(children="Karte zur Bestimmung der Einzugsgebiete",
                                       id="world_map_header"),
                        dcc.Graph(id="graph"),
                        dcc.Interval(id="my_interval", interval=2000, n_intervals=0, disabled=False),
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card([
                        dbc.CardHeader("Art der Notfallversorgung"),
                        dbc.CardBody([
                                html.Div([
                                    html.Span(style={"color": "blue", "margin-right": "5px", "display": "inline-flex",
                                                     "align-items": "center"}, children=["\u25CF"]),
                                    html.Span("Medizinische Notfallstation",
                                              style={"color": "black", "display": "inline"})
                                ]),
                                html.Div([
                                    html.Span(style={"color": "red", "margin-right": "5px", "display": "inline-flex",
                                                     "align-items": "center"}, children=["\u25CF"]),
                                    html.Span("Feuerwehrstützpunkt", style={"color": "black", "display": "inline"})
                                ]),
                                html.Div([
                                    html.Span(style={"color": "green", "margin-right": "5px", "display": "inline-flex",
                                                     "align-items": "center"}, children=["\u25CF"]),
                                    html.Span("Schlaganfallzentrum", style={"color": "black", "display": "inline"})
                                ]),
                            ])
                    ])
                ], width=2)
            ]))
    ])


def render_tab2():
    return html.Div([
        html.Div([
            dbc.Col(children=[
                dbc.Card([
                    dbc.CardHeader("Top 5 Notfallversorgungen"),
                    dbc.CardBody([
                        html.P("Hier werden die fünf grössten medizinischen Notfallstationen anhand des Personalbestands ersichtlich."),
                        dcc.Dropdown(
                            id='top_5_country_dropdown',
                            options=[
                                {'label': 'Schweiz', 'value': 'CH'},
                                {'label': 'Luxemburg', 'value': 'LU'},
                            ],
                            placeholder="Land auswählen",
                        ),
                        html.Div(style={'padding-top': '20px'}),  # Zeilenabstand
                        html.Ol(id='top_5_list', type="1")
                    ])
                ])
            ])
        ]),
        html.Div(style={'padding-top': '20px'}),  # Zeilenabstand
        dbc.Card([
            dbc.CardHeader("Anzahl Notfallversorgungen"),
            dbc.CardBody([
                html.P( #Notiz / Hinweis für Balkendiagramm für einfacheres Verständnis
                    "Die Anzahl der Notfallstationen wird auf die Bevölkerungsgrösse berechnet."),
                html.Div([
                    dbc.Col(children=[
                        dbc.Card([
                            dbc.CardHeader(
                                "Land 1"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='dropdown1',
                                    options=[
                                        {'label': 'Schweiz', 'value': 'CH'},
                                        {'label': 'Luxemburg', 'value': 'LU'},
                                    ],
                                    value="CH",
                                ),
                                html.Div(id='dropdown1_output')
                            ])
                        ])
                    ]),
                    dbc.Col(children=[
                        dbc.Card([
                            dbc.CardHeader(
                                "Land 2"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='dropdown2',
                                    options=[
                                        {'label': 'Schweiz', 'value': 'CH'},
                                        {'label': 'Luxemburg', 'value': 'LU'},
                                    ],
                                    value="LU",
                                ),
                                html.Div(id='dropdown2_output')
                            ])
                        ])
                    ]),
                ], className='row'),
                dcc.Graph(
                    id='stacked_bar_chart',
                ),
            ]),
        ]),
        html.Div(style={'padding-top': '20px'}),  # Zeilenabstand
        dbc.Col(children=[
            dbc.Card([
                dbc.CardHeader("Abdeckung der Notfallversorgung"),
                dbc.CardBody([
                    html.Div([
                        dbc.Col(children=[
                            dbc.Card([
                                dbc.CardHeader(
                                    "Land 1"),
                                dbc.CardBody([
                                    dcc.Dropdown(
                                        id='pie_chart1_country',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="CH",
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Dropdown(
                                        id='pie_chart1_municipality',
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    html.Div(
                                        html.P(id="coverage_pie_chart1_population"),
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Graph(id='coverage_pie_chart1'),
                                    html.Div(style={'padding-top': '20px'}),

                                ])
                            ])
                        ]),
                        dbc.Col(children=[
                            dbc.Card([
                                dbc.CardHeader(
                                    "Land 2"),
                                dbc.CardBody([
                                    dcc.Dropdown(
                                        id='pie_chart2_country',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="LU",
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Dropdown(
                                        id='pie_chart2_municipality',
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    html.Div(
                                        html.P(id="coverage_pie_chart2_population"),
                                    ),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Graph(id='coverage_pie_chart2')
                                ])
                            ])
                        ]),
                    ], className='row'),
                    html.Div(style={'padding-top': '20px'}),  # Zeilenabstand
                ])
            ])
        ])
    ])
