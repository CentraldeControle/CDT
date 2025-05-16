import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import timedelta
from dateutil.relativedelta import relativedelta

import os

st.set_page_config(
    layout="wide"
)

# Função para pré-processamento
def preprocess_data(data):
    # Corrigir o tipo de dado para datetime
    data['Data Filiação'] = pd.to_datetime(data['Data Filiação'], errors='coerce')
    # Remover linhas com datas inválidas
    data = data.dropna(subset=['Data Filiação'])
    # Converter datas para string no formato 'YYYY-MM-DD'
    data['Data Filiação'] = data['Data Filiação'].dt.strftime('%Y-%m-%d')
    # Adicionar coluna de quantidade com valor 1
    data['quantidade'] = 1
    # Agrupar por data de Filiação e franquia e calcular a contagem
    data = data.groupby(['Data Filiação','Franquia','Promotor de Vendas']).size().reset_index(name='quantidade')
    
    return data

def main():
    st.markdown("<h1 style='text-align: center;'>CDT</h1>", unsafe_allow_html=True)

    # List all Excel files in the current directory
    # List all Excel files in the current directory
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

    # Initialize an error message and data frames list
    error_message = ""
    data_frames = []

    if len(excel_files) < 3:
        error_message = 'Menos de três arquivos Excel encontrados na pasta.'
    else:
        # Sort the files by modification time, descending
        sorted_files = sorted(excel_files, key=lambda x: os.path.getmtime(x), reverse=True)
        # Select the three most recent Excel files
        selected_files = sorted_files[:3]

        # Read data from each selected Excel file
        for file_path in selected_files:
            try:
                # Read each Excel file into a DataFrame
                df = pd.read_excel(file_path)
                data_frames.append(df)
            except Exception as e:
                error_message = f"Failed to read {file_path}: {str(e)}"

    # Comment out to prevent execution
    # st.write(selected_files)
    # for df in data_frames:
    #     print(df.head())  # Display the first few rows of each DataFrame
    # print(error_message) if error_message else None

    if selected_files is not None:
        # Ler o arquivo Excel
        df = pd.read_excel("data.xlsx", header=0)
        
        # Pré-processamento dos dados
        processed_data = preprocess_data(df)
        
        
        # Adicionando o código de projeção
        processed_data['Data Filiação'] = pd.to_datetime(processed_data['Data Filiação'])
        processed_data['mes'] = processed_data['Data Filiação'].dt.month

        df_projec = processed_data.copy()
        
        # Convertendo a coluna 'Data Filiação' para o tipo datetime
        df_projec['Data Filiação'] = pd.to_datetime(df_projec['Data Filiação'])
        
        # Extraindo o mês da coluna 'Data Filiação' e criando uma nova coluna 'Mês'
  # Mapeando os números dos meses para os nomes em português
        meses_pt_br = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }

        # Calculando o primeiro dia do mês atual
        hoje = datetime.datetime.now().replace(day=1)

        # Calculando o primeiro dia do mês 3 meses atrás
        cinco_meses_atras = hoje - relativedelta(months=2)

        # Filtrar os dados para incluir apenas os últimos 3 meses completos
        df_ultimos_cinco_meses = df_projec[df_projec['Data Filiação'] >= cinco_meses_atras]

        # Adicionando a coluna 'Mês' com os nomes em português
        df_ultimos_cinco_meses['Mês'] = df_ultimos_cinco_meses['Data Filiação'].dt.month.map(meses_pt_br)

        # Agrupando os dados por franquia e mês, somando a quantidade para cada grupo
        dados_agrupados = df_ultimos_cinco_meses.groupby(['Franquia', 'Mês'])['quantidade'].sum().reset_index()

        # Definindo a ordem dos meses
        meses_ordem = [
            'Janeiro',
            'Fevereiro',
            'Março',
            'Abril',
            'Maio',
            'Junho',
            'Julho',
            'Agosto',
            'Setembro',
            'Outubro',
            'Novembro',
            'Dezembro'
        ]

        # Convertendo a coluna 'Mês' para o tipo categoria com a ordem definida
        dados_agrupados['Mês'] = pd.Categorical(dados_agrupados['Mês'], categories=meses_ordem, ordered=True)

        # Ordenando os dados pela ordem definida
        dados_agrupados = dados_agrupados.sort_values(by='Mês')

        # Definindo uma paleta de cores
        cores = ['#007bff', '#ffc107', '#28a745', '#17a2b8', '#ffc885']

        # Função para criar o gráfico
        def plotar_grafico(franquias_selecionadas):
            if not franquias_selecionadas:
                st.write(" ")
            else:
                # Ordenando as franquias selecionadas em ordem alfabética
                franquias_selecionadas.sort()

                cor_iter = iter(cores * (len(franquias_selecionadas) // len(cores) + 1))

                traces = []
                for franquia in franquias_selecionadas:
                    dados_franquia = dados_agrupados[dados_agrupados['Franquia'] == franquia]
                    trace = go.Bar(
                        x=dados_franquia['Mês'],
                        y=dados_franquia['quantidade'],
                        name=franquia,
                        hoverinfo='x+y',
                        text=dados_franquia['quantidade'],
                        textposition='outside',
                        marker=dict(color=next(cor_iter))
                    )
                    traces.append(trace)

                # Criando o layout do gráfico
                layout = go.Layout(
                    title='Vendas de cada franquia nos últimos 3 meses completos',
                    xaxis=dict(title='Mês'),
                    yaxis=dict(title='Quantidade'),
                )

                # Criando a figura
                fig = go.Figure(data=traces, layout=layout)




                # Ajustando o layout
                fig.update_layout(
                    showlegend=True,
                    yaxis=dict(range=[0, dados_agrupados['quantidade'].max() * 1.15]),
                )

                # Exibindo o gráfico
                st.plotly_chart(fig, use_container_width=True, config={
                    'displayModeBar': False,
                    'displaylogo': False
                })




        # Lista de franquias disponíveis
        franquias_disponiveis = dados_agrupados['Franquia'].unique()

        # Checkbox para selecionar as franquias
        franquias_selecionadas = st.sidebar.multiselect('Selecione as franquias para visualizar as vendas nos últimos 3 meses completos', franquias_disponiveis, default=franquias_disponiveis)

#====================================================================================================================================================================#
        
        current_date = datetime.datetime.now()

        # Tenta filtrar os dados para o mês atual
        df_current_month = processed_data[processed_data['Data Filiação'].dt.month == current_date.month]

        # Se não houver dados para o mês atual, busca os dados do mês anterior
        if df_current_month.empty:
            # Calcula o mês e ano anteriores
            if current_date.month == 1:
                previous_month = 12
                year = current_date.year - 1
            else:
                previous_month = current_date.month - 1
                year = current_date.year

            # Filtra os dados para o mês anterior
            df_current_month = processed_data[(processed_data['Data Filiação'].dt.month == previous_month) &
                                            (processed_data['Data Filiação'].dt.year == year)]


        # Calcular o total de quantidade para cada promotor
        df_total_por_promotor = df_current_month.groupby('Franquia')['quantidade'].sum().reset_index()
        

        def calcular_meta_restante(df_total_por_promotor, processed_data):
            # Obtém a data atual
            data_atual = datetime.date.today() - timedelta(days=1)
           
            # Verifica se existem dados para o mês atual no dataframe 'processed_data'
            if not processed_data[processed_data['Data Filiação'].dt.month == data_atual.month].empty:
                # Usa dados do mês atual
                primeiro_dia_mes_atual = data_atual.replace(day=1)
            else:
                if data_atual.month == 1:
                    data_atual = data_atual.replace(year=data_atual.year - 1, month=12, day=1)
                else:
                    data_atual = data_atual.replace(month=data_atual.month - 1, day=1)

            
            # Obtém o último dia do mês atual
            ultimo_dia_mes_atual = (data_atual.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            # Calcula quantos dias faltam para o fim do mês
            dias_restantes = (ultimo_dia_mes_atual - data_atual).days 
            
            # Calcula quantos dias passaram desde o primeiro dia do mês até a data atual, excluindo domingos
            dias_passados = sum(1 for i in range((data_atual - primeiro_dia_mes_atual).days + 1) if (primeiro_dia_mes_atual + timedelta(days=i)).weekday() != 6)
            
            # Garante que 'dias_passados' seja pelo menos 1 para evitar divisão por zero
            dias_passados = max(1, dias_passados)
            # Conta a quantidade de domingos restantes no mês
            domingos_restantes = sum(1 for i in range(dias_restantes) if (data_atual + timedelta(days=i)).weekday() == 6)
            
            # Calcula os dias restantes excluindo os domingos
            dias_restantes_sem_domingos = dias_restantes - domingos_restantes
            # Calcula a média diária excluindo os domingos
            df_total_por_promotor['media_diaria'] = df_total_por_promotor['quantidade'] / dias_passados
            
            # Multiplica a média diária pelo número de dias restantes
            df_total_por_promotor['meta_restante'] = df_total_por_promotor['media_diaria'] * dias_restantes_sem_domingos
            
            # Soma o total atingido até a data atual
            df_total_por_promotor['meta_restante'] += df_total_por_promotor['quantidade']
            
            return df_total_por_promotor

        # Chame a função passando 'processed_data' como argumento adicional se necessário.
        df_total_por_promotor = calcular_meta_restante(df_total_por_promotor, processed_data)
        
        # Criar o gráfico de barras usando Plotly Express
        fig2 = px.bar(df_total_por_promotor, x='Franquia', y='media_diaria',
                    title='Média Diária de Vendas de Cada Franquia até o Dia Anterior',
                    labels={'media_diaria': 'Média Diária de Vendas', 'Franquia': 'Franquia'},
                    color='Franquia',
                    color_discrete_sequence=cores)
        
        # Adicionar a quantidade total em cima de cada barra
        for i, media in enumerate(df_total_por_promotor['media_diaria']):
            fig2.data[i].update(text=str(round(media, 2)),  # Converter o valor para uma string
                                textposition='outside',  # Posição do texto (fora da barra)
                                hovertemplate='%{x}<br>Média Diária: %{y:.2f}')  # Template do hover
            
            fig2.update_layout(showlegend=True,yaxis=dict(range=[0, df_total_por_promotor['media_diaria'].max()* 1.2]))

        # Adicionar um checkbox
        show_graph = st.sidebar.checkbox('Média Diária de Vendas de Cada Franquia até o Dia Anterior', value=True)

        col1,col2 = st.columns(2)
        
        with col1:
        # Chamando a função para plotar o gráfico com as franquias selecionadas
            plotar_grafico(franquias_selecionadas)
            
        with col2:
        # Mostrar o gráfico apenas se a caixa de seleção estiver marcada
            if show_graph:
                st.plotly_chart(fig2, use_container_width=True, config={
                                            'displayModeBar': False,  # Para ocultar a barra de ferramentas
                                            'displaylogo': False  })# Para ocultar o logo))





#====================================================================================================================================================================#

        # Definir metas de quantidade para cada promotor por mês
        metas = {'CALDAS NOVAS': 400, 'FORMOSA': 400, 'GOIANIA CENTRO NORTE': 1000, 'MANHUACU': 200, 'SAO JOAO DA BOA VISTA': 400}

        # Converta a coluna 'data' para o tipo datetime
        processed_data['Data Filiação'] = pd.to_datetime(processed_data['Data Filiação'])
        
        
        # Calcular o total de quantidade para cada promotor no mês atual
        df_total_por_promotor = df_current_month.groupby('Franquia')['quantidade'].sum().reset_index()

        # Calcular a quantidade atingida e restante para cada promotor em relação à meta
        df_total_por_promotor['meta'] = df_total_por_promotor['Franquia'].map(metas)
        df_total_por_promotor['atingido'] = df_total_por_promotor['quantidade']
        df_total_por_promotor['falta'] = df_total_por_promotor['meta'] - df_total_por_promotor['quantidade']
        
        
        # Função para criar o gráfico
        def plotar_grafico2(franquias_selecionadas, df_total_por_promotor):
            if not franquias_selecionadas:
                st.write(' ')
            else:
                # Criar uma figura para cada franquia selecionada
                st.markdown('<hr>', unsafe_allow_html=True)
                cols = st.columns(len(franquias_selecionadas))
                for i, franquia in enumerate(franquias_selecionadas):
                    row = df_total_por_promotor[df_total_por_promotor['Franquia'] == franquia].iloc[0]

                    fig = go.Figure()

                    # Adicionar o indicador de atingido
                    fig.add_trace(go.Indicator(
                        mode="gauge+number+delta",
                        value=row['atingido'],  # Definir o valor como a quantidade atingida
                        title={'text': f"{row['Franquia']}"},
                        delta = {'reference': row['meta'], 'increasing': {'color': "RebeccaPurple"}},
                        gauge={'axis': {'range': [None, row['meta']], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "darkblue"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "white",
                            'steps': [
                                {'range': [0, row['meta'] * 0.6], 'color': 'red'},
                                {'range': [row['meta'] * 0.6, row['meta'] * 0.8], 'color': 'yellow'},
                                {'range': [row['meta'] * 0.8, row['meta']], 'color': 'limegreen'}],
                            'threshold': {'line': {'color': "limegreen", 'width': 4}, 'thickness': 0.75,
                                            'value': row['meta']}}))
                    
                    # Arredondar a meta restante para duas casas decimais
                    meta_restante_arredondada = round(row['meta_restante'])

                    # Adicionar um texto indicando a meta restante
                    fig.add_annotation(x=0.5, y=0.25,
                                        text=f"Projeção : {meta_restante_arredondada}",
                                        showarrow=False,
                                        font=dict(size=14))

                    # Atualizar o layout
                    fig.update_layout(
                        margin=dict(l=15, r=30, t=0, b=20)  # Adjust left, right, top, and bottom margins to 10px
                    )

                    # Exibir o gráfico
                    cols[i].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False})

        # Chame a função para calcular a meta restante
        df_total_por_promotor = calcular_meta_restante(df_total_por_promotor,processed_data)

        # Adicionar uma barra de seleção para escolher as franquias (permitindo seleção múltipla)
        franquias_selecionadas2 = st.sidebar.multiselect('Projeção da(s) franquia(s):', df_total_por_promotor['Franquia'].unique(),default=df_total_por_promotor['Franquia'])

        # Chamar a função para plotar os gráficos
        plotar_grafico2(franquias_selecionadas2, df_total_por_promotor)

#====================================================================================================================================================================#

#====================================================================================================================================================================#

        def calcular_meta_restante2(df_meta, df_filtrado, primeiro_dia_mes):
            
            data_atual = pd.to_datetime("today")

            dias_passados = sum(
                1 for i in range((data_atual - primeiro_dia_mes).days + 1)
                if (primeiro_dia_mes + timedelta(days=i)).weekday() != 6
            )

            dias_totais = sum(
                1 for i in range((data_atual.replace(day=1) + pd.offsets.MonthEnd(0)).day)
                if (primeiro_dia_mes + timedelta(days=i)).weekday() != 6
            )

            proporcao_dias = dias_passados / dias_totais if dias_totais > 0 else 1
            df_meta['meta_restante'] = df_meta['atingido']  # A projeção é igual ao valor atingido
            return df_meta
        # Obter o primeiro dia do mês atual
        hoje = pd.to_datetime("today")
        primeiro_dia_mes_atual = hoje.replace(day=1)

        # Obter o primeiro e último dia do mês passado
        primeiro_dia_mes_passado = (primeiro_dia_mes_atual - pd.DateOffset(months=1)).replace(day=1)
        ultimo_dia_mes_passado = primeiro_dia_mes_atual - pd.DateOffset(days=1)

        # Filtrar os dados do mês passado
        df_last_month = processed_data[
            (processed_data['Data Filiação'] >= primeiro_dia_mes_passado) &
            (processed_data['Data Filiação'] <= ultimo_dia_mes_passado)
        ]
        
        

        df_total_por_promotor_passado = df_last_month.groupby('Franquia')['quantidade'].sum().reset_index()
        df_total_por_promotor_passado['meta'] = df_total_por_promotor_passado['Franquia'].map(metas)
        df_total_por_promotor_passado['atingido'] = df_total_por_promotor_passado['quantidade']
        df_total_por_promotor_passado['falta'] = df_total_por_promotor_passado['meta'] - df_total_por_promotor_passado['quantidade']

        # Calcular a projeção/meta restante
        df_total_por_promotor_passado = calcular_meta_restante2(df_total_por_promotor_passado, df_last_month, primeiro_dia_mes_passado)
        df_total_por_promotor = calcular_meta_restante2(df_total_por_promotor, processed_data, primeiro_dia_mes_atual)
        # Adicionar seleção de mês
        mes_opcao = st.sidebar.radio("Escolha o mês:", ["Mês Atual", "Mês Passado"])

        if mes_opcao == "Mês Atual":
            franquias_selecionadas = st.sidebar.multiselect(
            f'Projeção da(s) franquia(s): ({mes_opcao})',
            df_total_por_promotor['Franquia'].unique(),
            default=df_total_por_promotor['Franquia'],
            key=f"multiselect_{mes_opcao.replace(' ', '_')}"
        )
            plotar_grafico2(franquias_selecionadas, df_total_por_promotor)
        else:
            franquias_selecionadas_passado = st.sidebar.multiselect('Projeção da(s) franquia(s) - Mês Passado:', df_total_por_promotor_passado['Franquia'].unique(), default=df_total_por_promotor_passado['Franquia'])
            plotar_grafico2(franquias_selecionadas_passado, df_total_por_promotor_passado)       

        # Adicionando um seletor na sidebar para escolher a franquia
        franquias = processed_data['Franquia'].unique()
        franquia_selecionada3 = st.sidebar.selectbox('Top 5 Promotores/Franquia', franquias)

        # Filtrando os dados para a franquia selecionada
        dados_filtrados = processed_data[processed_data['Franquia'] == franquia_selecionada3]

        # Agrupando os dados filtrados por Promotor e somando as quantidades
        total_vendas_por_promotor = dados_filtrados.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()

        # Ordenando os promotores pelo total de vendas e pegando os top 5
        top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)


        # Criando um gráfico de barras para visualizar os top 5 vendedores da franquia selecionada
        fig1 = px.bar(top_5_vendedores, x='Promotor de Vendas', y='quantidade',
                    title=f'Top 5 Promotores de Venda - Franquia {franquia_selecionada3}',
                    labels={'Promotor de Vendas': 'Promotor', 'quantidade': 'Total de Vendas'},
                    color='Promotor de Vendas',
                    text='quantidade',
                    color_discrete_sequence=cores)

        fig1.update_layout(showlegend=False)
        fig1.update_traces(texttemplate='%{text}', textposition='outside')

        max_quantidade = top_5_vendedores['quantidade'].max()
        fig1.update_layout(yaxis=dict(range=[0, max_quantidade * 1.2]))


#====================================================================================================================================================================#    

        # Criando uma nova coluna 'Trimestre' e 'Ano' para facilitar a seleção
        processed_data['Ano'] = processed_data['Data Filiação'].dt.year
        processed_data['Trimestre'] = processed_data['Data Filiação'].dt.month.apply(lambda x: (x-1)//3 + 1)

        # Obtendo os trimestres únicos disponíveis
        trimestres_unicos = processed_data[['Ano', 'Trimestre']].drop_duplicates()
        trimestres_unicos['Ano_Trimestre'] = trimestres_unicos.apply(lambda x: f"{x['Ano']} Q{x['Trimestre']}", axis=1)
        trimestres_unicos = trimestres_unicos.sort_values(by=['Ano', 'Trimestre'], ascending=[False, False])
        lista_trimestres = trimestres_unicos['Ano_Trimestre'].tolist()

        # Seletor para escolher o trimestre na sidebar
        trimestre_escolhido = st.sidebar.selectbox('Escolha o Trimestre', lista_trimestres)
        ano_escolhido, q_escolhido = trimestre_escolhido.split(' Q')
        q_escolhido = int(q_escolhido)

        # Filtrando o DataFrame pelo trimestre escolhido
        dados_trimestre_escolhido = processed_data[(processed_data['Ano'] == int(ano_escolhido)) & (processed_data['Trimestre'] == q_escolhido)]

        # Continuação do processo de filtragem por franquia com a sidebar, como antes
        franquias = dados_trimestre_escolhido['Franquia'].unique()
        

        # Filtrando por franquia selecionada
        dados_filtrados = dados_trimestre_escolhido[dados_trimestre_escolhido['Franquia'] == franquia_selecionada3]

        # Agrupando por Promotor e somando as quantidades
        total_vendas_por_promotor = dados_filtrados.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()

        # Ordenando e pegando os top 5 promotores
        top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)


        fig2 = px.bar(top_5_vendedores, x='Promotor de Vendas', y='quantidade',
                    title=f'Top 5 Promotores de Venda - Franquia {franquia_selecionada3}, {trimestre_escolhido}',
                    labels={'Promotor de Vendas': 'Promotor', 'quantidade': 'Total de Vendas'},
                    color='Promotor de Vendas',
                    text='quantidade',
                    color_discrete_sequence=cores)

        fig2.update_layout(showlegend=False)
        fig2.update_traces(texttemplate='%{text}', textposition='outside')

        max_quantidade = top_5_vendedores['quantidade'].max()
        fig2.update_layout(yaxis=dict(range=[0, max_quantidade * 1.2]))
       

        max_quantidade = top_5_vendedores['quantidade']

        col3,col4 = st.columns(2)
        with col3:
            st.plotly_chart(fig1,use_container_width=True,)
        with col4:
            st.plotly_chart(fig2,use_container_width=True,)
        

        # Checkbox para selecionar a data
        show_date_input = st.sidebar.checkbox('Selecionar Data')









#====================================================================================================================================================================#
# Resultados dos colaboradore do mês anterior
        
        # Criando uma nova coluna 'Ano' e 'Mês' para facilitar a seleção
        processed_data['Ano'] = processed_data['Data Filiação'].dt.year
        processed_data['Mês'] = processed_data['Data Filiação'].dt.month

        # Obtendo o ano e mês atual
        
        mes_atual = current_date.month
        ano_atual = current_date.year

        # Calculando o mês e ano do mês passado
        if mes_atual == 1:
            mes_passado = 12
            ano_passado = ano_atual - 1
        else:
            mes_passado = mes_atual - 1
            ano_passado = ano_atual

        # Filtrando o DataFrame pelo mês passado
        dados_mes_passado = processed_data[(processed_data['Ano'] == ano_passado) & (processed_data['Mês'] == mes_passado)]

        # Filtrando os dados por franquia
        franquias = sorted(dados_mes_passado['Franquia'].unique())

        # Verificando o número de franquias para ajustar o número de colunas
        cols = min(5, len(franquias))

        # Criando uma figura com subplots em uma única linha
        fig = make_subplots(
            rows=1, 
            cols=cols, 
            subplot_titles=[f'Franquia {franquia}' for franquia in franquias[:cols]],
            horizontal_spacing=0.05  # Espaçamento horizontal entre os gráficos
        )

        # Adicionando cada gráfico no subplot correspondente
        for i, franquia in enumerate(franquias[:cols]):
            dados_franquia = dados_mes_passado[dados_mes_passado['Franquia'] == franquia]
            
            # Agrupando por Promotor e somando as quantidades
            total_vendas_por_promotor = dados_franquia.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()

            # Ordenando e pegando os top 5 promotores
            top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)
            
            # Criando o gráfico de barras
            barra = go.Bar(
                x=top_5_vendedores['Promotor de Vendas'],
                y=top_5_vendedores['quantidade'],
                text=top_5_vendedores['quantidade'],
                textposition='outside',
                marker_color=cores[i % len(cores)]  # Pode ajustar as cores conforme necessário
            )
            
            # Adicionando o gráfico ao subplot
            fig.add_trace(barra, row=1, col=i+1)

            # Ajustando o layout do subplot
            fig.update_xaxes(title_text='Promotor', row=1, col=i+1)
            fig.update_yaxes(title_text='Total de Vendas', row=1, col=i+1)
            
            # Ajustando o layout do subplot para garantir que o texto não seja cortado
            max_y = top_5_vendedores['quantidade'].max()
            fig.update_yaxes(range=[0, max_y * 1.3], row=1, col=i+1)

        # Atualizando o layout geral da figura
        fig.update_layout(
            title_text=f'Top 5 Promotores de Venda - Mês {mes_passado}/{ano_passado}',
            title={
                'x': 0.45,  # Centers the title horizontally
                'y': 1.0,  # Adjusts the vertical position if necessary
                'xanchor': 'center',  # Ensures the center of the title is at `x`
                'yanchor': 'top'  # Anchors the title at the top if `y` is adjusted
            },
            title_font=dict(  # This specifies the font settings for the title
                size=24,  # Sets the font size
                family='Arial, sans-serif',  # Optionally, sets the font type
                color='black'  # Optionally, sets the font color
            ),
            showlegend=False,
            height=500,  # Altura total da figura
            width=400 * cols,  # Largura total da figura para acomodar os 4 gráficos lado a lado
        )

        # Exibindo a figura com Streamlit
        st.plotly_chart(fig)
