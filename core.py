import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Budget",
    page_icon="💰",
    layout="wide"
)

# Initialisation des données dans la session
if 'budget_mensuel' not in st.session_state:
    st.session_state.budget_mensuel = 0
if 'enveloppes' not in st.session_state:
    st.session_state.enveloppes = {}
if 'depenses' not in st.session_state:
    st.session_state.depenses = []

# Fonction pour sauvegarder les données
def sauvegarder_donnees():
    donnees = {
        'budget_mensuel': st.session_state.budget_mensuel,
        'enveloppes': st.session_state.enveloppes,
        'depenses': st.session_state.depenses
    }
    with open('donnees_budget.json', 'w') as f:
        json.dump(donnees, f)

# Fonction pour charger les données
def charger_donnees():
    try:
        with open('donnees_budget.json', 'r') as f:
            donnees = json.load(f)
            st.session_state.budget_mensuel = donnees['budget_mensuel']
            st.session_state.enveloppes = donnees['enveloppes']
            st.session_state.depenses = donnees['depenses']
    except FileNotFoundError:
        pass

# Chargement des données au démarrage
charger_donnees()

# Titre de l'application
st.title("💰 Gestionnaire de Budget par Enveloppes")

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration")
    nouveau_budget = st.number_input(
        "Budget mensuel (€)",
        min_value=0.0,
        value=float(st.session_state.budget_mensuel),
        step=100.0
    )
    
    if nouveau_budget != st.session_state.budget_mensuel:
        st.session_state.budget_mensuel = nouveau_budget
        sauvegarder_donnees()

    # Gestion des enveloppes
    st.subheader("Gestion des enveloppes")
    nouvelle_enveloppe = st.text_input("Nom de la nouvelle enveloppe")
    montant_enveloppe = st.number_input("Montant de l'enveloppe (€)", min_value=0.0, step=10.0)
    
    if st.button("Ajouter l'enveloppe"):
        if nouvelle_enveloppe and montant_enveloppe > 0:
            st.session_state.enveloppes[nouvelle_enveloppe] = montant_enveloppe
            sauvegarder_donnees()
            st.success(f"Enveloppe '{nouvelle_enveloppe}' ajoutée!")

# Corps principal
col1, col2 = st.columns(2)

# Ajout des dépenses
with col1:
    st.header("Ajouter une dépense")
    with st.form("nouvelle_depense"):
        montant = st.number_input("Montant (€)", min_value=0.0, step=0.5)
        categorie = st.selectbox("Catégorie", options=list(st.session_state.enveloppes.keys()))
        description = st.text_input("Description")
        date = st.date_input("Date")
        
        if st.form_submit_button("Ajouter"):
            if montant > 0 and categorie:
                nouvelle_depense = {
                    'montant': montant,
                    'categorie': categorie,
                    'description': description,
                    'date': date.strftime("%Y-%m-%d")
                }
                st.session_state.depenses.append(nouvelle_depense)
                sauvegarder_donnees()
                st.success("Dépense ajoutée avec succès!")

# Affichage des jauges
with col2:
    st.header("Suivi des enveloppes")
    
    for categorie, budget in st.session_state.enveloppes.items():
        depenses_categorie = sum(d['montant'] for d in st.session_state.depenses 
                               if d['categorie'] == categorie)
        
        # Création de la jauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=depenses_categorie,
            title={'text': f"Enveloppe: {categorie}"},
            delta={'reference': budget},
            gauge={
                'axis': {'range': [None, budget]},
                'bar': {'color': "darkblue"},
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': budget
                }
            }
        ))
        
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)

# Historique des dépenses
st.header("Historique des dépenses")
if st.session_state.depenses:
    df = pd.DataFrame(st.session_state.depenses)
    st.dataframe(df)
