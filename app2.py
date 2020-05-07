import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash.dependencies import Input, Output
from bs4 import BeautifulSoup
import requests
from datetime import date
from datetime import timedelta

fig = go.Figure()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

url = requests.get("https://covid19.ncdc.gov.ng/report/").text
soup = BeautifulSoup(url,'lxml')
Table = soup.find('table')
Table1 = Table.find_all('td')
today = date.today()
yesterday = today - timedelta(days = 1) 


State = []
Confirmed = []
Admits = []
Discharged = []
Deaths = []

for d in range(0,len(Table1),5):
    State.append(Table1[d].text.strip()) 
    Confirmed.append(Table1[d+1].text.strip())
    Admits.append(Table1[d+2].text.strip())
    Discharged.append(Table1[d+3].text.strip())
    Deaths.append(Table1[d+4].text.strip())
Table2 = pd.DataFrame(data = [State,Confirmed,Admits,Discharged,Deaths]).transpose()
Table2.columns = ["State","Total Confirmed Cases","Total Admissions","Total Discharged","Total Deaths"]
Table2["Date"] = yesterday

S = pd.read_excel("Data.xlsx")

df = pd.DataFrame(S)
df.replace(np.nan,0, inplace = True)
df = df[['Date', 'State', 'TOTAL Confirmed Cases','ACTIVE CASES','TOTAL DISCHARGED', 'TOTAL DEATHS',' CONFIRMED CASES  PER DAY','ADMITTED CASES PER DAY','DISCHARGED CASES PER DAY',
             'DEATHS PER DAY']]


df["Month"] = df["Date"].dt.month
df["Week"] = df["Date"].dt.week

a = df.groupby("Week").sum()

b = a.reset_index()
c = df.groupby(["State","Week"]).sum()
c.reset_index(inplace = True)
states = c.State.unique()


fig4 = make_subplots(
    rows=2, cols=2, subplot_titles=("Confirmed Cases per week", "Deaths per Week", "Discharges Per Week", "Discharge Rate")
)

# Add traces
fig4.add_trace(go.Scatter(x= b["Week"], y=b[" CONFIRMED CASES  PER DAY"]), row=1, col=1)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["DEATHS PER DAY"]), row=1, col=2)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["DISCHARGED CASES PER DAY"]), row=2, col=1)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["DISCHARGED CASES PER DAY"]/b[" CONFIRMED CASES  PER DAY"]), row=2, col=2)

# Update xaxis properties
fig4.update_xaxes(title_text="Week", row=1, col=1)
fig4.update_xaxes(title_text="Week", row=1, col=2)
fig4.update_xaxes(title_text="Week", row=2, col=1)
fig4.update_xaxes(title_text="Week", type="log", row=2, col=2)

# Update yaxis properties
fig4.update_yaxes(title_text="Confirmed Cases", row=1, col=1)
fig4.update_yaxes(title_text="Deaths", row=1, col=2)
fig4.update_yaxes(title_text="Discharges", row=2, col=1)
fig4.update_yaxes(title_text="Discharge rate", row=2, col=2)

# Update title and height
fig4.update_layout(title_text="Indicators per Week", height=700,template= "plotly_dark")


# New Figure

fig6 = make_subplots(
    rows=1, cols=5,
    specs=[[{"type": "Indicator"}, {"type": "Indicator"},{"type": "Indicator"}, {"type": "Indicator"},{"type": "Indicator"}]],
    subplot_titles=("Total Number of Days", "Total Cases", "Total Deaths", "Total DIscharged","Death Rate")
)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = df["Date"].nunique(),
            delta = {'reference': 80, 'relative':True}), row = 1, col = 1)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value =  df[' CONFIRMED CASES  PER DAY'].sum(),
            delta = {'reference': 1500, 'relative':True}), row = 1, col = 2)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = df["DEATHS PER DAY"].sum(),
            delta = {'reference': 90, 'relative':True}), row = 1, col = 3)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = df["DISCHARGED CASES PER DAY"].sum(),
            delta = {'reference': 1000, 'relative':True}), row = 1, col = 4)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value =  df["DEATHS PER DAY"].sum()/ df[' CONFIRMED CASES  PER DAY'].sum(),
            delta = {'reference': 0.0300, 'relative':True}), row = 1, col = 5)
fig6.update_layout( height=250, template= "plotly_dark")





app.layout = html.Div(children = [
	html.H1(children = 'Nigerian Covid-19 Dashboard by Relentless_97'),

       html.Div([dcc.Graph( 
         id='Transactions', config={
        "displaylogo": False},
         figure= fig6
    )]),
        html.Div([dcc.Graph(id='Graph3',config={
        "displaylogo": False},
        figure = fig4

        ### Select Per State to show progression(Cases, deaths, Recoveries, Active) over the weeks then day
        ### Select per week to show in every state
    )]),
        html.Div([dcc.Dropdown(
                id='state-filter',
                options=[{'label': i, 'value': i} for i in states], style={'backgroundColor': '#1E1E1E'},
                value='Abia', multi = True)
            ,
            dcc.Graph(id='Confirmed',config={
        "displaylogo": False},),
    ])

])

@app.callback(
    Output('Confirmed', 'figure'),
    [Input('state-filter', 'value')])
def update_graph(selected_dropdown_value):
    core = make_subplots(rows = 2, cols= 2, specs=[[{"rowspan": 2},{}],
           [None,{}]],
           subplot_titles=("Confirmed Cases","Deaths", "Discharges"))
    df_sub = c
    for state1 in selected_dropdown_value:
        trace1 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1][' CONFIRMED CASES  PER DAY'],
                                 mode='lines',
                                 name=state1)
        trace2 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1]["DEATHS PER DAY"],
                                 mode='lines',
                                 name=state1)
        trace3 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1]["DISCHARGED CASES PER DAY"],
                                 mode='lines',
                                 name=state1)
        core.append_trace(trace1, row =1, col = 1)
        core.append_trace(trace2, row =1, col= 2)
        core.append_trace(trace3, row = 2,col = 2)

        core.update_xaxes(title_text="Week", row=1, col=1)
        core.update_xaxes(title_text="Week", row=1, col=2)
        core.update_xaxes(title_text="Week", row=2, col=2)
         

        # Update yaxis properties
        core.update_yaxes(title_text="Confirmed Cases", row=1, col=1)
        core.update_yaxes(title_text="Deaths", row=1, col=2)
        core.update_yaxes(title_text="Discharges", row=2, col=2)
         


        core.update_layout( height=500, template= "plotly_dark",
                            title={'text': 'State per week', 'font': {'color': 'white'}, 'x': 0.5})

    return core








if __name__ == '__main__':
	app.run_server(debug = True,)