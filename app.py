import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Gestion de l'inventaire", layout="wide")

# ---------------------------------------------------------
# 2️⃣ FONCTION POUR CHARGER L'EXCEL
# ---------------------------------------------------------
@st.cache_data # Pour que l'app soit rapide
def charger_donnees():
    nom_fichier = "Inventaire.xlsx" # Doit correspondre exactement au nom sur GitHub
    if os.path.exists(nom_fichier):
        try:
            df = pd.read_excel(nom_fichier)
            return df
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
            return pd.DataFrame()
    else:
        st.error(f"Fichier '{nom_fichier}' introuvable.")
        return pd.DataFrame()

# -------------------------
# 3️⃣ AUTHENTIFICATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Connexion au Système ERP</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if user == "admin" and pwd == "pass1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ Identifiants incorrects")
    st.stop()

# -------------------------
# 4️⃣ TRAITEMENT DES FILTRES
# -------------------------
df_global = charger_donnees()

# Sidebar
st.sidebar.header("🔍 Filtres de recherche")

if not df_global.empty:
    # Liste des clients unique
    liste_clients = ["Tous les clients"] + sorted(df_global['Client'].dropna().unique().tolist())
    client_filtre = st.sidebar.selectbox("Filtrer par Client", options=liste_clients)
    
    # Liste des statuts (si la colonne existe)
    if 'Statut' in df_global.columns:
        liste_statuts = ["Tous"] + sorted(df_global['Statut'].dropna().unique().tolist())
    else:
        liste_statuts = ["Tous"]
    statut_filtre = st.sidebar.selectbox("Filtrer par Statut", options=liste_statuts)
else:
    client_filtre = "Tous les clients"
    statut_filtre = "Tous"

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# -------------------------
# 5️⃣ AFFICHAGE PRINCIPAL
# -------------------------
st.title("📦 Gestion de l'inventaire")

if not df_global.empty:
    df_affichage = df_global.copy()

    # Appliquer les filtres
    if client_filtre != "Tous les clients":
        df_affichage = df_affichage[df_affichage['Client'] == client_filtre]
    
    if statut_filtre != "Tous" and 'Statut' in df_affichage.columns:
        df_affichage = df_affichage[df_affichage['Statut'] == statut_filtre]

    st.info(f"Affichage de **{len(df_affichage)}** lignes après filtrage.")
    st.dataframe(df_affichage, use_container_width=True, hide_index=True)
else:
    st.warning("Aucune donnée disponible dans le fichier Excel.")

st.divider()

# -------------------------
# 6️⃣ BOUTONS D'ACTION
# -------------------------
c1, c2 = st.columns(2)
with c1:
    st.button("💾 Sauvegarder directement sur Excel", use_container_width=True)
with c2:
    st.button("📩 Télécharger une copie (Backup)", use_container_width=True)
