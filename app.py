import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="ERP Solaire - Inventaire Excel",
    layout="wide"
)

# ---------------------------------------------------------
# 2️⃣ CHARGEMENT DES DONNÉES DEPUIS EXCEL
# ---------------------------------------------------------
def charger_donnees():
    nom_fichier = 'inventaire.xlsx' # ⚠️ Ton fichier doit s'appeler exactement comme ça
    if os.path.exists(nom_fichier):
        try:
            # Lire le fichier Excel
            df = pd.read_excel(nom_fichier)
            return df
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
            return pd.DataFrame()
    else:
        st.error(f"⚠️ Le fichier '{nom_fichier}' est introuvable dans le dossier.")
        return pd.DataFrame()

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
# 4️⃣ TRAITEMENT DES DONNÉES
# -------------------------
df_global = charger_donnees()

# Préparer les filtres
clients_list = ["Tous les clients"]
if not df_global.empty and 'Client' in df_global.columns:
    clients_list += sorted(df_global['Client'].dropna().unique().tolist())

# -------------------------
# 5️⃣ BARRE LATÉRALE (FILTRES)
# -------------------------
st.sidebar.title("🔍 Filtres de recherche")
client_filtre = st.sidebar.selectbox("Filtrer par Client", options=clients_list)

statut_options = ["Tous"]
if not df_global.empty and 'Statut' in df_global.columns:
    statut_options += sorted(df_global['Statut'].dropna().unique().tolist())

statut_filtre = st.sidebar.selectbox("Filtrer par Statut", options=statut_options)

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# -------------------------
# 6️⃣ INTERFACE PRINCIPALE
# -------------------------
st.title("📦 Gestion de l'inventaire (Source: Excel)")

if not df_global.empty:
    df_affichage = df_global.copy()

    # Filtrage par client
    if client_filtre != "Tous les clients":
        df_affichage = df_affichage[df_affichage['Client'] == client_filtre]
    
    # Filtrage par statut
    if statut_filtre != "Tous":
        df_affichage = df_affichage[df_affichage['Statut'] == statut_filtre]

    # Affichage du nombre de lignes
    st.info(f"Affichage de **{len(df_affichage)}** lignes après filtrage.")

    # Affichage du tableau
    st.dataframe(df_affichage, use_container_width=True, hide_index=True)

else:
    st.warning("Veuillez vérifier que votre fichier 'inventaire.xlsx' contient des données.")

st.divider()

# -------------------------
# 7️⃣ BOUTONS D'ACTION
# -------------------------
c1, c2 = st.columns(2)
with c1:
    # Bouton de téléchargement simple
    st.download_button(
        label="💾 Exporter vers Excel",
        data=df_global.to_csv(index=False).encode('utf-8'),
        file_name='export_inventaire.csv',
        mime='text/csv',
        use_container_width=True
    )
with c2:
    st.button("📩 Créer un Backup", use_container_width=True)
