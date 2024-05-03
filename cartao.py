import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import plotly.express as px
from datetime import timedelta
import os

st.set_page_config(
    layout="wide"
)

# Função para pré-processamento
def preprocess_data(data):
    # Corrigir o tipo de dado para datetime
    data['Data filiação'] = pd.to_datetime(data['Data filiação'], errors='coerce')
    # Remover linhas com datas inválidas
    data = data.dropna(subset=['Data filiação'])
    # Converter datas para string no formato 'YYYY-MM-DD'
    data['Data filiação'] = data['Data filiação'].dt.strftime('%Y-%m-%d')
    # Adicionar coluna de quantidade com valor 1
    data['quantidade'] = 1
    # Agrupar por data de filiação e franquia e calcular a contagem
    data = data.groupby(['Data filiação','Franquia','Promotor Venda Prospecção']).size().reset_index(name='quantidade')
    
    return data

def main():
    st.markdown("<h1 style='text-align: center;'>CDT</h1>", unsafe_allow_html=True)

    # Lista todos os arquivos Excel na pasta
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

    if len(excel_files) == 0:
        st.error('Nenhum arquivo Excel encontrado na pasta.')
    else:
        # Seleciona o arquivo Excel mais recente
        selected_file = max(excel_files, key=os.path.getmtime)
        

    if selected_file is not None:
        # Ler o arquivo Excel
        df = pd.read_excel(selected_file, header=0)
        
        # Pré-processamento dos dados
        processed_data = preprocess_data(df)
        
        
        # Adicionando o código de projeção
        processed_data['Data filiação'] = pd.to_datetime(processed_data['Data filiação'])
        processed_data['mes'] = processed_data['Data filiação'].dt.month

        df_projec = processed_data.copy()
        
        # Convertendo a coluna 'Data filiação' para o tipo datetime
        df_projec['Data filiação'] = pd.to_datetime(df_projec['Data filiação'])

        # Extraindo o mês da coluna 'Data filiação' e criando uma nova coluna 'Mês'
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
        df_projec['Mês'] = df_projec['Data filiação'].dt.month.map(meses_pt_br)

        # Agrupando os dados por franquia e mês e somando a quantidade para cada grupo
        dados_agrupados = df_projec.groupby(['Franquia', 'Mês'])['quantidade'].sum().reset_index()
        
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
                        hoverinfo='x+y',  # Mostrar valor de x, y e o texto personalizado
                        text=dados_franquia['quantidade'],  # Adicionar o valor da quantidade como texto
                        textposition='outside',
                        marker=dict(color=next(cor_iter))# Posição do texto fora da barra
                    )
                    traces.append(trace)

                # Criando o layout do gráfico
                layout = go.Layout(
                    title='Vendas de cada franquias por mês',
                    xaxis=dict(title='Mês'),
                    yaxis=dict(title='Quantidade'),
                            
                )

                # Criando a figura
                fig = go.Figure(data=traces, layout=layout)
                fig.update_layout(showlegend=True,yaxis=dict(range=[0, dados_agrupados['quantidade'].max() * 1.15]))

                # Exibindo o gráfico
                st.plotly_chart(fig, use_container_width=True, config={
                    'displayModeBar': False,  # Para ocultar a barra de ferramentas
                    'displaylogo': False  # Para ocultar o logo
                })

        # Lista de franquias disponíveis
        franquias_disponiveis = dados_agrupados['Franquia'].unique()

        # Checkbox para selecionar as franquias
        franquias_selecionadas = st.sidebar.multiselect('Vendas de cada franquias por mês', franquias_disponiveis, default=franquias_disponiveis)

