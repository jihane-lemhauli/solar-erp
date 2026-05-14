import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Gestion de l'inventaire", layout="wide")

# ---------------------------------------------------------
# 2️⃣ CONNEXION À LA BASE DE DONNÉES
# ---------------------------------------------------------
def obtenir_connexion():
    try:
        return sqlite3.connect('database.db', check_same_thread=False)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# -------------------------
# 3️⃣ AUTHENTIFICATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 Connexion au Système ERP</h2>", unsafe_allow_html=True)
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
# 4️⃣ CHARGEMENT DES DONNÉES
# -------------------------
conn = obtenir_connexion()
clients_list = ["Tous les clients"]
df_inventaire = pd.DataFrame()

if conn:
    try:
        # Récupérer les noms des clients pour le filtre latéral
        df_c = pd.read_sql("SELECT DISTINCT nom_client FROM Clients ORDER BY nom_client ASC", conn)
        clients_list += df_c['nom_client'].tolist()
        
        # Récupérer les données de l'inventaire
        df_inventaire = pd.read_sql("SELECT * FROM Inventaire", conn)
    except:
        pass
    finally:
        conn.close()

# -------------------------
# 5️⃣ BARRE LATÉRALE (FILTRES)
# -------------------------
st.sidebar.title("🔍 Filtres de recherche")

# Remplacement du filtre Shipment par la Liste des Clients
client_filtre = st.sidebar.selectbox("Filtrer par Client", options=clients_list)

statut_filtre = st.sidebar.selectbox("Filtrer par Statut", options=["Tous", "En cours", "Livré", "En attente"])

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# -------------------------
# 6️⃣ INTERFACE PRINCIPALE
# -------------------------
st.title("📦 Gestion de l'inventaire")

# 7️⃣ LOGIQUE DE FILTRAGE
df_affichage = df_inventaire.copy()

if not df_affichage.empty:
    # Filtrer par le client sélectionné dans la barre latérale
    if client_filtre != "Tous les clients":
        # On utilise la colonne 'client_concerne' pour faire la correspondance
        df_affichage = df_affichage[df_affichage['client_concerne'] == client_filtre]
    
    # Filtre par Statut (si la colonne existe dans votre table)
    if statut_filtre != "Tous" and 'statut' in df_affichage.columns:
        df_affichage = df_affichage[df_affichage['statut'] == statut_filtre]

    st.write(f"Affichage de **{len(df_affichage)}** lignes après filtrage.")
    
    # Affichage du tableau final
    st.dataframe(df_affichage, use_container_width=True, hide_index=True)
else:
    st.info("Aucune donnée d'inventaire disponible.")

st.divider()

# 8️⃣ BOUTONS D'ACTION
c1, c2 = st.columns(2)
with c1:
    st.button("💾 Sauvegarder directement sur Excel", use_container_width=True)
with c2:
    st.button("📩 Télécharger une copie de sauvegarde (Backup)", use_container_width=True)
