import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html

layout = html.Div([
    html.Div(style={'height': '20px'}),  # Leerzeile einfüge
    html.H1("Einzugsgebiete von Notfallversorgungen", style={'text-align': 'center'}),
    html.Div(style={'height': '20px'}),  # Leerzeile einfügen
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Karte mit Einzugsgebiete', value='tab-1'),
        dcc.Tab(label='Charts für Vergleiche', value='tab-2'),
    ]),
    html.Div(style={'height': '20px'}),  # Leerzeile einfügen
    html.Div(id='page-content')
])


def row(children):
    return dbc.Row(children, style={"margin-bottom": "2rem"})


def render_tab1():
    return html.Div([
        html.Div(
            row([
                dbc.Col(width=12, children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Notfallart"),
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
                dbc.Col(width=12, children=[
                    dbc.Card([
                        dbc.CardHeader(
                            "Kriterien der Einzugsgebiete"),
                        dbc.CardBody([
                            dcc.Dropdown(id='criteria',
                                         options=[
                                             {"label": "15 Minuten", "value": 'minutes'},
                                             {"label": "Einzugsfläche 600km^2", "value": 'area'},
                                             {"label": "Grösse der Notfallstation", "value": 'population'},
                                             {"label": "Vollständige Abdeckung", "value": 'float fill'}],
                                         style={"width": "40%"})
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


def render_tab2():
    return html.Div([
        html.Div([
            dbc.Col(children=[
                dbc.Card([
                    dbc.CardHeader("Top 5 Notfallversorgungen"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='top_5_country_dropdown',
                            options=[
                                {'label': 'Schweiz', 'value': 'CH'},
                                {'label': 'Luxemburg', 'value': 'LU'}
                            ],
                            placeholder="Land auswählen"
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
                                        {'label': 'Luxemburg', 'value': 'LU'}
                                    ],
                                    value="CH"
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
                                    value="LU"
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
                    dcc.Dropdown(
                        id='coverage_pie_chart_emergency_type',
                        options=[
                            {'label': 'Medizinische Notfallstation', 'value': 'NFS'},
                            {'label': 'Feuerwehrstützpunkt', 'value': 'fire_station'},
                            {'label': 'Schlaganfallzentrum', 'value': 'stroke_unit'}
                        ]
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
