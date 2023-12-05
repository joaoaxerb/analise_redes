import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.express as px
import plotly.figure_factory as ff
import io
import base64

# Read CSV data
df = pd.read_csv("/home/joaoaxer/src/tcc/teste2_dia_27.csv")

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

# Initialize an empty DataFrame
df = pd.DataFrame()

# Define layout
app.layout = html.Div(style={'backgroundColor': 'lightblue', 'text-align': 'center'}, children=[
    html.H1("Análise de redes - PUC Minas",
            style={'color': 'white', 'background-color': 'blue', 'padding': '20px', 'margin-bottom': '0'}),

    # File Upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('selecione um arquivo CSV')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),

    # Tabs and other content
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Visão Geral dos Pacotes', value='tab1'),
        dcc.Tab(label='Detalhes dos Pacotes', value='tab2'),
        dcc.Tab(label='Métricas Estatísticas', value='tab3'),
    ]),

    # Tab content
    html.Div(id='tabs-content'),
])


# Callback to handle file upload and update DataFrame
@app.callback(
    Output('tabs-content', 'children'),
    [
        Input('tabs', 'value'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified'),
    ]
)
def update_tab(tab_name, contents, filename, last_modified):
    global df  # Make df global to update it
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
        df = pd.read_csv(decoded)
    elif df.empty:  # If df is still empty, return an empty layout
        return []
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
        # Estatísticas sobre o comprimento dos pacotes
        packet_length_stats = df["Length"].describe()

        # Estatísticas sobre o tempo entre chegadas de pacotes
        inter_arrival_time_stats = df["Time"].diff().describe()

        # Adicione interpretações
        interpretations = {
            "mean": "A média do comprimento dos pacotes é a medida central que representa o tamanho típico dos pacotes na comunicação.",
            "50%": "O percentil 50% (mediana) indica o valor abaixo do qual metade dos comprimentos dos pacotes estão. É uma medida de tendência central robusta.",
            "std": "O desvio padrão mostra a dispersão dos comprimentos dos pacotes em relação à média. Quanto maior o desvio padrão, maior a variabilidade."
        }

        # Inclua as interpretações na apresentação
        interpretation_table = html.Table(
            # Cabeçalho
            [html.Tr([html.Th(col) for col in ['Métrica', 'Comprimento do Pacote', 'Intervalo entre Chegadas']])] +
            # Linhas
            [html.Tr([
                html.Td(metric),
                html.Td(packet_length_stats[metric]),
                html.Td(inter_arrival_time_stats[metric]),
            ]) for metric in ['mean', '50%', 'std']] +
            [html.Tr([html.Td(colSpan=3, children=html.P(interpretations[metric]))])
             for metric in ['mean', '50%', 'std']],
            style={'width': '100%'}
        )

        # Packet Size Distribution
        packet_size_distribution = ff.create_distplot([df["Length"]],
                                                      group_labels=[
                                                          "Packet Size"],
                                                      bin_size=10,
                                                      show_hist=False,  # Hide histogram
                                                      show_rug=False,  # Hide rug plot
                                                      )
        packet_size_distribution.update_layout(
            title_text="Packet Size Distribution")

        # Inter-Arrival Time Distribution
        inter_arrival_time_distribution = ff.create_distplot([df["Time"].diff().dropna()],
                                                             group_labels=[
                                                                 "Inter-Arrival Time"],
                                                             bin_size=0.01,
                                                             show_hist=False,
                                                             show_rug=False,
                                                             )
        inter_arrival_time_distribution.update_layout(
            title_text="Inter-Arrival Time Distribution")

        # Adicione os histogramas e interpretações à aba de estatísticas
        return [
            html.Div([
                html.H3("Métricas Estatísticas"),
                interpretation_table,
                dcc.Graph(figure=packet_size_distribution),
                dcc.Graph(figure=inter_arrival_time_distribution),
            ]),
        ]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
