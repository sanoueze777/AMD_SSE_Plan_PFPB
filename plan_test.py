import altair as alt
import streamlit as st
from vega_datasets import data
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import date
import sqlite3
from sqlite3 import Error
from datetime import datetime
import mysql.connector

""" """""""""


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = mysql.connector.connect(user='u152993259_webmasteramd15', password='Jesussauve7',
                              host='sql735.main-hosting.eu',
                              database=db_file)
    except Error as e:
        print(e)

    return conn

def insert_executed_action(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO Action_executee(expert,date,mission,champ_activites,temps_travail,lieu)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor(buffered=True)
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def select_from_mission(conn):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = '''SELECT DISTINCT mission from mission_executee'''
    cur = conn.cursor(buffered=True)
    cur.execute(sql)
    conn.commit()
    return cur


def select_from_experts(conn):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = '''SELECT DISTINCT nom from Expert_activite'''
    cur = conn.cursor(buffered=True)
    cur.execute(sql)
    conn.commit()
    return cur

def create_task(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO Action_planifiee(mission,date_debut,date_fin,expert,champ_activites,temps_travail)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor(buffered=True)
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid


def insert_expert(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO Expert_activite(missions,champs_activites,temps_travail,nom)
              VALUES(?,?,?,?) '''
    cur = conn.cursor(buffered=True)
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid

def insert_mission(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO Mission_executee(mission,date_derniere_action,champ_activite_derniere_action,volume_travail_total)
              VALUES(?,?,?,?) '''
    cur = conn.cursor(buffered=True)
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid


""""""""""""


st.image("Capture d’écran 2022-10-17 175305.png", use_column_width=False)
st.title("SYSTEME DE SUIVI DES MISSIONS | planification")

hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """


today = date.today()


#st.set_page_config(layout="wide")
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


name, authentication_status, username = authenticator.login('Connexion', 'main')

if authentication_status:
    expert_name = st.session_state["name"]
    st.write(f"{today}")
    
    authenticator.logout('Se déconnecter', 'main')

    #####################################    Misions and experts List #################################
    database = "u152993259_sse"
    conn = create_connection(database)
    records1 = select_from_mission(conn).fetchall()
    records2 = select_from_experts(conn).fetchall()
    
    missions_list = []
    experts_list = []
    
    for row in records1:
        missions_list.append(row[0])
    for row in records2:
        experts_list.append(row[0])


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

    
    st.sidebar.image("Capture d’écran 2022-10-17 175305.png", use_column_width=False)
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    with st.sidebar:
            choice = option_menu(None,["Accueil", 'Suivi du personnel',"Suivi des missions"], 
        icons=['house','list-task','gear'], default_index=0,styles={
            "nav-link-selected": {"background-color": "red"},
        })
    # Sidebar
    st.sidebar.title(f"{expert_name} ")
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
    Main_df = pd.DataFrame({"Mission": [""], "Date de début": [""], "Date de fin": [""], "Expert": [""], "Champ d'activités": [""], "Temps de travail estimé": [None]})

    if choice == "Accueil":


        Mission_list = missions_list
        
        Activities_group_list = ["Réunions cadrage /démarrage","Atelier cadrage","Outils collecte","Rapport cadrage/démarrage","Collecte données 1 (entretiens )","Collecte données 2 (Revue doc/BD)","Reunion étape mise en œuvre","Rapports d'étude","Atelier examen /validation","Gestion / suivi de projet","Montage offres techniques","Gestion et animation du pôle"]

        Working_time = [str(1),str(0.75),str(0.5),str(0.25)]
        Working_Places = ["A distance","Au Bureau"]
        st.markdown(f"Veuillez entrer les missions à planifier. Pour modifier une planification, veuillez planifier la meme mission à nouveau")
        df = pd.DataFrame({"Mission": [""], "Date de début": [""], "Date de fin": [""], "Responsable": [""], "Champ d'activités": [""], "Temps de travail estimé": [None]})

        df["Mission"] = (
        df["Mission"].astype("category").cat.add_categories(Mission_list)
    )
        df["Date de début"] = ("JJ/MM/AAAA")
    
        df["Date de fin"] =  ("JJ/MM/AAAA")
    
        df["Responsable"] = (
        df["Responsable"].astype("category").cat.add_categories(experts_list)
    )
        
        df["Champ d'activités"] = ( df["Champ d'activités"].astype("category").cat.add_categories(Activities_group_list)
    )
        df["Temps de travail estimé"] = (
        df["Temps de travail estimé"].astype("category").cat.add_categories(Working_time)
    )
        
        edited_df = st.experimental_data_editor(df, num_rows="dynamic")
        if st.button('Enregistrer'):
            database = "u152993259_sse"
            conn = create_connection(database)
            can_insert = True
            for i in range(len(edited_df)):
                date_d = edited_df.loc[i,"Date de début"]
                date_f = edited_df.loc[i,"Date de fin"]
                format_string = "%d/%m/%Y"
                try:
                    date_dobj = datetime.strptime(date_d, format_string).date()
                    date_fobj = datetime.strptime(date_f, format_string).date()
                except:
                    st.write("impossible d'enregistrer : veuillez utiliser le format JJ/MM/AAAA pour les dates")
                    can_insert = False
                    break
            
            if can_insert == True:
                for i in range(len(edited_df)):
                    responsable = edited_df.loc[i,"Responsable"]
                    date_debut = edited_df.loc[i,"Date de début"]
                    date_fin = edited_df.loc[i,"Date de fin"]
                    mission = edited_df.loc[i,"Mission"]
                    champ_act_planifié = edited_df.loc[i,"Champ d'activités"]
                    Temps_tra_planifié = float(edited_df.loc[i,"Temps de travail estimé"])
                    action_planifié = (mission,date_debut,date_fin,responsable,champ_act_planifié,Temps_tra_planifié)
                    action_executed_id = create_task(conn, action_planifié)
                st.write("Enregistré avec succès !")





    if choice == "Suivi du personnel":
        
        Mission_list = missions_list
        
        Activities_group_list = ["Réunions cadrage /démarrage","Atelier cadrage","Outils collecte","Rapport cadrage/démarrage","Collecte données 1 (entretiens )","Collecte données 2 (Revue doc/BD)","Reunion étape mise en œuvre","Rapports d'étude","Atelier examen /validation","Gestion / suivi de projet","Montage offres techniques","Gestion et animation du pôle"]

        Working_time = [str(1),str(0.75),str(0.5),str(0.25)]
        Working_Places = ["A distance","Au Bureau"]
        st.markdown(f"Veuillez entrer un nouvel expert et cliquez sur enregistrer")
        df = pd.DataFrame({"Mission": [""], "Nom": [""], "Champ d'activités": [""], "Temps de travail estimé": [None]})

        df["Mission"] = (
        df["Mission"].astype("category").cat.add_categories(Mission_list)
    )
        
        df["Nom"] = ""
        
        df["Champ d'activités"] = ( df["Champ d'activités"].astype("category").cat.add_categories(Activities_group_list)
    )
        df["Temps de travail estimé"] = (
        df["Temps de travail estimé"].astype("category").cat.add_categories(Working_time)
    )
        
        edited_df = st.experimental_data_editor(df, num_rows="dynamic")
        if st.button('Enregistrer'):
            database = "u152993259_sse"
            conn = create_connection(database)
            for i in range(len(edited_df)):
                expert = edited_df.loc[i,"Nom"]
                mission = edited_df.loc[i,"Mission"]
                champ_act_planifié = edited_df.loc[i,"Champ d'activités"]
                Temps_tra_planifié = float(edited_df.loc[i,"Temps de travail estimé"])
                expert_inséré = (mission,champ_act_planifié,Temps_tra_planifié,expert)
                expert_inséré_id = insert_expert(conn, expert_inséré)
            st.write("Enregistré avec succès !")

                
                
                
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
        
        
        
    if choice == "Suivi des missions":
        
        Mission_list = missions_list
        
        Activities_group_list = ["Réunions cadrage /démarrage","Atelier cadrage","Outils collecte","Rapport cadrage/démarrage","Collecte données 1 (entretiens )","Collecte données 2 (Revue doc/BD)","Reunion étape mise en œuvre","Rapports d'étude","Atelier examen /validation","Gestion / suivi de projet","Montage offres techniques","Gestion et animation du pôle"]

        Working_time = [str(1),str(0.75),str(0.5),str(0.25)]
        Working_Places = ["A distance","Au Bureau"]
        st.markdown(f"Veuillez entrer une nouvelle mission et cliquez sur enregistrer")
        df = pd.DataFrame({"Mission": [""], "Champ d'activités": [""], "Temps de travail estimé": [None]})

        df["Mission"] = ""
    
        
        df["Date de dernière action"] = ""
        
        df["Champ d'activités"] = ( df["Champ d'activités"].astype("category").cat.add_categories(Activities_group_list)
    )
        df["Temps de travail estimé"] = 0
        
        edited_df = st.experimental_data_editor(df, num_rows="dynamic")
        if st.button('Enregistrer'):
            database = "u152993259_sse"
            conn = create_connection(database)
            for i in range(len(edited_df)):
                mission = edited_df.loc[i,"Mission"]
                derniere_action = edited_df.loc[i,"Date de dernière action"]
                champ_act_planifié = edited_df.loc[i,"Champ d'activités"]
                Temps_tra_planifié = float(edited_df.loc[i,"Temps de travail estimé"])
                mission_insérée = (mission,derniere_action,champ_act_planifié,Temps_tra_planifié)
                mission_insérée_inséré_id = insert_mission(conn, mission_insérée)
            st.write("Enregistré avec succès !")
            
            

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')