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
from pandasql import sqldf
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

##########################################  deployed
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
    sql = '''SELECT DISTINCT mission from Mission_executee'''
    cur = conn.cursor(buffered=True)
    cur.execute(sql)
    conn.commit()
    return cur

def select_all_actions(conn):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = '''SELECT * from Action_executee'''
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


def select_all_experts(conn):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = '''SELECT * from Expert_activite'''
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
              VALUES(%s,%s,%s,%s,%s,%s) '''
    cur = conn.cursor()
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
              VALUES(%s,%s,%s,%s) '''
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
              VALUES(%s,%s,%s,%s) '''
    cur = conn.cursor(buffered=True)
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid
def highlight_survived(s):
    return ['background-color: lightgreen']*len(s) if 50<s else ['background-color: pink']*len(s)

def color_survived(val):
    color = 'green' if 50<val else 'pink'
    return f'background-color: {color}'

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

    experts_table = select_all_actions(conn).fetchall()
    missions_table = select_all_actions(conn).fetchall()

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
        df["Temps de travail estimé"] = 0
        
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
                    action_planifié = (mission,str(date_debut),str(date_fin),responsable,champ_act_planifié,Temps_tra_planifié)
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
        
        experts_table = pd.DataFrame(experts_table, columns = ["Numero","Expert","Date","Mission","Activité","Temps de travail","Lieu de travail" ])
        
        #xperts_table.colunms = ["Numero","Expert","Date","Mission","Activité","Temps de travail","Lieu de travail" ]
        
        experts_table["taux d'exécution %"]=0
        for i in range(len(experts_table)):
            if experts_table.loc[i,"Activité"] == "Réunions cadrage /démarrage":
                experts_table.loc[i,"taux d'exécution %"] = 5
            elif experts_table.loc[i,"Activité"] == "Atelier cadrage":
                experts_table.loc[i,"taux d'exécution %"] = 5
            elif experts_table.loc[i,"Activité"] == "Outils collecte":
                experts_table.loc[i,"taux d'exécution %"] = 15
            elif experts_table.loc[i,"Activité"] == "Collecte données 1 (entretiens)":
                experts_table.loc[i,"taux d'exécution %"] = 30
            elif experts_table.loc[i,"Activité"] == "Collecte données 2 (Revue doc/BD)":
                experts_table.loc[i,"taux d'exécution %"] = 45
            elif experts_table.loc[i,"Activité"] == "Reunion étape mise en œuvre":
                experts_table.loc[i,"taux d'exécution %"] = 60
            elif experts_table.loc[i,"Activité"] == "Rapports d'étude":
                experts_table.loc[i,"taux d'exécution %"] = 80
            elif experts_table.loc[i,"Activité"] == "Atelier examen /validation":
                experts_table.loc[i,"taux d'exécution %"] = 100
            else:
                experts_table.loc[i,"taux d'exécution %"] = None
        #st.table(experts_table)
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        #experts_table = experts_table[(pd.DatetimeIndex(experts_table['Date']).month==currentMonth) & (pd.DatetimeIndex(experts_table["Date"]).year==currentYear)]
        
        st.write("Activité des experts ce mois")
        
        
        experts_summary = experts_table.groupby("Expert")["Temps de travail"].sum()
        experts_summary = experts_summary.to_frame()
        st.dataframe(experts_summary.style.applymap(color_survived, subset=["Temps de travail"]))
        
        left_column, right_column = st.columns(2)
        df = pd.DataFrame(
            np.random.randn(100, 2) / [1, 1] + [17.573934, -3.9861092],
            columns=['lat', 'lon'])
        


    # Content
 
    

        for i in range(len(experts_table)):
            experts_table.loc[i,"Temps de travail"] = float(experts_table.loc[i,"Temps de travail"])
        
        
        chart = alt.Chart(experts_table).mark_bar().encode(
        x='Activité', y='Temps de travail',color='Expert')
        chart.save('chart.html')

        right_column.altair_chart(chart, use_container_width=True)
        #left_column.chart_1
        
        chart_2 = alt.Chart(experts_table).mark_bar().encode(
        x='Mission', y='Temps de travail',color='Expert')
        chart.save('chart.html')

        left_column.altair_chart(chart_2, use_container_width=True)
        
        chart_3 = alt.Chart(experts_table).mark_bar().encode(
        x='Temps de travail', y='Expert',color='Mission')
        chart.save('chart.html')

        st.altair_chart(chart_3, use_container_width=True)
        
        st.write("historique des activités")
        st.dataframe(experts_table.style.applymap(color_survived, subset=["taux d'exécution %"]))
        
        st.write("Feuilles de temps")
        gb = GridOptionsBuilder.from_dataframe(experts_table)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
                experts_table,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT', 
                update_mode='MODEL_CHANGED', 
                fit_columns_on_grid_load=False,
                enable_enterprise_modules=True,
                height=500, 
                width='100%',
                reload_data=True
                )
        
        data = grid_response['data']
        data_x = data.to_csv("data_x.csv")
        """
        st.download_button(
        label="Enregistrer la feuille de temps csv",
        data=data_x,
        file_name=f"feuille_de_temps_{data.loc[1,'Expert']}.csv",
        mime='text/csv',
        )
        """
        
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
        
        
        experts_table = pd.DataFrame(experts_table, columns = ["Numero","Expert","Date","Mission","Activité","Temps de travail","Lieu de travail" ])
        
        experts_table["taux d'exécution %"] = 0
        for i in range(len(experts_table)):
            if experts_table.loc[i,"Activité"] == "Réunions cadrage /démarrage":
                experts_table.loc[i,"taux d'exécution %"] = 5
            elif experts_table.loc[i,"Activité"] == "Atelier cadrage":
                experts_table.loc[i,"taux d'exécution %"] = 5
            elif experts_table.loc[i,"Activité"] == "Outils collecte":
                experts_table.loc[i,"taux d'exécution %"] = 15
            elif experts_table.loc[i,"Activité"] == "Collecte données 1 (entretiens )":
                experts_table.loc[i,"taux d'exécution %"] = 30
            elif experts_table.loc[i,"Activité"] == "Collecte données 2 (Revue doc/BD)":
                experts_table.loc[i,"taux d'exécution %"] = 45
            elif experts_table.loc[i,"Activité"] == "Reunion étape mise en œuvre":
                experts_table.loc[i,"taux d'exécution %"] = 60
            elif experts_table.loc[i,"Activité"] == "Rapports d'étude":
                experts_table.loc[i,"taux d'exécution %"] = 80
            elif experts_table.loc[i,"Activité"] == "Atelier examen /validation":
                experts_table.loc[i,"taux d'exécution %"] = 100
            else:
                experts_table.loc[i,"taux d'exécution %"] = None
                
                
        table_summary = experts_table.groupby("Mission")["taux d'exécution %"].max()
        table_summary = table_summary.to_frame()
        st.dataframe(table_summary.style.applymap(color_survived, subset=["taux d'exécution %"]))
        
        
        
        left_column, right_column = st.columns(2)
        
        
        for i in range(len(experts_table)):
            experts_table.loc[i,"Temps de travail"] = float(experts_table.loc[i,"Temps de travail"])
        
        
        chart = alt.Chart(experts_table).mark_bar().encode(
        x='Mission', y='Temps de travail',color='Expert')
        chart.save('chart.html')

        right_column.altair_chart(chart, use_container_width=True)
        #left_column.chart_1
        
        chart_2 = alt.Chart(experts_table).mark_bar().encode(
        x='Mission', y='Temps de travail',color='Expert')
        chart.save('chart.html')

        left_column.altair_chart(chart_2, use_container_width=True)
        
        chart_3 = alt.Chart(experts_table).mark_bar().encode(
        x='Temps de travail', y='Expert',color='Mission')
        chart.save('chart.html')

        st.altair_chart(chart_3, use_container_width=True)
        
        st.dataframe(experts_table.style.applymap(color_survived, subset=["taux d'exécution %"]))
        
        

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')