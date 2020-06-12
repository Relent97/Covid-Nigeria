# Import required libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash.dependencies import Input, Output, ClientsideFunction
from bs4 import BeautifulSoup
import requests
from datetime import date
from datetime import timedelta
fig = go.Figure()

# Multi-dropdown options


# get relative data folder


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls


# Load data
url = url = requests.get("https://covid19.ncdc.gov.ng/report/").text
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
Table2["Date"] = today
Table2 = Table2[["Date","State","Total Confirmed Cases","Total Admissions","Total Discharged","Total Deaths"]]
Table2["Date"] = pd.to_datetime(Table2["Date"])
Table2["Total Confirmed Cases"] = Table2["Total Confirmed Cases"].str.replace(",","")
Table2["Total Admissions"] = Table2["Total Admissions"].str.replace(",","")
Table2["Total Discharged"] = Table2["Total Discharged"].str.replace(",","")
Table2["Total Deaths"] = Table2["Total Deaths"].str.replace(",","")
Tab = ["Total Confirmed Cases", "Total Admissions", "Total Discharged", "Total Deaths"]
Table2[Tab] = Table2[Tab].applymap(float)
Table2["Total Active Cases"] = Table2["Total Confirmed Cases"] - (Table2["Total Discharged"]+Table2["Total Deaths"]) 


S = pd.read_excel("Data.xlsx")
df = pd.DataFrame(S)
df.replace(np.nan,0, inplace = True)
df = df[['Date', 'State', 'NUMBER OF TESTS DONE',' NEW CONFIRMED CASES','TOTAL Confirmed Cases', 'NEW ADMITTED CASES','TOTAL ACTIVE CASES','NEW DISCHARGED CASES','TOTAL DISCHARGED',
'NEW DEATHS','TOTAL DEATHS','DAY LAST CASE']]


df["Month"] = df["Date"].dt.month
df["Week"] = df["Date"].dt.week

## Date comparison
Day1 = df.Date.max()
Day2 = Day1 - timedelta(days = 1)
a = df.groupby("Week").sum()

b = a.reset_index()
c = df.groupby(["State","Week"]).sum()
c.reset_index(inplace = True)
states = c.State.unique()

fig2 = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "Indicator"}, {"type": "Indicator"}],
           [{"type": "Indicator"}, {"type": "Indicator"}]],
    subplot_titles=("Cases", "Deaths", "Discharged","Admissions")
)
fig2.add_trace(go.Indicator(mode = "number+delta",
            value = df[df["Date"] == df.Date.max()][" NEW CONFIRMED CASES"].sum(),
            delta = {'reference': df[df["Date"] == Day2][" NEW CONFIRMED CASES"].sum(), 'relative':True}), row = 1, col = 1)
fig2.add_trace(go.Indicator(mode = "number+delta",
            value =  df[df["Date"] == df.Date.max()]["NEW DISCHARGED CASES"].sum(),
            delta = {'reference': df[df["Date"] == Day2]["NEW DISCHARGED CASES"].sum(), 'relative':True}), row = 1, col = 2)
fig2.add_trace(go.Indicator(mode = "number+delta",
            value = df[df["Date"] == df.Date.max()]["NEW DEATHS"].sum(),
            delta = {'reference': df[df["Date"] == Day2]["NEW DEATHS"].sum(), 'relative':True}), row = 2, col = 1)
fig2.add_trace(go.Indicator(mode = "number+delta",
            value = df[df["Date"] == df.Date.max()][" NEW CONFIRMED CASES"].sum(),
            delta = {'reference': df[df["Date"] == Day2][" NEW CONFIRMED CASES"].sum(), 'relative':True}), row = 2, col = 2)
fig2.update_layout( height=250, title = "Latest Daily Figures",template= "plotly_dark")


fig6 = make_subplots(
    rows=1, cols=5,
    specs=[[{"type": "Indicator"}, {"type": "Indicator"},{"type": "Indicator"}, {"type": "Indicator"},{"type": "Indicator"}]],
    subplot_titles=("Days", "Cases", "Deaths", "Discharged","Death Rate")
)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = df["Date"].nunique(), delta = {'reference' : 0, 'relative':False}), 
            row = 1, col = 1)
fig6.add_trace(go.Indicator(mode = "number+delta",value =  Table2['Total Confirmed Cases'].sum(),
            delta = {'reference': df[df["Date"] == Day2]["TOTAL Confirmed Cases"].sum(), 'relative':True}), row = 1, col = 2)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = Table2["Total Deaths"].sum(),
            delta = {'reference': df[df["Date"] == Day2]["TOTAL DEATHS"].sum() , 'relative':True}), row = 1, col = 3)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value = Table2["Total Discharged"].sum(),
            delta = {'reference': df[df["Date"] == Day2]["TOTAL DISCHARGED"].sum(), 'relative':True}), row = 1, col = 4)
fig6.add_trace(go.Indicator(mode = "number+delta",
            value =  Table2["Total Deaths"].sum()/ Table2['Total Confirmed Cases'].sum(),
            delta = {'reference': 0.03, 'relative':True}), row = 1, col = 5)
fig6.update_layout( height=250, template= "plotly_dark", title = "Figures from 27th February 2020 till Date(% change from previuos day)" )