#====================================================================================================================================================================#

        

        if show_date_input:

            st.markdown('<hr>', unsafe_allow_html=True)
            
            # Sidebar para selecionar a data
            selected_date = st.sidebar.date_input('Selecione uma data', min_value=df_projec['Data Filiação'].min(), max_value=df_projec['Data Filiação'].max(), value=df_projec['Data Filiação'].max())

            # Filtrar os dados para a data selecionada
            dados_selecionados = df_projec[df_projec['Data Filiação'].dt.date == selected_date]

            # Calcular a quantidade de cada franquia na data selecionada
            quantidade_por_franquia = dados_selecionados.groupby('Franquia')['quantidade'].sum().reset_index()

            # Função para plotar o gráfico
            def plot_graph(data, title):
                fig4 = px.bar(data, x='Franquia', y='quantidade', 
                            title=title,
                            labels={'quantidade': 'Quantidade', 'Franquia': 'Franquia'},
                            color='Franquia',
                            color_discrete_sequence=cores)
                
                # Adicionar a quantidade no topo de cada barra
                fig4.update_traces(texttemplate='%{y}', textposition='outside')
                fig4.update_layout(xaxis_title='Franquia', yaxis_title='Quantidade', showlegend=False)
                
                # Ajustar o limite do eixo y
                fig4.update_layout(yaxis=dict(range=[0, data['quantidade'].max() * 1.1]))  # Aumenta 10% além do valor máximo
                return st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False, 'displaylogo': False})

            plot_graph(quantidade_por_franquia, f'Vendas por Franquia em {selected_date.strftime("%d/%m/%Y")}')


        st.markdown('<hr>', unsafe_allow_html=True)



