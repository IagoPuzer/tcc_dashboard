# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, dash_table
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

# fazendo a leitura dos dados e a construção do data frame
df = pd.read_csv("New_dataset.csv", usecols=['proc', 'date', 'vara', 'assunto', 'advogados'])

df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
df['quantidade'] = 1

varas = df['vara'].value_counts().index
varas = natsorted(varas)
df2 = df.copy()

# criando o dataframe para fazer a leitura dos assuntos
assuntos = df2['assunto'].value_counts().head(10)
data_assuntos = pd.DataFrame(assuntos)
data_assuntos = data_assuntos.reset_index()
data_assuntos.columns = ['assuntos', 'quantidade_assuntos']

# criando o dataframe para fazer a leitura dos advogados
advogados = df2['advogados'].value_counts().head(10)
data_advogados = pd.DataFrame(advogados)
data_advogados = data_advogados.reset_index()
data_advogados.columns = ['advogados', 'quantidade_advogados']

df = df.resample('M', on='date').sum()

# Calculo da média móvel
df['media'] = df['quantidade'].rolling(2).mean()
df['max'] = round(df['media'] + (df['media'] * 0.10))
df['min'] = round(df['media'] - (df['media'] * 0.10))

# criando as opções para se usar no dropdown de varas
opcoes = list(df2['vara'].unique())
opcoes.append('Toda seção')


