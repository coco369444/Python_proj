# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 20:53:05 2022

@author: corentin
"""

    
    
import dash
import dash_core_components as dcc
import dash_html_components as html   
from dash.dependencies import Input, Output
from graph_plotly import create_fig
import plotly.graph_objects as go
    
app = dash.Dash(__name__)

all_options = {
    'EUR': ['BNP', 'Revolut', 'JB'],
    'CHF': ['CS', 'Revolut', 'JB'],
    'USD': ['JB']
}

app.layout = html.Div([
    html.Div([
        html.Label('Currency'),
        dcc.RadioItems(
            id="currency",
            options=[
                {'label': 'EUR', 'value': 'EUR'},
                {'label': 'CHF', 'value': 'CHF'},
                {'label': 'USD', 'value': 'USD'},
                #{'label': 'All', 'value': 'All'},
            ],
            value='CHF',
            labelStyle={'display': 'block'}
        ),
    
    html.Br(),
    html.Label('Normalised Expenses and incomes'),
    
    dcc.RadioItems(
        id="normalized",
        options=[
            {'label': 'Yes', 'value': True},
            {'label': 'No', 'value': False},
            
            ],
            value=False,
            labelStyle={'display': 'incline-block'}
        ),
    ], style={'padding': 10, 'flex': 1}),
    
    html.Br(),
    
    html.Div([
    #    html.Label('Checkboxes'),
    #    dcc.Checklist(
    #        id="banks",
    #        options=[
    #            {'label': 'BNP (EUR)', 'value': 'BNP'},
    #            {'label': 'CS (CHF)', 'value': 'CS'},
    #            {'label': 'Revolut (EUR,CHF)', 'value': 'Revolut'},
    #            {'label': 'JB (EUR, CHF, USD)', 'value': 'JB'},
    #        ],
    #        value=['BNP', 'CS','Revolut','JB'],
    #        labelStyle={'display': 'block'}
    #    ),
        html.Label('Banks'),
        dcc.Checklist(id='Banks',value="JB",labelStyle={'display': 'block'}),

        html.Br(),
        html.Label('Period (Months)'),
        dcc.Slider(
            id="Period",
            min=1,
            max=12,
            marks={i: '{}'.format(i) if i == 1 else str(i) for i in range(1, 13)},
            value=6,
        ),
    ], style={'padding': 10, 'flex': 1}),
    html.Hr(),
    
    #], style={'display': 'flex', 'flex-direction': 'row'}),
    
    dcc.Graph(id='graph-with-slider')
    
    ])

@app.callback(
    Output('Banks', 'options'),
    Input('currency', 'value'))
def set_cities_options(currency):
    return [{'label': i, 'value': i} for i in all_options[currency]]

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('currency', 'value'),
    Input('normalized', 'value'),
    Input('Banks', 'value'),
    Input('Period', 'value'),)
def update_figure(currency,normalized,banks,Period):
    #filtered_df = df[df.year == selected_year]
    
    if banks==None :
        fig=go.Figure()
    else :
        fig = create_fig(currency,banks,normalized,Period)
    #fig.update_layout(transition_duration=500)
    #fig.update_layout(transition_duration=500)

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)