#====================================================================================================================================================================#

        st.markdown('<hr>', unsafe_allow_html=True)
                # Adicionar as barras de cada franquia ao subplot correspondente

        # Criando uma nova coluna 'Ano' e 'Mês' para facilitar a seleção
        processed_data['Ano'] = processed_data['Data Filiação'].dt.year
        processed_data['Mês'] = processed_data['Data Filiação'].dt.month

        # Obtendo o ano e mês atual
        ano_atual = datetime.datetime.now().year
        mes_atual = datetime.datetime.now().month

        # Filtrando o DataFrame pelo mês atual
        dados_mes_atual = processed_data[(processed_data['Ano'] == ano_atual) & (processed_data['Mês'] == mes_atual)]

        # Filtrando os dados por franquia
        franquias = sorted(dados_mes_atual['Franquia'].unique())

        # Criando uma figura com 4 subplots em uma única linha
        fig = make_subplots(
            rows=1, 
            cols=5, 
            subplot_titles=[f'Franquia {franquia}' for franquia in franquias],
            horizontal_spacing=0.05  # Espaçamento horizontal entre os gráficos
        )

        # Variáveis para posição dos subplots
        positions = [(1, 1), (1, 2), (1, 3), (1, 4),(1, 5)]



        # Adicionando cada gráfico no subplot correspondente
        for i, franquia in enumerate(franquias):
            dados_franquia = dados_mes_atual[dados_mes_atual['Franquia'] == franquia]
            
            # Agrupando por Promotor e somando as quantidades
            total_vendas_por_promotor = dados_franquia.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()

            # Ordenando e pegando os top 5 promotores
            top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)
            
            # Criando o gráfico de barras
            barra = go.Bar(
                x=top_5_vendedores['Promotor de Vendas'],
                y=top_5_vendedores['quantidade'],
                text=top_5_vendedores['quantidade'],
                textposition='outside',
                marker_color=cores[i % len(cores)]
            )
            
            # Adicionando o gráfico ao subplot
            row, col = positions[i]
            fig.add_trace(barra, row=row, col=col)

            # Ajustando o layout do subplot
            fig.update_xaxes(title_text='Promotor', row=row, col=col)
            fig.update_yaxes(title_text='Total de Vendas', row=row, col=col)
                # Ajustando o layout do subplot para garantir que o texto não seja cortado
            max_y = top_5_vendedores['quantidade'].max()
            fig.update_yaxes(range=[0, max_y * 1.3], row=row, col=col)

        # Atualizando o layout geral da figura
        fig.update_layout(
            title_text=f'Top 5 Promotores de Venda - Mês {mes_atual}/{ano_atual}',
            title={
                                'x': 0.45,  # Centers the title horizontally
                                'y': 1.0,  # Adjusts the vertical position if necessary
                                'xanchor': 'center',  # Ensures the center of the title is at `x`
                                'yanchor': 'top'  # Anchors the title at the top if `y` is adjusted
                            },
                            title_font=dict(  # This specifies the font settings for the title
                                size=24,  # Sets the font size
                                family='Arial, sans-serif',  # Optionally, sets the font type
                                color='black'  # Optionally, sets the font color
                            ), 
            showlegend=False,
            height=500,  # Altura total da figura
            width=400 * cols,  # Largura total da figura para acomodar os 4 gráficos lado a lado
            
            
        )

        # Exibindo a figura com Streamlit
        st.plotly_chart(fig)



        data_atual = datetime.date.today() - timedelta(days=1)

        # Calcular o total de dias úteis até a data atual excluindo os domingos
        dias_totais = pd.date_range(start='2024-01-01', end=data_atual)
        # Filtrar para remover os domingos
        dias_uteis = dias_totais[~dias_totais.weekday.isin([6])]
        
        # Somar as quantidades para cada franquia
        total_vendas = dados_agrupados.groupby('Franquia')['quantidade'].sum()
        
        # Calcular a média diária excluindo apenas os domingos
        media_diaria = total_vendas / len(dias_uteis)
        
        # Converter para DataFrame
        media_diaria = media_diaria.reset_index(name='Média Diária')
        
        # Criar o gráfico de barras com as médias diárias
        fig6 = px.bar(media_diaria, x='Franquia', y='Média Diária', 
                      text='Média Diária', 
                      title='Média Diária de Vendas por Franquia em 2024 (Até Ontém, excluindo domingos)',
                      color = 'Franquia',
                      color_discrete_sequence=cores)

        # Atualizar layout para exibir os valores em cima das barras
        fig6.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig6.update_layout(yaxis=dict(range=[0, media_diaria['Média Diária'].max() * 1.1]))

        st.plotly_chart(fig6)





        processed_data['Data Filiação'] = pd.to_datetime(processed_data['Data Filiação'])

        # Filtrar os dados para a unidade de Caldas Novas
        dados_caldas_novas = processed_data[processed_data['Franquia'] == 'CALDAS NOVAS']

        # Filtrar os dados dos últimos 3 meses
        data_limite = pd.Timestamp.today() - pd.DateOffset(months=3)
        dados_caldas_novas_ultimos_3_meses = dados_caldas_novas[dados_caldas_novas['Data Filiação'] >= data_limite]

        # Criando a figura com subplots para cada um dos 3 meses
        fig = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=[
                'Junho',
                'Maio',
                'Abril'
            ],
            horizontal_spacing=0.08  # Espaçamento horizontal entre os gráficos
        )

        # Função para filtrar dados por mês e gerar gráfico de barras
        def add_mes_subplot(mes_offset, col):
            # Calcula o mês de interesse
            mes_inicio = pd.Timestamp.today().replace(day=1) - pd.DateOffset(months=mes_offset)
            mes_fim = mes_inicio + pd.DateOffset(months=1)
            
            # Filtra os dados para o mês de interesse
            dados_mes = dados_caldas_novas_ultimos_3_meses[
                (dados_caldas_novas_ultimos_3_meses['Data Filiação'] >= mes_inicio) &
                (dados_caldas_novas_ultimos_3_meses['Data Filiação'] < mes_fim)
            ]
            
            # Agrupando por Promotor e somando as quantidades
            total_vendas_por_promotor = dados_mes.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()
            
            # Ordenando e pegando os top 5 promotores
            top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)
            
            # Criando o gráfico de barras
            barra = go.Bar(
                x=top_5_vendedores['Promotor de Vendas'],
                y=top_5_vendedores['quantidade'],
                text=top_5_vendedores['quantidade'],
                textposition='outside',
                marker_color=cores  # Pode alterar a cor conforme preferir
            )
            
            # Adicionando o gráfico ao subplot
            fig.add_trace(barra, row=1, col=col)
            
            # Ajustando o layout do subplot
            fig.update_xaxes(title_text='Promotor', row=1, col=col)
            fig.update_yaxes(title_text='Total de Vendas', row=1, col=col)
            if not top_5_vendedores['quantidade'].empty:
                max_y = top_5_vendedores['quantidade'].max()
                fig.update_yaxes(range=[0, max_y * 1.3], row=1, col=col)

        # Adicionando subplots para cada um dos 3 meses
        add_mes_subplot(0, 1)  # Mês atual
        add_mes_subplot(1, 2)  # 1 mês atrás
        add_mes_subplot(2, 3)  # 2 meses atrás

        # Atualizando o layout geral da figura
        fig.update_layout(
            title_text='Top 5 Promotores de Venda da Unidade Caldas Novas dos Últimos 3 Meses',
            title={
                'x': 0.5,  # Centraliza o título horizontalmente
                'y': 0.9,  # Ajusta a posição vertical se necessário
                'xanchor': 'center',  # Garante que o centro do título esteja em `x`
                'yanchor': 'top'  # Ancora o título no topo se `y` for ajustado
            },
            title_font=dict(
                size=24,
                family='Arial, sans-serif',
                color='black'
            ),
            showlegend=False,
            height=500,
            width=1200  # Ajusta a largura conforme necessário
        )

        # Exibindo a figura com Streamlit (substitua st.plotly_chart(fig) pela função apropriada no seu ambiente)
        st.plotly_chart(fig)




        # Suponha que 'processed_data' é o seu DataFrame e 'Data Filiação' a coluna com as datas de Filiação
        # Converter a coluna de data para datetime, se ainda não estiver
        processed_data['Data Filiação'] = pd.to_datetime(processed_data['Data Filiação'])

        # Remover o filtro de mês e ano atual para considerar todas as datas
        # Filtrando os dados por franquia
        franquias = sorted(processed_data['Franquia'].unique())

        # Criando uma figura com subplots para cada franquia
        fig = make_subplots(
            rows=1, 
            cols=len(franquias), 
            subplot_titles=[f' {franquia}' for franquia in franquias],
            horizontal_spacing=0.05  # Espaçamento horizontal entre os gráficos
        )


        # Adicionando cada gráfico no subplot correspondente
        for i, franquia in enumerate(franquias):
            dados_franquia = processed_data[processed_data['Franquia'] == franquia]
            
            # Agrupando por Promotor e somando as quantidades
            total_vendas_por_promotor = dados_franquia.groupby('Promotor de Vendas')['quantidade'].sum().reset_index()

            # Ordenando e pegando os top 5 promotores
            top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)
            
            # Criando o gráfico de barras
            barra = go.Bar(
                x=top_5_vendedores['Promotor de Vendas'],
                y=top_5_vendedores['quantidade'],
                text=top_5_vendedores['quantidade'],
                textposition='outside',
                marker_color=cores[i % len(cores)]
            )
            
            # Adicionando o gráfico ao subplot
            fig.add_trace(barra, row=1, col=i+1)

            # Ajustando o layout do subplot
            fig.update_xaxes(title_text='Promotor', row=1, col=i+1)
            fig.update_yaxes(title_text='Total de Vendas', row=1, col=i+1)
            # Ajustando o layout do subplot para garantir que o texto não seja cortado
            max_y = top_5_vendedores['quantidade'].max()
            fig.update_yaxes(range=[0, max_y * 1.3], row=1, col=i+1)

        # Atualizando o layout geral da figura
        fig.update_layout(
            title_text='Top 5 Promotores de Venda de Todos os Tempos',
            title={
                'x': 0.45,  # Centraliza o título horizontalmente
                'y': 1.0,  # Ajusta a posição vertical se necessário
                'xanchor': 'center',  # Garante que o centro do título esteja em `x`
                'yanchor': 'top'  # Ancora o título no topo se `y` for ajustado
            },
            title_font=dict(  # Especifica as configurações de fonte para o título
                size=24,  # Define o tamanho da fonte
                family='Arial, sans-serif',  # Opcionalmente, define o tipo de fonte
                color='black'  # Opcionalmente, define a cor da fonte
            ), 
            showlegend=False,
            height=500,  # Altura total da figura
            width=400 * len(franquias),  # Largura total da figura para acomodar os gráficos lado a lado
        )

        # Exibindo a figura com Streamlit (substitua st.plotly_chart(fig) pela função apropriada no seu ambiente)
        st.plotly_chart(fig)



