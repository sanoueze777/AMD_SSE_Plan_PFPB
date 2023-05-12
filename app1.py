import altair as alt
import streamlit as st
from vega_datasets import data
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

# Loading the cars dataset
df = data.cars()

# List of quantitative data items
item_list = [
    col for col in df.columns if df[col].dtype in ['float64', 'int64']]

# List of Origins
origin_list = list(df['Origin'].unique())

# Create the column of YYYY 
df['YYYY'] = df['Year'].apply(lambda x: x.year)
min_year = df['YYYY'].min()
max_year = df['YYYY'].max()

st.set_page_config(layout="wide")
st.sidebar.image("gttBKso5_400x400.jpg", use_column_width=False)
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
with st.sidebar:
		choice = option_menu(None,["Accueil", 'Rechercher',"Statistiques"], 
	icons=['house','list-task','gear'], default_index=0,styles={
        "nav-link-selected": {"background-color": "red"},
    })
# Sidebar
st.sidebar.title("Système de Suivi Evaluation HYDROMET")
st.sidebar.markdown('###')
st.sidebar.markdown("### Parametres")
start_year, end_year = st.sidebar.slider(
    "Période",
    min_value=min_year, max_value=max_year,
    value=(min_year, max_year))

st.sidebar.markdown('###')
origins = st.sidebar.multiselect('Origins', origin_list,
                                 default=origin_list)
st.sidebar.markdown('###')
item1 = st.sidebar.selectbox('element 1', item_list, index=0)
item2 = st.sidebar.selectbox('element 2', item_list, index=3)

df_rng = df[(df['YYYY'] >= start_year) & (df['YYYY'] <= end_year)]
source = df_rng[df_rng['Origin'].isin(origins)]

# Content
base = alt.Chart(source).properties(height=300)

bar = base.mark_bar().encode(
    x=alt.X('count(Origin):Q', title='Number of Records'),
    y=alt.Y('Origin:N', title='Origin'),
    color=alt.Color('Origin:N', legend=None)
)

point = base.mark_circle(size=50).encode(
    x=alt.X(item1 + ':Q', title=item1),
    y=alt.Y(item2 + ':Q', title=item2),
    color=alt.Color('Origin:N', title='',
                    legend=alt.Legend(orient='bottom-left'))
)

line1 = base.mark_line(size=5).encode(
    x=alt.X('yearmonth(Year):T', title='Date'),
    y=alt.Y('mean(' + item1 + '):Q', title='exemple'),
    color=alt.Color('Origin:N', title='',
                    legend=alt.Legend(orient='bottom-left'))
)

line2 = base.mark_line(size=5).encode(
    x=alt.X('yearmonth(Year):T', title='Date'),
    y=alt.Y('mean(' + item2 + '):Q', title='exemple'),
    color=alt.Color('Origin:N', title='',
                    legend=alt.Legend(orient='bottom-left'))
)

# Layout (Content)
left_column, right_column = st.columns(2)
df = pd.DataFrame(
    np.random.randn(100, 2) / [1, 1] + [17.573934, -3.9861092],
    columns=['lat', 'lon'])

left_column.map(df)
left_column.markdown(
    '**Indicateur  1 exemple')
left_column.altair_chart(bar, use_container_width=True)

right_column.markdown(
    '**Indicateur 2 exemple' )
right_column.altair_chart(point, use_container_width=True)

left_column.markdown( '_ (Indicateur  3 exemple )**')
left_column.altair_chart(line1, use_container_width=True)

right_column.markdown('_ (Indicateur  4 exemple)**')
right_column.altair_chart(line2, use_container_width=True)