import config
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime as dt
import psycopg2
import pandas as pd
import plotly
from newsapi import NewsApiClient

def getConn(config):
    conn = psycopg2.connect(user = config.user,
                            password = config.password,
                            host = config.host,
                            port = "5432",
                            database = config.db)
    return conn

def _generate_table(n, conn, sql):
    values = pd.read_sql(sql, conn)
    time_to_dest = str(values['time_to_destination'].values[0])
    time_stamp = list(str(values['time'].values[0]).split('T'))[1]
    return [html.Span('{}'.format(time_to_dest),style={'font-size':50}),html.Br(),
            html.Span('Last Updated: {}'.format(time_stamp))]#

def _update_chart(n,conn, sql, color):
    '''
    Updates Charts with from sql table
    n: update interval (ms)
    conn: sql connection object
    sql: query
    color: chart background color
    '''
    df = pd.read_sql(sql, conn)
    data= {
    'time': [],
    'minutes': []
    }

    for i in range(len(df)):
        time = str(df.iloc[i]['time'])
        minutes = str(df.iloc[i]['time_to_destination'])

        minute_list = minutes.split(' ')

        if len(minute_list) > 2:
            hours_to_mins = (int(minute_list[0])*60) + int(minute_list[2])
        else:
            hours_to_mins = int(minute_list[0])

        data['time'].append(time)
        data['minutes'].append(hours_to_mins)

    fig = plotly.subplots.make_subplots(rows=2,cols=1, vertical_spacing=0)

    fig['layout']['margin'] = {
    'l': 10, 'b': 0, 't': 50, 'r': 50

    }

    fig.append_trace({
    'x':data['time'],
    'y': data['minutes'],
    'mode': 'lines+markers',
    'type': 'scatter'
    },1,1)

    fig.layout.height = 290
    fig.layout.xaxis.visible=False
    fig.layout.yaxis.visible=False
    fig.layout.plot_bgcolor=color
    fig.layout.paper_bgcolor=color

    return fig

todays_date = dt.datetime.today()
format_date = todays_date.strftime("%b %d %Y")

app = dash.Dash()
app.layout = html.Div([
            html.Div(

                        html.Div([

                            html.H4(
                                    str('Time to Location A'),
                                    style={'margin-left':50, 'font-size':25}
                                    ),

                            html.Div(
                                    id='live-update-value',
                                    style={'margin-top':30, 'margin-left':50},
                                    className='card'
                                    ),

                            dcc.Graph(id='live-update-chart'),

                            dcc.Interval(
                                        id='interval-component',
                                        interval=30000,
                                        n_intervals=0
                            )
                            ],style={'padding-top':10}
                        ),
                        style={'backgroundColor':'#25374C', 'width':'49.5%', 'float':'left'}
            ),
            html.Div(
                        html.Div([

                            html.H4(
                                    str('Time to Location B'),
                                    style={'margin-left':50, 'font-size':25}
                                    ),

                            html.Div(
                                    id='live-update-value2',
                                    style={'margin-top':30, 'margin-left':50}
                                    ),

                            dcc.Graph(id='live-update-chart2'),

                            dcc.Interval(
                                        id='interval-component2',
                                        interval=30000,
                                        n_intervals=0
                            )
                            ],style={'padding-top':10}
                        ),
                        style={'backgroundColor':'#25374C', 'width':'49.5%','float':'right'}

            ),
            #News API DIV
            html.Div(
                        html.Div([
                            html.H5(
                                'News - ' + str(format_date), style={'margin-left':50,
                                                                    'margin-top':'15px',
                                                                    'font-size':25}
                            ),

                            html.Div(
                                    id='live-update-value3',
                                    style={'margin-top':1, 'margin-left':50}),

                            dcc.Interval(
                                id='interval-component3',
                                interval=30000,
                                n_intervals=0
                            )
                            ],style={'padding-top':10}
                        ),
                        style={'width':'100%', 'height':'290px','float':'left','margin-top':'10px'}
                        )
            ])

@app.callback(Output('live-update-value', 'children'), [Input("interval-component","n_intervals")])
def generate_table(n, conn=getConn(config)):
    return _generate_table(n, conn, 'select * from time_to_destination2 order by time desc limit 1;')

@app.callback(Output('live-update-chart', 'figure'), [Input("interval-component","n_intervals")])
def update_chart(n,conn=getConn(config)):
    return _update_chart(n,conn,'select * from time_to_destination2 order by time desc limit 5;','#25374C')

@app.callback(Output('live-update-value2', 'children'), [Input("interval-component2","n_intervals")])
def generate_table(n, conn=getConn(config)):
    return _generate_table(n, conn, 'select * from time_to_destination2 order by time desc limit 1;')

@app.callback(Output('live-update-chart2', 'figure'), [Input("interval-component2","n_intervals")])
def update_chart(n,conn=getConn(config)):
    return _update_chart(n,conn,'select * from time_to_destination2 order by time desc limit 5;','#25374C')

@app.callback(Output('live-update-value3', 'children'), [Input("interval-component2","n_intervals")])
def pull_news(n, config=config):

        newsapi = NewsApiClient(api_key=config.newsapi_key)

        top_headlines = newsapi.get_top_headlines(
                                          sources='Forbes.com,CNN,CNBC',
                                          language='en')

        styles = {'float':'left','height':'250px','margin':'5px','width':'30%',
        'font-size':35,'backgroundColor':'#1F292E','padding':'10px','color':'black',
        'font-family': 'Verdana'}

        #truncate articles titles that are beyond 90 characters
        def limitTitle(title):
            if len(title) > 90:
                title = str(title[:90]) + '...'

            return title

        #Returns top three articles of newapi response
        return [html.Div([html.H6(
                                top_headlines['articles'][0]['source']['name'],style={'margin':'1px'}),
                                html.Span(limitTitle(top_headlines['articles'][0]['title']))],
                                style=styles),
                html.Div([html.H6(
                                top_headlines['articles'][1]['source']['name'],style={'margin':'1px'}),
                                html.Span(limitTitle(top_headlines['articles'][1]['title']))],
                                style=styles),
                html.Div([html.H6(
                                top_headlines['articles'][2]['source']['name'],style={'margin':'1px'}),
                                html.Span(limitTitle(top_headlines['articles'][2]['title']))],
                                style=styles)]

if __name__ == '__main__':
    app.run_server(debug=True, port=1337)
