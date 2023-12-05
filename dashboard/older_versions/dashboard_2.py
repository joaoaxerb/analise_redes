import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.express as px

# Read CSV data
df = pd.read_csv("/home/joaoaxer/src/tcc/teste_mostra.csv")

# Calculate percentage of total for each protocol
total_packets = len(df)
protocol_counts = df["Protocol"].value_counts().reset_index()
protocol_counts.columns = ["Protocol", "Count"]
protocol_counts["Percentage"] = (protocol_counts["Count"] / len(df)) * 100

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(style={'backgroundColor': 'lightblue', 'text-align': 'center'}, children=[
    html.H1("Análise de redes - PUC Minas",
            style={'color': 'white', 'background-color': 'blue', 'padding': '20px', 'margin-bottom': '0'}),

    # Tabs
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Packet Overview', value='tab1'),
        dcc.Tab(label='Packet Details', value='tab2'),
    ]),

    # Tab content
    html.Div(id='tabs-content'),

])

# Callback to update tab content


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def update_tab(tab_name):
    if tab_name == 'tab1':
        return [
            # Number of packets
            html.Div([
                html.H3("Number of Packets Captured"),
                html.H4(len(df)),
            ]),
            # Bar chart - Percentage of Total Packets for Each Protocol
            dcc.Graph(
                figure=px.bar(protocol_counts, x="Protocol", y="Percentage", title="Percentage of Total Packets for Each Protocol", labels={
                              'Protocol': 'Communication Protocol', 'Percentage': 'Percentage of Total'}),
            ),
            # Bar chart - Packets per communication protocol
            dcc.Graph(
                figure=px.bar(df, x="Protocol", title="Pacotes por protocolo", labels={
                              'Protocol': 'Communication Protocol', 'count': 'Number of Packets'}),
            ),
            # Bar chart - Packets per device
            dcc.Graph(
                figure=px.bar(df, x="Source", title="Packets per Device", labels={
                              'Source': 'Device IP', 'count': 'Number of Packets'}),
            ),
        ]
    elif tab_name == 'tab2':
        return [
            # Packet details table
            html.Div([
                html.H3("Packet Details"),
                dash_table.DataTable(
                    id='packet-details-table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'width': '150px', 'textAlign': 'left'},
                )
            ]),
        ]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
