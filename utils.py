#utils.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import plotly.express as px
import math
from streamlit_config import *

# Variáveis globais

cdi_anual_medio = 0.11
qtdade_desviopadrao = 2

class Config:

    patrimonio = 0.0
    aporte = 0.0
    inicio_aporte = ""
    duracao_aporte = 0
    resgate = 0.0
    inicio_resgate = ""
    imposto = 0.0
    prazo = 0
    perfil = ""
    cdi_percent = 0

def inicializa_webpage():

    setup_config = Config

    data_maxima = date(2099, 12, 31)

    streamlit_page_config()
    streamlit_css()

    st.sidebar.title("Informações para projeção")
    
    # Inputs no sidebar
    setup_config.patrimonio = st.sidebar.number_input("Patrimônio investido atual (R$):", min_value=0.0, step=100.0)
    setup_config.aporte = st.sidebar.number_input("Valor do aporte mensal (R$):", min_value=0.0, step=100.0)
    setup_config.inicio_aporte = st.sidebar.date_input("Data para iniciar os aportes:", value=datetime.today().date(), format="DD/MM/YYYY", min_value=datetime.today().date(), max_value=data_maxima)
    setup_config.duracao_aporte = st.sidebar.number_input("Prazo dos aportes (em meses):", min_value=0, step=1)
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    setup_config.resgate = st.sidebar.number_input("Valor do resgate mensal (R$):", min_value=0.0, step=100.0)
    setup_config.inicio_resgate = st.sidebar.date_input("Quando pretende iniciar os resgates:", min_value=setup_config.inicio_aporte+relativedelta(months=setup_config.duracao_aporte), format="DD/MM/YYYY", max_value=data_maxima)
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    # setup_config.imposto = st.sidebar.selectbox("Selecione o imposto de renda (%)", [22.5, 20.0, 17.5, 15.0, 10.0, 0.0])
    setup_config.prazo = st.sidebar.number_input("Prazo da projeção (em meses):", 
                                                 value=relativedelta(setup_config.inicio_resgate, datetime.today()).years*12 + relativedelta(setup_config.inicio_resgate,datetime.today()).months + 120, 
                                                 min_value=relativedelta(setup_config.inicio_resgate, datetime.today()).years*12 + relativedelta(setup_config.inicio_resgate,datetime.today()).months,
                                                 step=1)
    setup_config.perfil = st.sidebar.selectbox("Selecione o perfil de risco:", ["Conservador", "Moderado", "Arrojado", "Agressivo"])

    # Ajustar intervalo do slider CDI com base no perfil selecionado
    if setup_config.perfil == "Conservador":
        cdi_min = 100
        cdi_max = 120
    elif setup_config.perfil == "Moderado":
        cdi_min = 120
        cdi_max = 130
    elif setup_config.perfil == "Arrojado":
        cdi_min = 130
        cdi_max = 170
    else:  # Agressivo
        cdi_min = 170
        cdi_max = 200

    setup_config.cdi_percent = st.sidebar.slider("Percentual do CDI (%)", 
                                    min_value=cdi_min, 
                                    max_value=cdi_max, 
                                    value=cdi_min, 
                                    step=10,
                                    format="%d%%")
    
    return True

def calcular_primeiro_milhao(aporte_mensal, duracao_aporte, taxa_retorno_anual, valor_inicial):

    # Converter a taxa de retorno anual para mensal
    taxa_retorno_mensal = (1 + taxa_retorno_anual) ** (1/12) - 1

    # Valor inicial
    valor_acumulado = valor_inicial
    
    # Data inicial
    data_inicial = datetime.today()
    data_atual = data_inicial
    
    # Contador de meses
    meses = 0
    
    # Loop até atingir o primeiro milhão
    while valor_acumulado < 1_000_000:

        if meses > duracao_aporte:

            aporte_mensal = 0

        # Adicionar aporte mensal
        valor_acumulado += aporte_mensal

        # Aplicar taxa de retorno mensal
        valor_acumulado *= (1 + taxa_retorno_mensal)
        
        # Incrementar contador de meses
        meses += 1
        
        # Atualizar a data
        data_atual = data_inicial + timedelta(days=30*meses)

    return data_atual.strftime('%d/%m/%Y')

