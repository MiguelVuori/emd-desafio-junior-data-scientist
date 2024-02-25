#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt
import plotly.express as px
import basedosdados as bd

#######################
# Page configuration
st.set_page_config(
    page_title="Chamados ao 1746, Rio de Janeiro",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# Load data

@st.cache_data
def load_data(limit):
    df_bairro = bd.read_sql("SELECT id_bairro, nome, geometry FROM `datario.dados_mestres.bairro` ", billing_project_id="seismic-harmony-413819")
    df_chamados = bd.read_sql("SELECT id_chamado, id_bairro, data_inicio, subtipo FROM `datario.administracao_servicos_publicos.chamado_1746`" + str(limit), billing_project_id="seismic-harmony-413819")
    df_eventos = bd.read_sql("SELECT * FROM `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` ", billing_project_id="seismic-harmony-413819")

    df_bairro_ano_chamados = df_chamados.copy()
    df_bairro_ano_chamados['data_inicio'] = df_bairro_ano_chamados['data_inicio'].dt.year
    df_bairro_ano_chamados = df_bairro_ano_chamados.merge(df_bairro, on='id_bairro').groupby(['nome','data_inicio']).agg({'id_chamado': 'count'})
    df_bairro_ano_chamados = df_bairro_ano_chamados.rename(columns={'id_chamado':'num_chamados'})
    df_bairro_ano_chamados = df_bairro_ano_chamados.reset_index()
    df_num_chamados = df_chamados.merge(df_bairro, on='id_bairro').groupby('id_bairro').agg({'id_chamado': 'count'})
    df_num_chamados.columns = ['num_chamados']
    df_num_chamados = pd.merge(df_num_chamados, df_bairro, on='id_bairro')

    chamados_perturbação_sossego = df_chamados[df_chamados['subtipo'] == 'Perturbação do sossego']
    chamados_com_eventos = pd.merge(chamados_perturbação_sossego, df_eventos, how='cross')
    chamados_com_eventos = chamados_com_eventos[(chamados_com_eventos['data_inicio'].dt.date >= chamados_com_eventos['data_inicial']) & (chamados_com_eventos['data_inicio'].dt.date <= chamados_com_eventos['data_final'])]
    

    return df_bairro, df_chamados, df_eventos,df_bairro_ano_chamados, df_num_chamados, chamados_perturbação_sossego, chamados_com_eventos

df_bairro, df_chamados, df_eventos,df_bairro_ano_chamados, df_num_chamados, chamados_perturbação_sossego, chamados_com_eventos = load_data('')

#######################
# Sidebar
with st.sidebar:
    st.title('🏂 Total de chamados ao 1746, Rio de Janeiro')
   
    year_list = list(df_chamados['data_inicio'].dt.year.unique())[::-1]
    subtipo_list = list(df_chamados['subtipo'].unique())[::-1]

    if 2023 in year_list:
        default_year = year_list.index(2023)
    else:
        default_year = 0
    
    
    if 'Perturbação do sossego' in subtipo_list:
        default_subtipo = subtipo_list.index('Perturbação do sossego')
    else:
        default_subtipo = 0

    selected_year = st.selectbox('Selecione um ano', year_list, index=default_year)
    df_selected_year = df_bairro_ano_chamados[df_bairro_ano_chamados['data_inicio'] == selected_year]
    
    selected_subtipo = st.selectbox('Select um subtipo', subtipo_list, index=default_subtipo)
    df_selected_subtipo = df_chamados[df_chamados['subtipo'] == selected_subtipo]
    


    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

#######################
# Plots

# Heatmap
@st.cache_data
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):

    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    return heatmap

# Choropleth map

@st.cache_data
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    input_df['geometry'] = gpd.GeoSeries.from_wkt(input_df['geometry'])
    geo_df = gpd.GeoDataFrame(input_df, geometry='geometry')
    choropleth = px.choropleth(geo_df,geojson=geo_df.geometry, locations=geo_df.index, color=input_column,
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(geo_df.num_chamados)),
                               labels={'chamados':'Chamados'}
                              )
    choropleth.update_geos(fitbounds='geojson', visible= False)
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Convert population to text 
def format_number(num):
    if num > 1000:
        if num > 1000000:
            if not num % 1000000:
                return f'{num // 1000000} M'
            return f'{round(num / 1000000, 1)} M'
        return f'{num // 1000} K'
    return f'{num}'