#====================================================================================================================================================================#


        df_motivo = pd.read_excel("data (1).xlsx", header=0)

        # Suponha que 'df_motivo' é o seu DataFrame e 'Data última desfiliação' a coluna com as datas de desFiliação
        # Converter a coluna de data para datetime, se ainda não estiver
        df_motivo['Data última desfiliação'] = pd.to_datetime(df_motivo['Data última desfiliação'])

        # Obter o mês e ano atual
        current_month = current_date.month
        current_year = current_date.year

        # Filtrar o DataFrame para o mês e ano atual
        df_motivo_current = df_motivo[(df_motivo['Data última desfiliação'].dt.month == current_month) & 
                                    (df_motivo['Data última desfiliação'].dt.year == current_year)]

        # Prosseguir com a análise agrupada, como antes
        top_motivos = df_motivo_current.groupby(['Franquia', 'Motivo última desfiliação']).size().reset_index(name='Contagem')
        top_motivos = top_motivos.sort_values(['Franquia', 'Contagem'], ascending=[True, False]).groupby('Franquia').head(5)

        # Configurar subplots para cada franquia
        franquias = top_motivos['Franquia'].unique()
        cols = len(franquias)
        fig = make_subplots(rows=1, cols=cols, subplot_titles=franquias, horizontal_spacing=0.05)

        # Calcular o máximo para cada franquia
        max_counts = top_motivos.groupby('Franquia')['Contagem'].max() * 1.2  # Aumentar o máximo em 20%

        # Adicionar as barras de cada franquia ao subplot correspondente
        for i, franquia in enumerate(franquias):
            subdata = top_motivos[top_motivos['Franquia'] == franquia]
            fig.add_trace(go.Bar(x=subdata['Motivo última desfiliação'], y=subdata['Contagem'], orientation='v',
                                marker=dict(color=cores[i % len(cores)]),
                                text=subdata['Contagem'], textposition='outside'),
                        row=1, col=i+1)

            # Ajustar o eixo Y para cada subplot baseado no máximo da franquia
            fig.update_yaxes(title_text='Número de Desfiliações', range=[0, max_counts[franquia]], row=1, col=i+1)

        # Ajustar layout e escalas
        fig.update_layout(
            title_text="Top 5 Motivos de DesFiliação por Franquia",
                          title={
                                'x': 0.45,  # Centers the title horizontally
                                'y': 1.0,  # Adjusts the vertical position if necessary
                                'xanchor': 'center',  # Ensures the center of the title is at `x`
                                'yanchor': 'top'  # Anchors the title at the top if `y` is adjusted
                            },
                            title_font=dict(  # This specifies the font settings for the title
                                size=24,  # Sets the font size
                                family='Arial, sans-serif',  # Optionally, sets the font type
                                color='black'  # Optionally, sets the font color
                            ),
            showlegend=False,
            height=500,  # Aumentada a altura do gráfico
            width=400 * cols,  # Ajustar largura baseado no número de franquias para melhor visualização
            margin=dict(l=50, r=100, t=50, b=150),  # Ajustar as margens do gráfico
            font=dict(size=10)
        )

        st.plotly_chart(fig)


         # Prosseguir com a análise agrupada, como antes
        top_motivos = df_motivo.groupby(['Franquia', 'Motivo última desfiliação']).size().reset_index(name='Contagem')
        top_motivos = top_motivos.sort_values(['Franquia', 'Contagem'], ascending=[True, False]).groupby('Franquia').head(5)

        # Configurar subplots para cada franquia
        franquias = top_motivos['Franquia'].unique()
        cols = len(franquias)
        fig = make_subplots(rows=1, cols=cols, subplot_titles=franquias, horizontal_spacing=0.05)

        # Calcular o máximo para cada franquia
        max_counts = top_motivos.groupby('Franquia')['Contagem'].max() * 1.2  # Aumentar o máximo em 20%



        # Adicionar as barras de cada franquia ao subplot correspondente
        for i, franquia in enumerate(franquias):
            subdata = top_motivos[top_motivos['Franquia'] == franquia]
            fig.add_trace(go.Bar(x=subdata['Motivo última desfiliação'], y=subdata['Contagem'], orientation='v',
                                marker=dict(color=cores[i % len(cores)]),
                                text=subdata['Contagem'], textposition='outside'),
                        row=1, col=i+1)

            # Ajustar o eixo Y para cada subplot baseado no máximo da franquia
            fig.update_yaxes(title_text='Número de Desfiliações', range=[0, max_counts[franquia]], row=1, col=i+1)

        # Ajustar layout e escalas
        fig.update_layout(
            title_text="Top 5 Motivos de DesFiliação por Franquia",
            title={
                'x': 0.45,  # Centraliza o título horizontalmente
                'y': 1.0,  # Ajusta a posição vertical se necessário
                'xanchor': 'center',  # Garante que o centro do título esteja em `x`
                'yanchor': 'top'  # Ancora o título no topo se `y` for ajustado
            },
            title_font=dict(  # Especifica as configurações de fonte para o título
                size=24,  # Define o tamanho da fonte
                family='Arial, sans-serif',  # Opcionalmente, define o tipo de fonte
                color='black'  # Opcionalmente, define a cor da fonte
            ),
            showlegend=False,
            height=500,  # Aumenta a altura do gráfico
            width=400 * cols,  # Ajusta a largura com base no número de franquias para melhor visualização
            margin=dict(l=50, r=100, t=50, b=150),  # Ajusta as margens do gráfico
            font=dict(size=10)
        )

        # Exibir o gráfico com o Streamlit (substitua st.plotly_chart(fig) pela função apropriada no seu ambiente)
        st.plotly_chart(fig)


