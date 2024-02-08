import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def caminho_absoluto(caminho_relativo_com_barras_normais):
    
    caminho_base = os.getcwd()

    caminho_absoluto = os.path.join(caminho_base, caminho_relativo_com_barras_normais)

    return caminho_absoluto

def refatorar_indece(df, nome_index):
    
    qnt_linha = df.shape[0] + 1

    index = [i for i in range(1, qnt_linha)]

    df.set_index(pd.Index(index), inplace=True)

    df.index.name = nome_index
    
    return df

situacao_final = pd.read_excel(caminho_absoluto('data/tratamento_curva_abc/dados_tratados/situacao_final.xlsx')).set_index('Ordem')
mapa = pd.read_excel(caminho_absoluto('mapa_estoque/mapa_orientacao.xlsx')).fillna('-').astype(str)

mapa_prateleira = pd.read_excel(caminho_absoluto('mapa_estoque/mapa_prateleira_orientacao.xlsx'), sheet_name=None)

def criar_mapa_de_calor_saida(coluna_endereco, coluna_saida, mapa, nome_do_grafico):

    # Agrupar por endereço e somar os dados da coluna
    coluna_x_endereço = situacao_final[[coluna_endereco, coluna_saida]].groupby([coluna_endereco]).sum().reset_index()

    # Cria um serie com os valores, para transformar em um dicionario
    coluna_x_endereço = pd.Series(coluna_x_endereço[coluna_saida].values, index = coluna_x_endereço[coluna_endereco]).to_dict()

    # Mapeia as informações da coluna com os indereços
    coluna_por_enderco = mapa.replace(coluna_x_endereço)

    # Criar o mapa de calor
    fig = go.Figure(data=go.Heatmap(
                  z=coluna_por_enderco.values, # Valores para a cor
                  x=coluna_por_enderco.columns, # Eixos X
                  y=coluna_por_enderco.index, # Eixo Y
                  colorbar_title='Saída',
                  colorscale=['LightBlue', 'DarkBlue'],
                  text=mapa,
                  texttemplate='%{text}',
                  textfont={'size':10}
                  ))

    # Ajustes finais no layout
    fig.update_layout(title_text=nome_do_grafico,
                    yaxis=dict(autorange='reversed'),
                    xaxis_showgrid=False, yaxis_showgrid=False,
                    xaxis_zeroline=False, yaxis_zeroline=False,
                    autosize=False,
                    width=1450,
                    height=len(mapa.index) * 13,
                    )

    fig.update_xaxes(side='top')
    return fig

def criar_mapa_de_calor_ocupacao(nome_do_grafico):
    ## Ocupação (Cadastro)

    coluna_x_endereço = situacao_final[['Ender.Cx.Fechada', 'Código']]

    if opcao_coluna == 'Produtos com estoque':
        selecao_armazenado = situacao_final['Estoque Cx'] != '0'
        qnt_com_estoque_x_endereco = coluna_x_endereço[selecao_armazenado].groupby(['Ender.Cx.Fechada']).count().reset_index()
        # Cria um serie com os valores, para transformar em um dicionario
        tipo_da_ocupacao = pd.Series(qnt_com_estoque_x_endereco['Código'].values, index = qnt_com_estoque_x_endereco['Ender.Cx.Fechada']).to_dict()

    else:
        qnt_enderecado_x_endereco = coluna_x_endereço.groupby(['Ender.Cx.Fechada']).count().reset_index()
        # Cria um serie com os valores, para transformar em um dicionario
        tipo_da_ocupacao = pd.Series(qnt_enderecado_x_endereco['Código'].values, index = qnt_enderecado_x_endereco['Ender.Cx.Fechada']).to_dict()

    # Mapeia as informações da coluna com os indereços
    coluna_por_enderco = mapa.replace(tipo_da_ocupacao)
    
    # Criar o mapa de calor
    fig = go.Figure(data=go.Heatmap(
                z=coluna_por_enderco.values, # Valores para a cor
                x=coluna_por_enderco.columns, # Eixos X
                y=coluna_por_enderco.index, # Eixo Y
                colorbar_title='Saída',
                colorscale=['LightBlue', 'DarkBlue'],
                text=mapa,
                texttemplate='%{text}',
                textfont={'size':10}
                ))

    # Ajustes finais no layout
    fig.update_layout(title_text=nome_do_grafico,
                    yaxis=dict(autorange='reversed'),
                    xaxis_showgrid=False, yaxis_showgrid=False,
                    xaxis_zeroline=False, yaxis_zeroline=False,
                    autosize=False,
                    width=1450,
                    height=1200,
                    )

    fig.update_xaxes(side='top')
    return fig

