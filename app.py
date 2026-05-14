Aimport streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1️⃣ CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="ERP Solaire - Gestion de l'inventaire",
    layout="wide"
)

# ---------------------------------------------------------
# 2️⃣ CONNEXION À LA BASE DE DONNÉES
# ---------------------------------------------------------
def obtenir_connexion():
    try:
        return sqlite3.connect(
            'database.db',
            check_same_thread=False
        )
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None


# -------------------------
# 3️⃣ AUTHENTIFICATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(
        "<h2 style='text-align: center; color: #1e3a8a;'>🔐 Connexion au Système ERP</h2>",
        unsafe_allow_html=True
    )

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
        # Liste des clients pour le filtre
        df_c = pd.read_sql(
            """
            SELECT DISTINCT nom_client
            FROM Clients
            ORDER BY nom_client ASC
            """,
            conn
        )

        clients_list += df_c["nom_client"].tolist()

        # Charger l'inventaire
        df_inventaire = pd.read_sql(
            "SELECT * FROM Inventaire",
            conn
        )

    except Exception as e:
        st.error(f"Erreur : {e}")

    finally:
        conn.close()


# -------------------------
# 5️⃣ BARRE LATÉRALE (FILTRES)
# -------------------------
st.sidebar.title("🔍 Filtres de recherche")

# Filtre par client
client_filtre = st.sidebar.selectbox(
    "Filtrer par Client",
    options=clients_list
)

# Filtre par statut
statut_filtre = st.sidebar.selectbox(
    "Filtrer par Statut",
    options=["Tous", "En cours", "Livré", "En attente"]
)

# Déconnexion
if st.sidebar.button("🚪 Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()


# -------------------------
# 6️⃣ INTERFACE PRINCIPALE
# -------------------------
st.title("📦 Gestion de l'inventaire")


# -------------------------
# 7️⃣ FILTRAGE + TABLEAU
# -------------------------
if not df_inventaire.empty:

    df_affichage = df_inventaire.copy()

    # Filtrer par client
    if client_filtre != "Tous les clients":
        df_affichage = df_affichage[
            df_affichage["client_concerne"] == client_filtre
        ]

    # Filtrer par statut
    if (
        statut_filtre != "Tous"
        and "statut" in df_affichage.columns
    ):
        df_affichage = df_affichage[
            df_affichage["statut"] == statut_filtre
        ]

    # -------------------------------------------------
    # CLIENT AVANT SHIPMENT NO.
    # -------------------------------------------------
    if "client_concerne" in df_affichage.columns:

        # Renommer pour affichage
        df_affichage = df_affichage.rename(
            columns={
                "client_concerne": "Client"
            }
        )

        # Liste des colonnes
        cols = list(df_affichage.columns)

        # Supprimer Client temporairement
        cols.remove("Client")

        # Mettre Client avant Shipment No.
        if "Shipment No." in cols:
            shipment_index = cols.index("Shipment No.")
            cols.insert(
                shipment_index,
                "Client"
            )
        else:
            cols = ["Client"] + cols

        # Réorganiser le tableau
        df_affichage = df_affichage[cols]

    st.write(
        f"Affichage de **{len(df_affichage)}** lignes après filtrage."
    )

    # Tableau
    st.dataframe(
        df_affichage,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "Aucune donnée d'inventaire disponible."
    )


st.divider()

# -------------------------
# 8️⃣ BOUTONS D'ACTION
# -------------------------
c1, c2 = st.columns(2)

with c1:
    st.button(
        "💾 Sauvegarder directement sur Excel",
        use_container_width=True
    )

with c2:
    st.button(
        "📩 Télécharger une copie de sauvegarde (Backup)",
        use_container_width=True
    )
