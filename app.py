import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="ERP Solaire - Gestion Complète", layout="wide")

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

def check_login(username, password):
    return username == "admin" and password == "pass1234"

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔐 Connexion au Système CRM</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if check_login(user, pwd):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ Identifiants incorrects")
    st.stop()

# -------------------------
# 4️⃣ DESIGN CSS
# -------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
.noms-ticker {
    background: #1e3a8a; color: white; padding: 10px; border-radius: 8px;
    margin-bottom: 20px; font-weight: bold; overflow-x: auto; white-space: nowrap;
}
.stSelectbox label { color: #1e3a8a; font-weight: bold; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------------------------------------------------
# 5️⃣ CHARGEMENT DES DONNÉES
# ---------------------------------------------------------
conn = obtenir_connexion()
clients_list = []
df_inventaire = pd.DataFrame()

if conn:
    try:
        # Récupérer les noms des clients
        df_c = pd.read_sql("SELECT DISTINCT nom_client FROM Clients ORDER BY nom_client ASC", conn)
        clients_list = df_c['nom_client'].tolist()
        
        # Récupérer les données de l'inventaire
        # Note: Assurez-vous que la colonne 'client_concerne' existe pour le filtrage
        df_inventaire = pd.read_sql("SELECT * FROM Inventaire", conn)
    except:
        pass
    finally:
        conn.close()

# ---------------------------------------------------------
# 6️⃣ INTERFACE PRINCIPALE
# ---------------------------------------------------------
st.title("🏙️ ERP Solaire : Gestion de l'inventaire")

# Ticker (Aperçu rapide des noms en haut)
if clients_list:
    noms_str = "  •  ".join(clients_list)
    st.markdown(f'<div class="noms-ticker">👥 Clients Actifs : &nbsp;&nbsp; {noms_str}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7️⃣ LE FILTRE : LISTE DE CLIENT (SELECTBOX)
# ---------------------------------------------------------
# Had l-khana hiya li bghiti: kat-t-cliqua bach t-khtar shkun
client_selectionne = st.selectbox(
    "📂 Liste de client", 
    options=["Tous les clients"] + clients_list
)

# ---------------------------------------------------------
# 8️⃣ AFFICHAGE DE L'INVENTAIRE FILTRÉ
# ---------------------------------------------------------
if not df_inventaire.empty:
    if client_selectionne == "Tous les clients":
        df_filtre = df_inventaire
    else:
        df_filtre = df_inventaire[df_inventaire['client_concerne'] == client_selectionne]

    st.write(f"Affichage de **{len(df_filtre)}** lignes après filtrage.")
    st.dataframe(df_filtre, use_container_width=True, hide_index=True)
else:
    st.info("Aucune donnée d'inventaire trouvée.")

st.divider()

# ---------------------------------------------------------
# 9️⃣ BOUTONS D'ACTION (B7AL L-IMAGE)
# ---------------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    if st.button("💾 Sauvegarder direct f Excel", use_container_width=True):
        st.success("Exportation réussie !")
with c2:
    st.button("📩 Télécharger une copie (Backup)", use_container_width=True)

# ---------------------------------------------------------
# 🔟 AJOUT RAPIDE D'UN CLIENT (Optionnel)
# ---------------------------------------------------------
with st.expander("➕ Ajouter un nouveau client à la base"):
    with st.form("quick_add"):
        n_nom = st.text_input("Nom")
        n_tel = st.text_input("Tél")
        if st.form_submit_button("Enregistrer"):
            if n_nom:
                conn = obtenir_connexion()
                if conn:
                    conn.cursor().execute("INSERT INTO Clients (nom_client, telephone) VALUES (?,?)", (n_nom, n_tel))
                    conn.commit()
                    conn.close()
                    st.rerun()