# Calculation year-over-year chamados
@st.cache_data
def calculate_chamados_difference(input_df, input_year):

    selected_year_data = input_df[input_df['data_inicio'] == input_year].reset_index()
    previous_year_data = input_df[input_df['data_inicio'] == input_year - 1].reset_index()

    selected_year_data['chamados_difference'] = selected_year_data.num_chamados.sub(previous_year_data.num_chamados, fill_value=0)
    return pd.concat([selected_year_data.nome, selected_year_data.num_chamados, selected_year_data.chamados_difference], axis=1).sort_values(by="chamados_difference", ascending=False)


# Merge for metrics
@st.cache_data
def merge_for_metrics(input_df, groupby_index, date=None):

    if date == None:
        chamados = input_df[(input_df['data_inicio'].dt.date >= input_df['data_inicial']) & (input_df['data_inicio'].dt.date <= input_df['data_final'])]
        chamados['data_chamada'] = pd.to_datetime(chamados['data_inicio']).dt.date
        num_chamados_por_dia = chamados.groupby(groupby_index).size()
        media_chamados_por_dia = num_chamados_por_dia.mean()
        print('sum:', num_chamados_por_dia.sum(), 'dias:', num_chamados_por_dia.shape[0])
    else:
        chamados = input_df[(input_df['data_inicio'].dt.date >= pd.to_datetime(date[0])) & (input_df['data_inicio'].dt.date <= pd.to_datetime(date[1]))]
        chamados['data_chamada'] = pd.to_datetime(chamados['data_inicio']).dt.date
        num_chamados_por_dia = chamados.groupby(groupby_index).size()
        media_chamados_por_dia = num_chamados_por_dia.mean()
        print('sum:', num_chamados_por_dia.sum(), 'dias:', num_chamados_por_dia.shape[0])

    return media_chamados_por_dia

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Chamados em ' + str(selected_year))

    df_chamados_difference_sorted = calculate_chamados_difference(df_bairro_ano_chamados, selected_year)

    if selected_year > 2010:
        first_bairro_name = df_chamados_difference_sorted.nome.iloc[0]
        first_bairro_chamados = format_number(df_chamados_difference_sorted.num_chamados.iloc[0])
        first_bairro_delta = format_number(df_chamados_difference_sorted.chamados_difference.iloc[0])
    else:
        first_bairro_name = '-'
        first_bairro_chamados = '-'
        first_bairro_delta = ''

    st.metric(label=first_bairro_name, value=first_bairro_chamados, delta=first_bairro_delta)

    st.markdown('#### Média de chamados por dia relativos à ' + str(selected_subtipo))
    
    # ## Consulta 1: Média de chamados por dia em 2 anos

    media_chamados_por_dia_2_anos = merge_for_metrics(df_selected_subtipo, ['data_chamada'], date=['2022-01-01','2023-12-31'])

    st.metric(label="2022-2023", value="{:.1f}".format(media_chamados_por_dia_2_anos))



    # ## Consulta 2: Média de chamados por dia para eventos

    media_chamados_por_dia = merge_for_metrics(chamados_com_eventos, ['data_chamada', 'evento'], date=None)

    st.metric(label="eventos", value="{:.1f}".format(media_chamados_por_dia))

with col[1]:
    st.markdown('#### Chamados ao 1746')
    
    choropleth = make_choropleth(df_num_chamados, 'nome', 'num_chamados', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    heatmap = make_heatmap(df_bairro_ano_chamados, 'data_inicio', 'nome', 'num_chamados', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col[2]:
    st.markdown('#### Top Bairros')

    st.dataframe(df_selected_year.sort_values(by="num_chamados", ascending=False),
                 column_order=("nome", "num_chamados"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "nome": st.column_config.TextColumn(
                        "Bairro",
                    ),
                    "num_chamados": st.column_config.ProgressColumn(
                        "Chamados",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year.sort_values(by="num_chamados", ascending=False).num_chamados),
                     )}
                 )
    
    st.markdown('#### Chamados por evento')

    chamados_por_eventos = chamados_com_eventos[['evento', 'data_inicio']]
    chamados_por_eventos = chamados_por_eventos.groupby('evento').size()
    chamados_por_eventos = pd.DataFrame({'evento':chamados_por_eventos.index, 'num_chamados':chamados_por_eventos.values})
    bar = px.bar(chamados_por_eventos, x='evento', y='num_chamados')
    st.plotly_chart(bar, use_container_width=True)