def centralizar_coluna_html(df):

    df = df.reset_index(drop=True)  # Remove a coluna de índices
    
    # Definir o estilo para a segunda coluna
    def centralizar_segunda_coluna(x):
        return ['text-align: center' if i == 1 else '' for i in range(len(x))]
    
    # Aplicar estilo ao DataFrame
    styled_df = df.style.apply(centralizar_segunda_coluna, axis=1)
    
    # Converter para HTML e remover o índice
    html = styled_df.to_html(index=False)
    
    return html

def determinar_volatilidade(cdi_percentual):
    if cdi_percentual <= 120:
        return 0.015
    elif cdi_percentual <= 130:
        return 0.03
    elif cdi_percentual <= 170:
        return 0.05
    else:
        return 0.08

def calcular_projecao(self_config):

    cdi_mensal = ((1 + cdi_anual_medio) ** (1 / 12)) - 1

    # Definir a volatilidade anual com base no percentual do CDI
    if self_config.perfil == "Conservador": volatilidade_anual = 0.015
    elif self_config.perfil == "Moderado":  volatilidade_anual = 0.03
    elif self_config.perfil == "Arrojado":  volatilidade_anual = 0.05
    else: volatilidade_anual = 0.07

    # volatilidade_mensal = ((1 + volatilidade_anual) **(1/12)) - 1        

    # Conversão do início dos resgates para um índice de meses
    meses_ate_resgate = (self_config.inicio_resgate.year - datetime.now().year) * 12 + self_config.inicio_resgate.month - datetime.now().month

    tempo_ate_aporte = (self_config.inicio_aporte - datetime.today().date()).days // 30

    historico_patrimonio = pd.DataFrame({
        'Sem aporte': [],
        'Com aporte': []
    })

    patrimonio_final_sem_aporte = 0
    patrimonio_final_com_aporte = 0

    # Inicializando o patrimônio inicial
    if self_config.patrimonio > 0:

        historico_patrimonio.loc[len(historico_patrimonio)] = [self_config.patrimonio, self_config.patrimonio]
        patrimonio_final_com_aporte = self_config.patrimonio
        patrimonio_final_sem_aporte = self_config.patrimonio

    else:

        if self_config.aporte > 0 and self_config.duracao_aporte > 0:

            historico_patrimonio.loc[len(historico_patrimonio)] = [0, self_config.aporte]
            patrimonio_final_com_aporte = self_config.aporte
            # patrimônio_final_sem_aporte = self_config.aporte

    for mes in range(1, self_config.prazo + 1):       

        if self_config.aporte > 0 and self_config.duracao_aporte > 0:

            # Calcular o rendimento mensal com aporte
            if tempo_ate_aporte <= mes <= tempo_ate_aporte + self_config.duracao_aporte:

                rendimento_mensal = (patrimonio_final_com_aporte + self_config.aporte) * cdi_mensal * (self_config.cdi_percent / 100)
                patrimonio_final_com_aporte += rendimento_mensal + self_config.aporte

            elif mes > tempo_ate_aporte + self_config.duracao_aporte:
                rendimento_mensal = patrimonio_final_com_aporte * cdi_mensal * (self_config.cdi_percent / 100)
                patrimonio_final_com_aporte += rendimento_mensal

        if self_config.resgate > 0 and mes >= meses_ate_resgate:

            # Calcular o resgate com imposto
            
            rendimento_mensal = patrimonio_final_sem_aporte * cdi_mensal * (self_config.cdi_percent / 100)
            patrimonio_final_sem_aporte += rendimento_mensal
            resgate_com_imposto = self_config.resgate * (1 + self_config.imposto / 100)
            patrimonio_final_sem_aporte -= resgate_com_imposto

        if self_config.patrimonio > 0:

            rendimento_mensal = patrimonio_final_sem_aporte * cdi_mensal * (self_config.cdi_percent / 100)
            patrimonio_final_sem_aporte += rendimento_mensal
        
            
        # Armazenar os valores mensais no histórico
        historico_patrimonio.loc[len(historico_patrimonio)] = [patrimonio_final_sem_aporte, patrimonio_final_com_aporte]
        

    # Resultados finais
    patrimonio_final_sem_aporte = historico_patrimonio['Sem aporte'].iloc[-1]
    patrimonio_final_com_aporte = historico_patrimonio['Com aporte'].iloc[-1]   


    # Aplicar volatilidade
    # volatilidade = np.random.normal(0, volatilidade_mensal)
    # volatilidade = 0
    # patrimonio_final_sem_aporte *= (1 + volatilidade)
    # patrimonio_final_com_aporte *= (1 + volatilidade)

    # Registro do patrimônio
    # historico_patrimonio.loc[len(historico_patrimonio)] = [patrimonio_final_sem_aporte, patrimonio_final_com_aporte]
        
               
    return historico_patrimonio

