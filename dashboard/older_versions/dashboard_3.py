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

# Calculate statistics metrics
packet_length_stats = df["Length"].describe()
inter_arrival_time_stats = df["Time"].diff().describe()

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(style={'backgroundColor': 'lightblue', 'text-align': 'center'}, children=[
    html.H1("Análise de redes - PUC Minas",
            style={'color': 'white', 'background-color': 'blue', 'padding': '20px', 'margin-bottom': '0'}),

    # Tabs
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Visão Geral dos Pacotes', value='tab1'),
        dcc.Tab(label='Detalhes dos Pacotes', value='tab2'),
        dcc.Tab(label='Métricas Estatísticas', value='tab3'),
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
                html.H3("Numero de Pacotes Capturados"),
                html.H4(len(df)),
            ]),
            # Bar chart - Percentage of Total Packets for Each Protocol
            dcc.Graph(
                figure=px.bar(protocol_counts, x="Protocol", y="Percentage", title="Porcentagem de pacotes por Protocolo", labels={
                              'Protocol': 'Communication Protocol', 'Percentage': 'Percentage of Total'}),
            ),
            # Bar chart - Packets per device
            dcc.Graph(
                figure=px.bar(df, x="Source", title="Pacotes por Aparelho", labels={
                              'Source': 'Device IP', 'count': 'Number of Packets'}),
            ),
        ]
    elif tab_name == 'tab2':
        return [
            # Packet details table
            html.Div([
                html.H3("Detalhes dos Pacotes"),
                dash_table.DataTable(
                    id='packet-details-table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'width': '150px', 'textAlign': 'left'},
                )
            ]),
        ]
    elif tab_name == 'tab3':
        return [
            # Statistics metrics
            html.Div([
                html.H3("Métricas Estatísticas"),
                html.Table(
                    # Header
                    [html.Tr([html.Th(col) for col in ['Metric', 'Packet Length', 'Inter-Arrival Time']])] +
                    # Rows
                    [html.Tr([html.Td(metric)] + [html.Td(packet_length_stats[metric]), html.Td(inter_arrival_time_stats[metric])])
                     for metric in ['mean', '50%', 'std']],
                    style={'width': '100%'}
                )
            ]),
        ]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
