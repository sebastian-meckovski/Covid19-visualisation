import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.request as urllib2


app = dash.Dash(__name__)
server = app.server


def openurl():
    url = 'https://covid19-visualisation-seb.herokuapp.com/'
    print('opening URL')
    urllib2.urlopen(url)
    print('URL loaded')


def get_new_data():
    """Updates the global variable 'df' with new data"""
    global df
    df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    print('data loaded')


def get_new_data_every(period=1200):
    """Update the data every 'period' seconds"""
    while True:
        get_new_data()
        openurl()
        time.sleep(period)


get_new_data()

app.layout = html.Div([

    html.Div([

        dcc.Dropdown(
            id='country_selected',
            options=[{'label': i, 'value': i}for i in df['location'].unique()],
            multi=True,
            value=['United Kingdom', 'United States'],
        ),

        dcc.Graph(id='feature-graphic'),

        ]),

    html.Div([

        dcc.Dropdown(
            id='country_selected2',
            options=[{'label': i, 'value': i} for i in df['location'].unique()],
            value='United Kingdom',
        ),

        dcc.Graph(id='feature-graphic2'),

    ]),


])


@app.callback(Output('feature-graphic', 'figure'),
              [Input('country_selected', 'value')]
              )
def update_graph1(country_names):
    scatter_list = []
    for i in range(len(country_names)):
        country_df = df[df['location'] == country_names[i]]
        country_vac = country_df.dropna(subset=['total_vaccinations'])
        temp = go.Scatter(x=country_vac['date'],
                          y=country_vac['total_vaccinations_per_hundred'],
                          mode='lines+markers',
                          name=country_names[i])
        scatter_list.append(temp)

    return {'data': scatter_list,

            'layout': go.Layout(title='Global Vaccinations Data By Country',
                                xaxis={'title': 'Date'},
                                yaxis={'title': 'Total Vaccinations Per Hundred'}
                                )
            }


@app.callback(Output('feature-graphic2', 'figure'),
              [Input('country_selected2', 'value')]
              )
def update_graph2(country_name):
    country_df = df[df['location'] == country_name]
    fig = px.bar(country_df, x='date', y='new_cases')
    fig.update_layout(title='Total cases per day')

    return fig


executor = ThreadPoolExecutor(max_workers=1)
executor.submit(get_new_data_every)

if __name__ == '__main__':
    app.run_server()