st.title('Ocupação do estoque')

aba1, aba2, aba3 = st.tabs(['Caixa Fechada', 'Flowrack', 'Prateleira'])

with aba1:

    tipo_de_visualizacao = st.radio('Selecione o tipo de vizualização:',
                                    ['Ocupação', 'Saída'],
                                    captions=['Ocupação fisica do estoque', 'Saídas por atividades e vendas'])

    if tipo_de_visualizacao == 'Saída':
        colunas = ['Ativ.Ressupr.Frac',
                    'Ativ.Ressupr.Cx',
                    'Ativ.Ressupr.Geral',
                    'Qtde Venda Frac',
                    'Qtde Venda Cx',
                    'Qtde Venda Geral',
                    'Dias Pedido Frac',
                    'Dias Pedido Cx',
                    'Dias Pedido Geral',
                    'Média por dia frac',
                    'Média por dia cx',
                    'Média por dia geral',
                    ]
        
    else:
        colunas = ['Produtos Cadastrados',
                   'Produtos com estoque']

    opcao_coluna = st.selectbox('Selecione o tipo de saída:', colunas)

    if tipo_de_visualizacao == 'Saída':
        chart = criar_mapa_de_calor_saida('Ender.Cx.Fechada', opcao_coluna, mapa, f'{opcao_coluna} por Endereço de Caixa')

    else:
        chart = criar_mapa_de_calor_ocupacao(f'{opcao_coluna} por Endereço de Caixa')

    st.plotly_chart(chart, use_container_width=True)
    
with aba2:
    ''
    
with aba3:
    corredores = {'10' : mapa_prateleira['10'],
                '11' : mapa_prateleira['11'],
                '12' : mapa_prateleira['12'],
                '13' : mapa_prateleira['13'],
                '14' : mapa_prateleira['14'],
                '15' : mapa_prateleira['15'],
                '16' : mapa_prateleira['16'],
                '17' : mapa_prateleira['17'],
                '18' : mapa_prateleira['18'],
                '19' : mapa_prateleira['19'],
                '20' : mapa_prateleira['20'],
                '21' : mapa_prateleira['21'],
                '22' : mapa_prateleira['22'],
                '23' : mapa_prateleira['23'],
                '24' : mapa_prateleira['24'],
                '25' : mapa_prateleira['25'],
                '26' : mapa_prateleira['26'],
                '27' : mapa_prateleira['27'],
                '28' : mapa_prateleira['28'],
                '29' : mapa_prateleira['29'],
                }

    mapa_geral_plateleiras = pd.concat(corredores)
    refatorar_indece(mapa_geral_plateleiras, None)

    radio_selecao_visao_prateleiras = st.radio('Selecione o tipo de vizualização das prateleiras:', ['Geral', 'Por corredor'])

    if radio_selecao_visao_prateleiras == 'Geral':

        chart = criar_mapa_de_calor_saida('Ender.Fracionado', 'Qtde Venda Frac', mapa_geral_plateleiras, 'teste')

        st.plotly_chart(chart, use_container_width=True)

    else:

        corredor = st.selectbox('Selecion o Corredor:', ('10',
                                                         '11',
                                                         '12',
                                                         '13',
                                                         '14',
                                                         '15',
                                                         '16',
                                                         '17',
                                                         '18',
                                                         '19',
                                                         '20',
                                                         '21',
                                                         '22',
                                                         '23',
                                                         '24',
                                                         '25',
                                                         '26',
                                                         '27',
                                                         '28',
                                                         '29',
                                                         ))

        chart = criar_mapa_de_calor_saida('Ender.Fracionado', 'Qtde Venda Frac', corredores[f'{corredor}'], 'teste')

        st.plotly_chart(chart, use_container_width=True)
