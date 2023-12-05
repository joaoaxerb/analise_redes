import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
import plotly.express as px
import plotly.figure_factory as ff
import io
import base64

# Inicializar Dash app
app = dash.Dash(__name__)

# Inicializar DataFrames
df1 = pd.DataFrame()
df2 = pd.DataFrame()

# Definir layout
app.layout = html.Div(style={'backgroundColor': 'lightblue', 'text-align': 'center'}, children=[
    html.H1("Análise de redes - PUC Minas",
            style={'color': 'white', 'background-color': 'blue', 'padding': '20px', 'margin-bottom': '0'}),

    # Upload dos arquivos
    dcc.Upload(
        id='upload-data-1',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('selecione o arquivo CSV do primeiro cenário')
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
    dcc.Upload(
        id='upload-data-2',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('selecione o arquivo CSV do segundo cenário')
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

    # Dropdown menu para selecionar qual arquivo analisar
    dcc.Dropdown(
        id='file-selector',
        options=[
            {'label': 'Cenário 1', 'value': 'df1'},
            {'label': 'Cenário 2', 'value': 'df2'},
        ],
        value='df1',  # Default selection
        style={'width': '50%', 'margin': '10px'}
    ),

    # Abas
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Visão Geral dos Pacotes', value='tab1'),
        dcc.Tab(label='Detalhes dos Pacotes', value='tab2'),
        dcc.Tab(label='Métricas Estatísticas', value='tab3'),
    ]),

    # Tab content
    html.Div(id='tabs-content'),
])


# Callback para tratar arquivos csv
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'),
              Input('upload-data-1', 'contents'),
              Input('upload-data-2', 'contents'),
              State('upload-data-1', 'filename'),
              State('upload-data-2', 'filename'),
              Input('file-selector', 'value'))
def update_tab(tab_name, contents1, contents2, filename1, filename2, selected_file):
    global df1, df2  # Make df1 and df2 global to update them

    # Atualizar df1
    if contents1 is not None:
        content_type, content_string = contents1.split(',')
        decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
        df1 = pd.read_csv(decoded)

    # Atualizar df2
    if contents2 is not None:
        content_type, content_string = contents2.split(',')
        decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
        df2 = pd.read_csv(decoded)

    # Determinar qual arquivo usar
    selected_df = df1 if selected_file == 'df1' else df2

    # verfica se arquivo não está vazio
    if selected_df.empty:
        return [html.Div(html.H3("Selecione um arquivo para análise."))]

    if tab_name == 'tab1':

        protocol_counts = selected_df["Protocol"].value_counts().reset_index()
        protocol_counts.columns = ["Protocol", "Count"]
        protocol_counts["Percentage"] = (protocol_counts["Count"] / len(selected_df)) * 100
        # Ordena em ordem descendente
        protocol_counts_sorted = protocol_counts.sort_values(by="Percentage", ascending=False)

        # Seleciona top 10
        protocol_counts_top10 = protocol_counts_sorted.head(13)

        # Criar DataFrame para 'Source' e sua contagem 
        source_counts = selected_df["Source"].value_counts().reset_index()
        source_counts.columns = ["Source", "Count"]

        # Seleciona top 10
        source_counts_top10 = source_counts.head(10)

        return [
            # Numero de pacotes
            html.Div([
                html.H3("Numero de Pacotes Capturados"),
                html.H4(len(selected_df)),
            ]),
            # Gráfico de barras - Porcentage do Total Packets (Top 13)
            dcc.Graph(
                figure=px.histogram(protocol_counts_top10, x="Percentage", y="Protocol", title="Porcentagem de pacotes por Protocolo (Top 10)",
                            labels={'Protocol': 'Communication Protocol', 'Percentage': 'Percentage of Total'}, category_orders={"Protocol": protocol_counts_sorted["Protocol"].tolist()}),
            ),
            # Gráfico de barras- Packets por dispossitivo (Top 10)
            dcc.Graph(
                figure=px.histogram(source_counts_top10, x="Count", y="Source", orientation="h", title="Pacotes por Dispositivo (Top 10)",
                            labels={'Source': 'Device IP', 'Count': 'Number of Packets'}),
            ),
        ]
    elif tab_name == 'tab2':
        return [
            # Detalhamento dos pacotes
            html.Div([
                html.H3("Detalhes dos Pacotes"),
                dash_table.DataTable(
                    id='packet-details-table',
                    columns=[{"name": i, "id": i}
                             for i in selected_df.columns],
                    data=selected_df.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'width': '150px', 'textAlign': 'left'},
                )
            ]),
        ]
    elif tab_name == 'tab3':
        # Estatísticas sobre o comprimento dos pacotes
        packet_length_stats = selected_df["Length"].describe()

        # Estatísticas sobre o tempo entre chegadas de pacotes
        inter_arrival_time_stats = selected_df["Time"].diff().describe()

        # Inclua as interpretações na apresentação
        interpretation_table = html.Table(
            # Cabeçalho
            [html.Tr([html.Th(col) for col in ['Métrica', 'Comprimento do Pacote', 'Intervalo entre Chegadas']])] +
            # Linhas
            [html.Tr([
                html.Td(metric),
                html.Td(packet_length_stats[metric]),
                html.Td(inter_arrival_time_stats[metric]),
             ]) for metric in ['mean', '50%', 'std']],
            style={'width': '100%'}
        )

        # Tamanho dos pacotes Distribution
        packet_size_distribution = ff.create_distplot([selected_df["Length"]],
                                                    group_labels=["Packet Size"],
                                                    bin_size=10,
                                                    show_hist=False,  # Show histogram
                                                    show_rug=False,  # Hide rug plot
                                                    histnorm='',
                                                    )
        packet_size_distribution.update_layout(
            title_text="Distribuição do Tamanho dos Pacotes",
            xaxis=dict(title="Comprimento do Pacote")
        )
        packet_size_distribution.update_yaxes(showticklabels=False)

        # Tempos de chegada Distribution
        inter_arrival_time_distribution = ff.create_distplot([selected_df["Time"].diff().dropna()],
                                                            group_labels=["Inter-Arrival Time"],
                                                            bin_size=0.01,
                                                            show_hist=False,
                                                            show_rug=False,
                                                            histnorm='',
                                                            )
        inter_arrival_time_distribution.update_layout(
            title_text="Distribuição dos Tempos de Chegada",
            xaxis=dict(title="Intervalo entre Chegadas")
        )
        inter_arrival_time_distribution.update_yaxes(showticklabels=False)

        # Adicione os histogramas e interpretações à aba de estatísticas
        return [
            html.Div([
                html.H3("Métricas Estatísticas"),
                interpretation_table,
                dcc.Graph(figure=packet_size_distribution),
                dcc.Graph(figure=inter_arrival_time_distribution),
            ]),
        ]


# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)