fig1 = px.bar(b, x = b["Week"], y = b["NEW ADMITTED CASES"])
fig1.update_layout(template = 'plotly_dark', title = "Confirmed Cases per week", height=250)

fig4 = make_subplots(
    rows=2, cols=2, subplot_titles=("Confirmed Cases per week", "Deaths per Week", "Discharges Per Week", "Discharge Rate")
)

# Add traces
fig4.add_trace(go.Scatter(x= b["Week"], y=b[" NEW CONFIRMED CASES"]), row=1, col=1)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["NEW DEATHS"]), row=1, col=2)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["NEW DISCHARGED CASES"]), row=2, col=1)
fig4.add_trace(go.Scatter(x= b["Week"], y=b["NEW DISCHARGED CASES"]/b[" NEW CONFIRMED CASES"]), row=2, col=2)

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

fig5 = px.bar(b, x = b["Week"], y = b[" NEW CONFIRMED CASES"] - (b["NEW DISCHARGED CASES"] + b["NEW DEATHS"]))
fig5.update_layout(template = 'plotly_dark', title = "Active Cases Per Week" )




# Create global chart template

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div([ html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Nigerian-map.png"),
                            id="Nigeria",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div([
                        html.Div([
                                html.H3(
                                    "Nigerian Covid-19 Dashboard",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "All data automatically updated from the NCDC website", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Contact Me", id="learn-more-button"),
                            href="https://twitter.com/koladeCh?s=08",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),

        html.Div(
            [
                html.Div(
                    [  html.P("This dashboard is built to track the spread of Covid-19 in Nigeria.For any questions you can find me on social media by clicking the contact me button.", 
                            className="control_label"),
                        html.P(" Please note that the dashbard experience is better with a laptop/desktop.", className="control_label"),
                        html.P("You can zoom in on each graph and also take pictures, just check the topright of each graph", className="control_label"),
                        html.P("Incorrect data is automatically reloaded within 5 minutes. If it exceeds 5 minutes kindly contact me.", className='control_label'),
                        dcc.Graph( id = 'Latest figures', figure = fig2, config={'displaylogo':False}),
                        html.P(
                            "Select a state from the dropdown below and compare the New Cases, Discharges, Deaths with other states week on week",
                            className="control_label",
                        ),
                        dcc.Dropdown(id='state-filter',
                           options=[{'label': i, 'value': i} for i in states], style={'backgroundColor': '#1E1E1E'},
                           value='Abia', multi = True,className="dcc_control",
                        ),

                        ],
                    className="pretty_container five columns",
                    id="cross-filter-options",
                ),

                html.Div([
                        html.Div([
                                html.Div([dcc.Graph( id='Overview', config={"displaylogo": False},
                                  figure= fig6, className="pretty_container")
                            ],
                            id="info-container", className="row flex-display"
                            
                        ),
                        html.Div(
                            [dcc.Graph(id="overall confirmed", config = {"displaylogo": False}, figure = fig1,
                             className="pretty_container")],
                            id="countGraphContainer", className="row flex-display"
                            
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ]),
                ],
                     className="row flex-display",
            ),


        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="Confirmed",config={
        "displaylogo": False},)],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="Activestate", config = {"displaylogo":False},)], #Requires another callback
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div([dcc.Graph(id='Graph3',config={
                    "displaylogo": False},
                      figure = fig4)],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="active-overall", figure = fig5,config={
                    "displaylogo": False})],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)



# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("overall confirmed", "figure")],
)


@app.callback(Output('Confirmed', 'figure'),
    [Input('state-filter', 'value')]
)

def update_graph(selected_dropdown_value):
    core = make_subplots(rows = 2, cols= 2, specs=[[{"rowspan": 2},{}],
           [None,{}]],
           subplot_titles=("Confirmed Cases","Deaths", "Discharges"))
    df_sub = c
    for state1 in selected_dropdown_value:
        trace1 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1][' NEW CONFIRMED CASES'],
                                 mode='lines',
                                 name=state1)
        trace2 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1]["NEW DEATHS"],
                                 mode='lines',
                                 name=state1)
        trace3 = go.Scatter(x=c[c['State'] == state1]["Week"],
                                 y=c[c['State'] == state1]["NEW DISCHARGED CASES"],
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

@app.callback(Output('Activestate', 'figure'),
    [Input('state-filter', 'value')]
)
def update_graph1(selected_dropdown_value1):
    sub_df  = c
    core2 = make_subplots(rows = 2, cols = 2, specs=[[{"colspan":2},None],
                                                    [None,None]])
    for state2 in selected_dropdown_value1:
        trace4 = go.Scatter(x=c[c['State'] == state2]["Week"],
                                 y=c[c['State'] == state2]['NEW ADMITTED CASES'], mode= 'lines',
                                 name=state2)
        core2.append_trace(trace4, row=1, col=1)
        core2.update_xaxes(title_text="Week", row=1, col=1)
        core2.update_yaxes(title_text="Active Cases", row=1, col=1)
        core2.update_layout(height = 500, template='plotly_dark', 
        title={'text': 'Active cases per Week', 'font': {'color': 'white'}, 'x': 0.5})
    return core2

    



# Main
if __name__ == "__main__":
    app.run_server(debug=True)