def atualizar_grafico(self_config):

    # Calcular a projeção
    historico_patrimonio = calcular_projecao(self_config)   

    curva_cdi = []

    meses = np.arange(self_config.prazo+1)
    cdi_mensal = (1 + cdi_anual_medio) ** (1 / 12) - 1

    # Calcular a curva do CDI com base no patrimônio inicial ou aportes
    if self_config.patrimonio > 0:   
        
        curva_cdi = self_config.patrimonio * ((1 + cdi_mensal) ** meses)

    else:

        if self_config.duracao_aporte > 0:

            curva_cdi = self_config.aporte * ((1 + cdi_mensal) ** meses)
        
    curva_cdi = list(curva_cdi)

    # Obter perfil de risco e volatilidade
    volatilidade_anual_estimada = determinar_volatilidade(self_config.cdi_percent)
    retorno_anual_estimado = cdi_anual_medio * self_config.cdi_percent/100

    plotar_grafico(curva_cdi, historico_patrimonio, self_config)
    
    configuracao_perfis(self_config.perfil, retorno_anual_estimado, volatilidade_anual_estimada)

def plotar_grafico(curva_cdi, historico_patrimonio, self_config):
    
    fig = go.Figure()

    # Calcular a variação percentual em relação ao valor inicial
    percentual_variacao_sem_aporte = (historico_patrimonio["Sem aporte"] / historico_patrimonio["Sem aporte"].iloc[0]) - 1
    percentual_variacao_com_aporte = (historico_patrimonio["Com aporte"] / historico_patrimonio["Com aporte"].iloc[0]) - 1

    if self_config.patrimonio > 0:

        # Adicionar a curva do patrimônio sem aporte
        fig.add_trace(go.Scatter(
            x=historico_patrimonio.index,
            y=historico_patrimonio["Sem aporte"],
            mode='lines',
            name='Patrimônio sem aporte',
            line=dict(color='#DDA0DD', width=4),
            hoverinfo='text',
            text=[f'Retorno sem aporte: {percentual*100:.2f}%' for percentual in percentual_variacao_sem_aporte],
            marker=dict(size=26, symbol='circle', color='#DDA0DD')
        ))

    if self_config.aporte > 0 and self_config.duracao_aporte > 0:

        # Adicionar a curva do patrimônio com aporte
        fig.add_trace(go.Scatter(
            x=historico_patrimonio.index,
            y=historico_patrimonio["Com aporte"],
            mode='lines',
            name='Patrimônio com aporte',
            line=dict(color='#00f262', width=4),
            hoverinfo='text',
            text=[f'Retorno com aporte: {percentual*100:.2f}%' for percentual in percentual_variacao_com_aporte],
            marker=dict(size=26, symbol='circle', color='#B87333')
        ))

    # Ajustar a curva do CDI para iniciar no mesmo valor do patrimônio inicial
    if curva_cdi:
        curva_cdi_inicial = curva_cdi[0]
        if curva_cdi_inicial != 0:
            curva_cdi = [curva_cdi_inicial] + [valor for valor in curva_cdi[1:]]
            percentual_variacao_cdi = [(valor / curva_cdi_inicial - 1) * 100 for valor in curva_cdi]
        else:
            percentual_variacao_cdi = [0 for _ in curva_cdi]
    else:
        percentual_variacao_cdi = []

    # Adicionar a curva do CDI
    fig.add_trace(go.Scatter(
        x=historico_patrimonio.index,
        y=curva_cdi,
        mode='lines',
        name='Curva CDI',
        line=dict(color='#FFFFF0', width=4, dash='dash'),
        hoverinfo='text',
        text=[f'CDI: {percentual:.2f}%' for percentual in percentual_variacao_cdi],
        marker=dict(size=26, symbol='diamond', color='#FFFFF0')
    ))

    # Configurações do gráfico       
    fig.update_layout(
        title=dict(
            text="",  # Definir o título como uma string vazia           
            xanchor='center'
        ),
        annotations=[
            dict(
                x=0.5,
                y=1.2,  # Ajuste a posição vertical conforme necessário
                xref='paper',
                yref='paper',
                text='Projeção Patrimonial',
                # text="<span style='text-shadow: 1px 1px 0 #00f262, -1px -1px 0 #00f262, 1px -1px 0 #00f262, -1px 1px 0 #00f262;'>Projeção Patrimonial</span>",
                showarrow=False,
                font=dict(size=36, family='Verdana', color='#00f262'),
                xanchor='center'
            )
        ],
        xaxis=dict(
            title="Meses",
            title_font=dict(size=18, family='Verdana', color='#FFFFFF'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)',
            zeroline=False,
            tickfont=dict(size=14, color='#FFFFFF'),
            showline=True,
            mirror=True,
            ticks='inside',
            showspikes=True,
            spikemode='across',
            spikedash='solid',
            spikethickness=1,
            spikesnap='cursor',
            showticklabels=True,
            ticklen=8,
            tickwidth=2,
            tickcolor='#FFFFFF',
            gridwidth=1,
            minor=dict(
                ticklen=6,
                tickwidth=1,
                tickcolor='#AAAAAA',
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)'
            )
        ),
        yaxis=dict(
            title="Patrimônio (em R$)",
            title_font=dict(size=18, family='Verdana', color='#FFFFFF'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)',
            zeroline=False,
            tickfont=dict(size=14, color='#FFFFFF'),
            showline=True,
            mirror=True,
            ticks='inside',
            showspikes=True,
            spikemode='across',
            spikedash='solid',
            spikethickness=1,
            spikesnap='cursor',
            showticklabels=True,
            ticklen=8,
            tickwidth=2,
            tickcolor='#FFFFFF',
            gridwidth=1,
            minor=dict(
                ticklen=6,
                tickwidth=1,
                tickcolor='#AAAAAA',
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)'
            )
        ),
        legend=dict(
            title=dict(text="Legenda", font=dict(size=14, family='Verdana', color='#FFFFFF')),
            font=dict(size=12, color='#FFFFFF'),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255, 255, 255, 0.2)',
            borderwidth=1
        ),
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=40, r=40, t=60, b=60)
    )

    # Identificar o primeiro valor negativo do patrimônio
    idx_primeiro_negativo = historico_patrimonio[historico_patrimonio["Sem aporte"] < 0].index.min()
    
    if pd.notna(idx_primeiro_negativo):
        valor_primeiro_negativo = historico_patrimonio.loc[idx_primeiro_negativo, "Sem aporte"]
        
        # Adicionar uma linha vertical indicando o ponto onde o patrimônio zerou
        fig.add_trace(go.Scatter(
            x=[idx_primeiro_negativo],
            y=[valor_primeiro_negativo],
            mode='markers',
            marker=dict(size=10, symbol='circle', color='red'),
            name='Patrimônio Zerado',
            showlegend=True
        ))

        fig.add_vline(
            x=idx_primeiro_negativo,
            line=dict(color='red', width=4, dash='dash'),
            annotation_text='',
            annotation_position='top right',
            annotation_font=dict(color='red', size=18)
        )

    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)

    if 0 < self_config.patrimonio < 1_000_000 and 0 < self_config.aporte < 1_000_000 and idx_primeiro_negativo == 0:
    
        # Identificar o primeiro milhão alcançado
        data_primeiro_milhao = calcular_primeiro_milhao(self_config.aporte, self_config.duracao_aporte, cdi_anual_medio*self_config.cdi_percent/100, self_config.patrimonio)
                
        st.write(f"""
                <span style='
                    font-size: 30px; 
                    color: green; 
                    text-shadow: 
                        1px 1px 0 #FFFFFF,
                        -1px -1px 0 #FFFFFF,
                        1px -1px 0 #FFFFFF,
                        -1px 1px 0 #FFFFFF;
                '>✔️</span> 
                <span style='
                    font-size: 24px; 
                    color: #9ACD32;                 
                '>PARABÉNS! O seu primeiro milhão será atingido em {data_primeiro_milhao}</span>
            """, unsafe_allow_html=True) 

    if self_config.patrimonio > 0.0:

        if idx_primeiro_negativo > 0:

            # Usar st.write para renderizar o HTML
            st.write(f"""
                <span style='
                    font-size: 30px; 
                    color: red; 
                    text-shadow: 
                        1px 1px 0 #FFFFFF,
                        -1px -1px 0 #FFFFFF,
                        1px -1px 0 #FFFFFF,
                        -1px 1px 0 #FFFFFF;
                '>❌</span> 
                <span style='
                    font-size: 24px; 
                    color: #F08080;                 
                '>CUIDADO: O patrimônio irá zerar no ano de {datetime.now().year + int(idx_primeiro_negativo/12)} caso você não faça mais aportes</span>
            """, unsafe_allow_html=True)       

        else:

            # Usar st.write para renderizar o HTML
            st.write(f"""
                <span style='
                    font-size: 30px; 
                    color: green; 
                    text-shadow: 
                        1px 1px 0 #FFFFFF,
                        -1px -1px 0 #FFFFFF,
                        1px -1px 0 #FFFFFF,
                        -1px 1px 0 #FFFFFF;
                '>✔️</span> 
                <span style='
                    font-size: 24px; 
                    color: #9ACD32;                 
                '>PARABÉNS! O seu patrimônio não zerou ao longo do período selecionado</span>
            """, unsafe_allow_html=True) 

    if self_config.resgate> 0 and self_config.prazo > 0:

        cdi_mensal = ((1 + cdi_anual_medio) ** (1 / 12)) - 1

        diferenca = relativedelta(self_config.inicio_resgate, self_config.inicio_aporte)

        diferenca_meses = diferenca.years * 12 + diferenca.months
        
        # Cálculo do resgate mensal bruto
        resgate_mensal_bruto = (self_config.patrimonio * cdi_mensal) / (1 - (1 + cdi_mensal) ** -(self_config.prazo - diferenca_meses))

        # Ajuste para o imposto
        resgate_mensal_maximo = resgate_mensal_bruto / (1 - self_config.imposto/100) 

        if resgate_mensal_maximo > 0:

            st.write(f"""
                        <span style='
                            font-size: 30px; 
                            color: green; 
                            text-shadow: 
                                1px 1px 0 #FFFFFF,
                                -1px -1px 0 #FFFFFF,
                                1px -1px 0 #FFFFFF,
                                -1px 1px 0 #FFFFFF;
                        '>⚠️</span> 
                        <span style='
                            font-size: 24px; 
                            color: #FFCC00;                 
                        '>ATENÇÃO! Iniciando os resgates em {self_config.inicio_resgate.strftime("%d/%m/%Y")}, o valor mensal máximo para que o patrimônio acabe em {self_config.prazo} meses é de R${resgate_mensal_maximo:,.2f}</span>
                    """, unsafe_allow_html=True) 
  
    st.markdown("<hr>", unsafe_allow_html=True)

