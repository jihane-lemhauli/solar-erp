import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. Configuration générale ---
st.set_page_config(
    page_title="PropMed ERP & Devis ☀️",
    layout="wide",
    page_icon="☀️"
)

# =========================================================
# 🎨 DESIGN PREMIUM MODERNE (CORRIGÉ)
# =========================================================
st.markdown("""
<style>

/* Arrière-plan général */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Navigation */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.06);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 6px;
    font-weight: 600;
}

/* Titre principal */
.main-title {
    color: #0f172a !important;
    font-size: 34px;
    font-weight: 800;
    border-bottom: 4px solid #2563eb;
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-align: center;
}

/* KPI */
.metric-card {
    background: white !important;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    padding: 20px;
    text-align: center;
}

.metric-title {
    color: #64748b !important;
    font-weight: 600;
    font-size: 16px;
}

.metric-value {
    color: #2563eb !important;
    font-size: 32px;
    font-weight: 800;
}

/* Formulaires */
div[data-testid="stForm"], div.stExpander {
    background: #ffffff !important;
    border-radius: 18px !important;
    border: 1px solid #e5e7eb !important;
    padding: 20px !important;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# UTILISATEURS
# =========================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# CONNEXION
# =========================
if not st.session_state.logged_in:

    st.markdown("""
    <div style="text-align:center; padding-top:40px; padding-bottom:30px;">
        <h1 style="color:#0f172a; font-size:42px; font-weight:800;">☀️ PropMed ERP</h1>
        <p style="color:#64748b; font-size:18px;">Système de Gestion & Générateur de Devis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        with st.form("login_form"):

            st.markdown("### 🔐 Connexion")

            utilisateur = st.text_input("Utilisateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")

            if st.form_submit_button("Se connecter", use_container_width=True):
                if utilisateur in USERS and USERS[utilisateur] == mot_de_passe:
                    st.session_state.logged_in = True
                    st.session_state.user = utilisateur
                    st.rerun()
                else:
                    st.error("❌ Erreur de connexion")

    st.stop()

# =========================
# NAVIGATION
# =========================
st.sidebar.markdown(f"""
👤 Bienvenue, {st.session_state.user}
""")

page = st.sidebar.radio(
    "Navigation 📋",
    ["Gestion Inventaire 📦", "Générateur de Devis 📄"]
)

st.sidebar.markdown("---")

if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# CHARGEMENT DONNÉES
# =========================
FILE_NAME = "Inventaire.xlsx"

def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_excel(FILE_NAME)
    return pd.DataFrame()

df_raw = load_data()

# =========================================================
# PAGE 1: INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":

    st.markdown("<h1 class='main-title'>📦 Gestion de l’Inventaire & Clients</h1>", unsafe_allow_html=True)

    st.sidebar.subheader("🔍 Filtres")
    clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist()) if not df_raw.empty else ["Tous"]

    client_select = st.sidebar.selectbox("Filtrer par client", clients)

    df_display = df_raw.copy()
    if client_select != "Tous" and not df_raw.empty:
        df_display = df_display[df_display["Client"] == client_select]

    # KPI
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Clients</div><div class='metric-value'>{df_raw['Client'].nunique() if not df_raw.empty else 0}</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Articles</div><div class='metric-value'>{len(df_raw)}</div></div>", unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Stock</div><div class='metric-value'>{0 if df_raw.empty else df_raw.get('Quantity in Inventory', pd.Series([0])).sum()}</div></div>", unsafe_allow_html=True)

    st.dataframe(df_display, use_container_width=True)

# =========================================================
# PAGE 2: DEVIS
# =========================================================
elif page == "Générateur de Devis 📄":

    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)

    st.session_state.devis_no = st.text_input("Numéro de devis", "0001")
    client = st.text_input("Nom du client", "Client")

    st.info("Ajout des articles ici")

    st.success(f"Devis en cours pour: {client}")