#====================================================================================================================================================================#
        
        current_date = datetime.datetime.now()

        # Tenta filtrar os dados para o mês atual
        df_current_month = processed_data[processed_data['Data filiação'].dt.month == current_date.month]

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
            df_current_month = processed_data[(processed_data['Data filiação'].dt.month == previous_month) &
                                            (processed_data['Data filiação'].dt.year == year)]


        # Calcular o total de quantidade para cada promotor
        df_total_por_promotor = df_current_month.groupby('Franquia')['quantidade'].sum().reset_index()


        def calcular_meta_restante(df_total_por_promotor, processed_data):
            # Obtém a data atual
            data_atual = datetime.date.today() - timedelta(days=1)
            
            # Verifica se existem dados para o mês atual no dataframe 'processed_data'
            if not processed_data[processed_data['Data filiação'].dt.month == data_atual.month].empty:
                # Usa dados do mês atual
                primeiro_dia_mes_atual = data_atual.replace(day=1)
            else:
                # Se não houver dados para o mês atual, ajusta para o mês anterior
                if data_atual.month == 1:
                    data_atual = data_atual.replace(year=data_atual.year - 1, month=12, day=31)
                else:
                    data_atual = data_atual.replace(month=data_atual.month - 1, day=1) + timedelta(days=-1)
                primeiro_dia_mes_atual = data_atual.replace(day=1)
            
            # Obtém o último dia do mês atual
            ultimo_dia_mes_atual = data_atual.replace(day=1, month=data_atual.month % 12 + 1) - timedelta(days=1)
            
            # Calcula quantos dias faltam para o fim do mês
            dias_restantes = (ultimo_dia_mes_atual - data_atual).days + 1
            
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
        metas = {'CALDAS NOVAS': 400, 'FORMOSA': 400, 'GOIANIA CENTRO NORTE': 1000, 'SAO JOAO DA BOA VISTA': 400}

        # Converta a coluna 'data' para o tipo datetime
        processed_data['Data filiação'] = pd.to_datetime(processed_data['Data filiação'])
        
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
                    fig.add_annotation(x=0.5, y=0.3,
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

       

        # Adicionando um seletor na sidebar para escolher a franquia
        franquias = processed_data['Franquia'].unique()
        franquia_selecionada3 = st.sidebar.selectbox('Top 5 Promotores/Franquia', franquias)

        # Filtrando os dados para a franquia selecionada
        dados_filtrados = processed_data[processed_data['Franquia'] == franquia_selecionada3]

        # Agrupando os dados filtrados por Promotor e somando as quantidades
        total_vendas_por_promotor = dados_filtrados.groupby('Promotor Venda Prospecção')['quantidade'].sum().reset_index()

        # Ordenando os promotores pelo total de vendas e pegando os top 5
        top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)


        # Criando um gráfico de barras para visualizar os top 5 vendedores da franquia selecionada
        fig1 = px.bar(top_5_vendedores, x='Promotor Venda Prospecção', y='quantidade',
                    title=f'Top 5 Promotores de Venda - Franquia {franquia_selecionada3}',
                    labels={'Promotor Venda Prospecção': 'Promotor', 'quantidade': 'Total de Vendas'},
                    color='Promotor Venda Prospecção',
                    text='quantidade',
                    color_discrete_sequence=cores)

        fig1.update_layout(showlegend=False)
        fig1.update_traces(texttemplate='%{text}', textposition='outside')

        max_quantidade = top_5_vendedores['quantidade'].max()
        fig1.update_layout(yaxis=dict(range=[0, max_quantidade * 1.2]))


#====================================================================================================================================================================#    

        # Criando uma nova coluna 'Trimestre' e 'Ano' para facilitar a seleção
        processed_data['Ano'] = processed_data['Data filiação'].dt.year
        processed_data['Trimestre'] = processed_data['Data filiação'].dt.month.apply(lambda x: (x-1)//3 + 1)

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
        total_vendas_por_promotor = dados_filtrados.groupby('Promotor Venda Prospecção')['quantidade'].sum().reset_index()

        # Ordenando e pegando os top 5 promotores
        top_5_vendedores = total_vendas_por_promotor.sort_values(by='quantidade', ascending=False).head(5)


        fig2 = px.bar(top_5_vendedores, x='Promotor Venda Prospecção', y='quantidade',
                    title=f'Top 5 Promotores de Venda - Franquia {franquia_selecionada3}, {trimestre_escolhido}',
                    labels={'Promotor Venda Prospecção': 'Promotor', 'quantidade': 'Total de Vendas'},
                    color='Promotor Venda Prospecção',
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
        
#====================================================================================================================================================================#

        # Processo de conversão da coluna 'Data Filiação' para datetime, se necessário
        # processed_data['Data Filiação'] = pd.to_datetime(processed_data['Data Filiação'])







        # Checkbox para selecionar a data
        show_date_input = st.sidebar.checkbox('Selecionar Data')
        
        st.markdown('<hr>', unsafe_allow_html=True)

        if show_date_input:
            # Sidebar para selecionar a data
            selected_date = st.sidebar.date_input('Selecione uma data', min_value=df_projec['Data filiação'].min(), max_value=df_projec['Data filiação'].max(), value=df_projec['Data filiação'].max())

            # Filtrar os dados para a data selecionada
            dados_selecionados = df_projec[df_projec['Data filiação'].dt.date == selected_date]

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

if __name__ == "__main__":
    main()