def configuracao_perfis(perfil, retorno, volatilidade):

    # Definir os dados da tabela
    dados_tabela = {
        "Ativo": ["Renda Fixa Pós-Fixado", 
                  "Renda Fixa Inflação", 
                  "Renda Variável", 
                  "Crédito Privado Inflação", 
                  "Renda Fixa Pré-Fixado", 
                  "Internacional", 
                  "Alternativos"],        
    }

    # Definir os dados das características da carteira
    caracteristicas_carteira = {
        "Característica": ["Volatilidade (anual)", "Sharpe esperado", "Retorno esperado (anual)"],
        "Valor" : [f"{volatilidade*100:.2f}%", "0.75", f"{retorno*100:.2f}%"]
    }

    if perfil == "Conservador":
        dados_tabela['Exposição'] = ["65%", "15%", "5%", "5%", "5%", "3%", "2%"]
    elif perfil == "Moderado":
        dados_tabela['Exposição'] = ["40.5%", "20%", "12%", "10%", "8.5%", "5%", "4%"]
    elif perfil == "Arrojado":
        dados_tabela['Exposição'] = ["25%", "20%", "17%", "15%", "12%", "7%", "4%"]
    else:
        dados_tabela['Exposição'] = ["26%", "25%", "15%", "12%", "10%", "8%", "4%"]
    
    # Criar DataFrames
    df_tabela = pd.DataFrame(dados_tabela)
    df_caracteristicas = pd.DataFrame(caracteristicas_carteira)

    exposicao_values = [float(valor.replace("%", "")) for valor in dados_tabela['Exposição']]
    labels = df_tabela['Ativo']

    # Criar gráfico de donut
    fig_perfil = go.Figure(data=[go.Pie(
        labels=labels,
        values=exposicao_values,
        hole=0.8,  # Define o tamanho do buraco para criar o efeito de donut
        marker=dict(colors=px.colors.sequential.Viridis),
        hoverinfo='label+percent',  # Informações mostradas ao passar o mouse
        hoverlabel=dict(font=dict(size=16))  # Ajusta o tamanho da fonte da anotação de hover
        
    )])

    # Adicionar informação no meio do donut
    fig_perfil.add_annotation(
        text=perfil,
        font_size=48,
        showarrow=False,
        x=0.5,  # Posicionar no centro do gráfico
        y=0.5,  # Posicionar no centro do gráfico
        align="center",
        xref="paper",
        yref="paper"
    )

    # Atualizar o layout do gráfico
    fig_perfil.update_layout(
        plot_bgcolor='#000000',  # Cor de fundo do gráfico (branco)
        paper_bgcolor='#120c2b',  # Cor de fundo da área externa ao gráfico (azul escuro)
        width=800,  # Largura do gráfico
        height=800,  # Altura do gráfico
        legend=dict(font=dict(size=16)),  # Ajusta o tamanho da fonte da legenda
        showlegend=True
    )

    # Ajustar o tamanho do texto em cada fatia
    fig_perfil.update_traces(
        textinfo='percent',  # Exibe rótulo e porcentagem
        textfont=dict(size=26)  # Ajusta o tamanho da fonte
    )    
    
    # Adicionar título
    st.title(f"Alocação por Perfil")

    # Organizar layout em duas colunas
    col1, col2 = st.columns([1, 2])

    # Função para centralizar a coluna da tabela
    def centralizar_coluna_html(df, col_name=None):
        if col_name:
            return df.style.set_properties(subset=[col_name], **{'text-align': 'center'}).to_html()
        return df.style.set_properties(**{'text-align': 'center'}).to_html()

    # Exibir a tabela na coluna 1
    with col1:
        st.write("### Alocação de Ativos")
        st.write(centralizar_coluna_html(df_tabela[['Ativo', 'Exposição']]), unsafe_allow_html=True)
        
        st.write("### Características da Carteira")
        st.write(centralizar_coluna_html(df_caracteristicas), unsafe_allow_html=True)

    # Exibir o gráfico de pizza na coluna 2
    with col2:
        st.plotly_chart(fig_perfil, use_container_width=True)