#====================================================================================================================================================================#


        st.markdown('<hr>', unsafe_allow_html=True)

        df_prev = pd.read_excel('data (2).xlsx')
        
        desafiliacao = df_prev.groupby('FRANQUIA')['QTD MENS CONSECUTIVA'].sum()

        # Converter a série em DataFrame para melhor manipulação com Plotly
        desafiliacao_df = desafiliacao.reset_index()

        # Garantir que temos cores suficientes para cada franquia, repetir a lista se necessário
        if len(cores) < len(desafiliacao_df):
            cores = (cores * (len(desafiliacao_df) // len(cores) + 1))[:len(desafiliacao_df)]

        # Criar um gráfico de barras com cores específicas para cada franquia
        fig = go.Figure()
        for i, row in desafiliacao_df.iterrows():
            fig.add_trace(go.Bar(
                x=[row['FRANQUIA']],
                y=[row['QTD MENS CONSECUTIVA']],
                name=row['FRANQUIA'],
                marker_color=cores[i],
                text=[row['QTD MENS CONSECUTIVA']],
                textposition='auto'
            ))

        # Adicionar textos nas barras para mostrar os valores
        fig.update_traces(texttemplate='%{text}', textposition='outside')

        # Ajustar o limite do eixo Y
        fig.update_layout(title_text="Previsão de desFiliação",
                          title={
                                'x': 0.5,  # Centers the title horizontally
                                'y': 0.9,  # Adjusts the vertical position if necessary
                                'xanchor': 'center',  # Ensures the center of the title is at `x`
                                'yanchor': 'top'  # Anchors the title at the top if `y` is adjusted
                            },
                            title_font=dict(  # This specifies the font settings for the title
                                size=24,  # Sets the font size
                                family='Arial, sans-serif',  # Optionally, sets the font type
                                color='black'  # Optionally, sets the font color
                            ),yaxis=dict(range=[0, desafiliacao.max() * 1.2]))

        # Tentativa de adicionar uma legenda, mesmo não sendo típico para este tipo de gráfico
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                marker=dict(size=10, color="Red"),
                                legendgroup='group', showlegend=True, name='Régua 6'))

        # Configurações finais do layout
        fig.update_layout(showlegend=False,
                        height=600,
                        width=700,
                        annotations=[
                dict(
                    text="Régua 6",  # Texto da anotação
                    xref="paper", yref="paper",  # Usar referências de posição relativa ao gráfico
                    x=0.10, y=0.95,  # Posição da anotação no gráfico
                    showarrow=True,  # Não mostrar seta
                    arrowhead=1,  # Tipo de cabeça da seta (1 é padrão)
                    arrowsize=1,  # Tamanho da seta
                    arrowwidth=2,  # Largura da seta
                    arrowcolor="black",  # Cor da seta
                    font=dict(size=16, color="black"),  # Configurações de fonte
                    bgcolor="white",  # Cor de fundo da anotação
                    bordercolor="black",  # Cor da borda da anotação
                    borderpad=4  # Espaçamento da borda
                )
            ]
        )

        # Mostrar o gráfico
        st.plotly_chart(fig)





if __name__ == "__main__":
    main()
#====================================================================================================================================================================#
