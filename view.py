import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
from dash_daq import ToggleSwitch

layout = html.Div([
    html.Div(style={'height': '10px'}),  # Leerzeile einfüge
    html.H1("Einzugsgebiete von Notfallversorgungen", style={'text-align': 'center'}),
    html.Div(style={'height': '10px'}),  # Leerzeile einfügen
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Karte mit Einzugsgebiete', value='tab-1'),
        dcc.Tab(label='Charts für Vergleiche', value='tab-2'),
    ]),
    html.Div(style={'height': '10px'}),  # Leerzeile einfügen
    html.Div(id='page-content')
    ],
    style={"font-size": "25px"},
)


def row(children):
    return dbc.Row(children, style={"margin-bottom": "2rem"})

def slider_style(display):
    return {"width": "40%", 'display': "block" if display else 'none'}

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
                                         style={"width": "40%"})
                        ])
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
                                        ToggleSwitch(id='air_ambulance', value=0),
                                        html.Div(id='output'),
                                    ],
                                    id="air_ambulance_button",
                                ),
                                dbc.Col(
                                    width=1,  # Breite der Spalte anpassen
                                ),
                                html.Div([
                                    html.P(
                                        "Mit dem Slider kann die Geschwindigkeit des Fahrzeugs gesteurt werden (Angaben in km/h)",
                                    style={'margin-left': '20px'}),
                                    dcc.Slider(0, 100, 5,
                                               value=50,
                                               id='criteria_slider'),
                                ], id="criteria_slider_div")
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
                html.P(
                    "Die Anzahl der Notfallstationen wird auf die Bevölkerungsgrösse berechnet."),
                html.Div([
                    dbc.Col(width=2, children=[
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
                    dbc.Col(width=2, children=[
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
                        dbc.Col(width=2, children=[
                            dbc.Card([
                                dbc.CardHeader(
                                    "Land 1"),
                                dbc.CardBody([
                                    dcc.Dropdown(
                                        id='pie_chart_dropdown1',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="CH",
                                    ),
                                    html.Div(id='pie_chart_dropdown1_output'),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Dropdown(
                                        id='pie_chart_dropdown3',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="CH",
                                    ),
                                    html.Div(id='pie_chart_dropdown3_output')
                                ])
                            ])
                        ]),
                        dbc.Col(width=2, children=[
                            dbc.Card([
                                dbc.CardHeader(
                                    "Land 2"),
                                dbc.CardBody([
                                    dcc.Dropdown(
                                        id='pie_chart_dropdown2',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="LU",
                                    ),
                                    html.Div(id='pie_chart_dropdown2_output'),
                                    html.Div(style={'padding-top': '20px'}),
                                    dcc.Dropdown(
                                        id='pie_chart_dropdown3',
                                        options=[
                                            {'label': 'Schweiz', 'value': 'CH'},
                                            {'label': 'Luxemburg', 'value': 'LU'},
                                        ],
                                        value="CH",
                                    ),
                                    html.Div(id='pie_chart_dropdown3_output')
                                ])
                            ])
                        ]),
                    ], className='row'),
                    html.Div(style={'padding-top': '20px'}),
                    dbc.Col(width=2, children=[
                        dbc.Card([
                            dbc.CardHeader(
                                "Art der Notfallversorgung"),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='coverage_pie_chart_emergency_type',
                                    options=[
                                        {'label': 'Medizinische Notfallstation', 'value': 'NFS'},
                                        {'label': 'Feuerwehrstützpunkt', 'value': 'fire_station'},
                                        {'label': 'Schlaganfallzentrum', 'value': 'stroke_unit'}
                                    ],
                                ),
                                html.Div([
                                    html.Div([
                                        dcc.Graph(
                                            id='coverage_pie_chart1'
                                        )
                                    ], className='six columns', style={'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Graph(
                                            id='coverage_pie_chart2'
                                        )
                                    ], className='six columns', style={'display': 'inline-block'}),
                                ])
                            ])
                        ])
                    ]),
                    html.Div(style={'padding-top': '20px'}),  # Zeilenabstand
                ])
            ])
        ])
    ])
