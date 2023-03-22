# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from natsort import natsorted
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.MINTY,
        dbc.themes.GRID,
        "https://fonts.googleapis.com/css?family=Poppins:300,400,500,600,700%7CRoboto:300,400,500,600,700",
        "assets/main.css"
    ]
)

#fazendo a leitura dos dados e a construção do data frame
df = pd.read_csv("New_dataset.csv", usecols=['proc', 'date', 'vara', 'assunto'])

df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
df['quantidade'] = 1

varas = df['vara'].value_counts().index
varas = natsorted(varas)
df2 = df.copy()

assuntos = df2['assunto'].value_counts().head(10)
data_assuntos = pd.DataFrame(assuntos)
data_assuntos = data_assuntos.reset_index()
data_assuntos.columns=['assuntos','quantidade_assuntos']

df = df.resample('M', on='date').sum()

print(df2['assunto'])

#criando as opções para se usar no dropdown
opcoes = list(df2['vara'].unique())
opcoes.append('Todas as varas')

#inicio da aplicação do dashboard
app.layout = html.Div(children=[
    html.Div(
        className='main',
        children=[
            html.Div(
                className='title',
                children=[
                    html.H1(children='Justiça Federal do Rio Grande do Norte'),
                    html.H2(children='Painel de acompanhamento de varas'),
                ]
            ),
            html.Div(
                className='main-row',
                children=[
                    html.Div(
                        className='dashboard-card',
                        children=[
                            html.H2(children='Selecione a vara'),
                            dcc.Dropdown(opcoes, value='Todas as varas', id='processos',
                                         className='dropdown'),
                        ],
                    ),
                    html.Div(
                        className='graph-content',
                        children=[
                                html.Div(
                                    className='graph-principal',
                                    children=[
                                        html.H2(
                                            children='Gráfico com o quantitativo de processos'
                                        ),
                                        dcc.Graph(
                                            id='grafico_quantidade_proc',
                                        ),
                                    ]
                                ),
                            html.Div(
                                className='graph-second',
                                children=[
                                    html.H2(
                                        children='Gráfico com o quantitativo de assuntos '
                                    ),
                                    dcc.Graph(
                                        id='grafico_quantidade_assuntos',

                                    ),
                                ]
                            )
                        ]
                    ),
                ]
            ),
        ]
    ),
])

@app.callback(
    [
    Output('grafico_quantidade_proc', 'figure'),
    Output('grafico_quantidade_assuntos', 'figure'),
    ],
    Input('processos', 'value')

)
def update_output(value):
    figAssuntos = px.bar(
        data_assuntos,
        x=data_assuntos['assuntos'],
        y=data_assuntos['quantidade_assuntos'],
    )
    figSeries = go.Figure()
    if value == 'Todas as varas':
        figSeries.add_trace(
        go.Scatter(
            x = df.index,
            y = df['quantidade'],
            name='Gráfico do quantitativo de processos',
            line = dict (
                color = 'tomato',
                width = 1,
            )
        )
    )

    else:
        tabela_filtrada = df2.loc[df2['vara']==value, :]
        serie_filtrada = tabela_filtrada.copy()
        serie_filtrada['date'] = pd.to_datetime(serie_filtrada['date'], format='%m/%d/%Y')
        serie_filtrada['quantidade'] = 1
        serie_filtrada = serie_filtrada.resample('M',on='date').sum()
        figSeries.add_trace(
           go.Scatter(
                x=serie_filtrada.index,
                y=serie_filtrada['quantidade'],
               name='Gráfico do quantitativo de processos',
                line=dict(
                    color='tomato',
                    width=1,
                )
            )
        )
    return figSeries, figAssuntos

if __name__ == '__main__':
    app.run_server(debug=True)