# inicio da aplicação do dashboard
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
                            html.Img(src="assets/images/logo-jfrn.svg"),
                            html.H3(children='Selecione a vara'),
                            dcc.Dropdown(opcoes, value='Toda seção', id='varas',
                                         className='dropdown'),
                        ],
                    ),
                    html.Div(
                        className='graph-content',
                        children=[
                            html.Div(
                                className='graph-principal',
                                children=[
                                    dcc.Graph(
                                        id='grafico_quantidade_proc',
                                    ),
                                ]
                            ),
                            html.Div(
                                className='graph-second',
                                children=[
                                    html.Div(
                                        className='graph-container',
                                        children=[
                                            dcc.Graph(
                                                id='grafico_quantidade_assuntos',

                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className='graph-container',
                                        children=[
                                            dcc.Graph(
                                                id='grafico_quantidade_adv',

                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            html.Div(
                                className='container-table',
                                children=[
                                    html.H2(
                                        className='title-cotainer-table',
                                        children=['Detalhamento de processos por vara']
                                    ),
                                    html.Div(
                                        className='table',
                                        id='table'
                                    )
                                ]
                            ),
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
        Output('grafico_quantidade_adv', 'figure'),
        Output('table', 'children'),
    ],
    Input('varas', 'value')

)
def update_output(value):
    figSeries = go.Figure()
    # quando o valor do dropdown for toda a seção trazer as informações  de toda a seção
    if value == 'Toda seção':
        # Inserindo a média móvel no gráfico
        figSeries.add_trace(
            go.Scatter(
                x=df.index,
                y=df['max'],
                name='Intervalo Máximo',
                fill=None,
                showlegend=False,
                line=dict(
                    color='green',
                    width=1,
                    dash='dot'
                )
            )
        )
        figSeries.add_trace(
            go.Scatter(
                x=df.index,
                y=df['media'],
                name='Média Móvel',
                fill='tonexty',
                line=dict(
                    color='green',
                    width=2,
                    dash='dot'
                )
            )
        )
        figSeries.add_trace(
            go.Scatter(
                x=df.index,
                y=df['min'],
                name='Intervalo Mínimo',
                fill='tonexty',
                showlegend=False,
                line=dict(
                    color='green',
                    width=1,
                    dash='dot'
                )
            )
        )
        # criando o gráfico com o quantitativo de processos
        figSeries.add_trace(
            go.Scatter(
                x=df.index,
                y=df['quantidade'],
                name='Gráfico do quantitativo de processos',
                line=dict(
                    color='tomato',
                    width=2,
                )
            )
        )
        # criando o gráfico com os assuntos mais relevantes
        figAssuntos = px.bar(
            data_assuntos,
            y=data_assuntos['assuntos'],
            x=data_assuntos['quantidade_assuntos'],
            color=data_assuntos['quantidade_assuntos'],
            color_continuous_scale="GnBu",
            orientation='h'

        )
        # criando o gráfico com os advogados que mais protocoloram processos
        figAdv = px.bar(
            data_advogados,
            y=data_advogados['advogados'],
            x=data_advogados['quantidade_advogados'],
            color=data_advogados['quantidade_advogados'],
            color_continuous_scale="GnBu",
            orientation='h'
        )
        figSeries.update_layout(
            hovermode='x unified',
            title_text='Relação do quantitativo de processos mensais em toda a seção',
            title_x=0.5,
            xaxis_title='Meses',
            yaxis_title=None,
            legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='bottom',
                y=1,
                x=0.5,
                font=dict(
                    size=12
                )
            )
        )
        figAssuntos.update_layout(
            yaxis_title=None,
            xaxis_title=None,
            legend_title_text='Assuntos',
            title_text='Assuntos mais relevantes em toda a seção',
            title_x=0.5,
            coloraxis_colorbar={
                'title': ''
            }
        )
        figAdv.update_layout(
            yaxis_title=None,
            xaxis_title=None,
            legend_title_text='Advogados',
            title_text='Advogados com mais processos em toda a seção',
            title_x=0.5,
            coloraxis_colorbar={
                'title': ''
            }
        )
        table_assunto = None

    else:
        # fazendo a separação do quantitativo de processos por vara
        tabela_filtrada = df2.loc[df2['vara'] == value, :]
        serie_filtrada = tabela_filtrada.copy()
        serie_filtrada['date'] = pd.to_datetime(serie_filtrada['date'], format='%m/%d/%Y')
        serie_filtrada['quantidade'] = 1
        serie_filtrada = serie_filtrada.resample('M', on='date').sum()

        # fazendo a contagem de assuntos por vara
        tabela_assuntos = tabela_filtrada['assunto'].value_counts()

        # fazendo a contagem de advogados por vara
        tabela_adv = tabela_filtrada['advogados'].value_counts()

        # Calculo da média móvel
        serie_filtrada['media'] = serie_filtrada['quantidade'].rolling(2).mean()
        serie_filtrada['max'] = round(serie_filtrada['media'] + (serie_filtrada['media'] * 0.10))
        serie_filtrada['min'] = round(serie_filtrada['media'] - (serie_filtrada['media'] * 0.10))

        # Fazendo o tratamento dos dados para ser exibido da melhor forma na tabela
        tabela_filtrada.drop(['quantidade'], axis=1, inplace=True)
        tabela_filtrada.columns = ['Num. processo', 'Data protocolação', 'vara', 'Assunto', 'Advogados']

        # Inserindo a média móvel no gráfico de acordo com a vara especifica
        figSeries.add_trace(
            go.Scatter(
                x=serie_filtrada.index,
                y=serie_filtrada['max'],
                name='Intervalo Máximo',
                fill=None,
                showlegend=False,
                line=dict(
                    color='green',
                    width=1,
                    dash='dot'
                )
            )
        ),
        figSeries.add_trace(
            go.Scatter(
                x=serie_filtrada.index,
                y=serie_filtrada['media'],
                name='Média Móvel',
                fill='tonexty',
                line=dict(
                    color='green',
                    width=2,
                    dash='dot'
                )
            )
        ),
        figSeries.add_trace(
            go.Scatter(
                x=serie_filtrada.index,
                y=serie_filtrada['min'],
                name='Intervalo Mínimo',
                fill='tonexty',
                showlegend=False,
                line=dict(
                    color='green',
                    width=1,
                    dash='dot'
                )
            )
        ),
        # criando o gráfico com o quantitativo de processos para a vara selecionada
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
        # criando o gráfico com os assuntos mais relevantes para a vara selecionada
        figAssuntos = px.bar(
            tabela_assuntos,
            y=tabela_assuntos.index,
            x=tabela_assuntos.values,
            color=tabela_assuntos.values,
            color_continuous_scale="GnBu",
        )
        # criando o gráfico com os advogados que mais protocoloram processos para a vara selecionada
        figAdv = px.bar(
            tabela_adv,
            y=tabela_adv.index,
            x=tabela_adv.values,
            color=tabela_adv.values,
            color_continuous_scale="GnBu",
        )
        # Criando a tabela com o detalhamento dos processos para a vara selecionada
        table_assunto = dash_table.DataTable(
            id='table',
            data=tabela_filtrada.to_dict('records'),
            fixed_rows={'headers': True, 'data': 0},
            style_table={'minWidth': '100%'},
            style_header={'textAlign': 'center', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'center'},
            columns=[{'id': x, 'name': x} for x in tabela_filtrada.columns],
            page_size=10
        )
        figSeries.update_layout(
            hovermode='x unified',
            title_text='Relação do quantitativo de processos mensais na vara',
            title_x=0.5,
            xaxis_title='Meses',
            yaxis_title=None,
            legend=dict(
                orientation='h',
                xanchor='center',
                yanchor='bottom',
                y=1,
                x=0.5,
                font=dict(
                    size=12
                )
            )
        )
        figAssuntos.update_layout(
            yaxis_title=None,
            xaxis_title=None,
            legend_title_text='Assuntos',
            title_text='Assuntos mais relevantes na vara',
            title_x=0.5,
            coloraxis_colorbar={
                'title': ''
            }
        )
        figAdv.update_layout(
            yaxis_title=None,
            xaxis_title=None,
            legend_title_text='Advogados',
            title_text='Advogados com mais processos na vara',
            title_x=0.5,
            coloraxis_colorbar={
                'title': ''
            }
        )

    return figSeries, figAssuntos, figAdv, table_assunto


if __name__ == '__main__':
    app.run_server(debug=True)
