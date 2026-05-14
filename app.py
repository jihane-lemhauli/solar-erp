import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. Configuration ---
st.set_page_config(page_title="PropMed ERP ☀️", layout="wide", page_icon="☀️")

# =========================================================
# 🎨 DESIGN & CSS PROFESSIONNEL (Clair & Lisible)
# =========================================================
st.markdown("""
<style>
    /* Khalfia dial l-app kamla (Gris très clair) */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Sidebar (Design pro - Bleu Marine) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Kataba f Sidebar t-welli l-ka7la bach t-ban mzyan */
    [data-testid="stSidebar"] * {
        color: #2c3e50 !important;
    }

    /* Titre principal */
    .main-title {
        color: #1a4e8a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        text-align: left;
        padding-bottom: 20px;
        border-bottom: 2px solid #1a4e8a;
    }

    /* Cards (Container dial l-inventaire) */
    div.stExpander, div[data-testid="stForm"] {
        background-color: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #eee !important;
    }

    /* Buttons Style */
    .stButton>button {
        background-color: #1a4e8a !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #12345d !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }

    /* Metrics & Text */
    .stMarkdown p {
        font-size: 15px !important;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# UTILISATEURS & CONNEXION
# =========================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#1a4e8a;'>PropMed ERP 🔐</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("Login"):
            u = st.text_input("Utilisateur")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter", use_container_width=True):
                if u in USERS and USERS[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3222/3222800.png", width=80) # Icon solaire simple
st.sidebar.markdown(f"### Bienvenue, **{st.session_state.user}** 👋")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])

st.sidebar.markdown("---")
if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# GESTION INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":
    FILE_NAME = "Inventaire.xlsx"

    def load_data():
        if os.path.exists(FILE_NAME):
            df = pd.read_excel(FILE_NAME)
            if "Client" not in df.columns: df.insert(0, "Client", "Inconnu")
            return df
        return pd.DataFrame(columns=["Client", "Shipment No.", "Description", "Quantity Ordered", "Quantity Used"])

    df_raw = load_data()

    st.markdown("<h1 class='main-title'>📦 Tableau de Bord Inventaire</h1>", unsafe_allow_html=True)

    # --- FILTRES ---
    c1, c2 = st.columns(2)
    with c1:
        client_list = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
        sel_client = st.selectbox("👤 Filtrer par Client", client_list)
    with c2:
        ship_list = ["Tous"] + sorted(df_raw["Shipment No."].unique().astype(str).tolist())
        sel_ship = st.selectbox("🚢 Filtrer par Shipment No.", ship_list)

    # Filtrage
    df_display = df_raw.copy()
    if sel_client != "Tous": df_display = df_display[df_display["Client"] == sel_client]
    if sel_ship != "Tous": df_display = df_display[df_display["Shipment No."].astype(str) == sel_ship]

    # --- AJOUT ---
    with st.expander("➕ Ajouter une nouvelle entrée"):
        with st.form("new_entry"):
            ca, cb, cc = st.columns(3)
            n_cli = ca.text_input("Nom Client")
            n_ship = cb.text_input("Shipment No.")
            n_desc = cc.text_input("Description")
            if st.form_submit_button("Ajouter à la liste"):
                new_row = pd.DataFrame([{"Client": n_cli, "Shipment No.": n_ship, "Description": n_desc}])
                df_raw = pd.concat([df_raw, new_row], ignore_index=True)
                df_raw.to_excel(FILE_NAME, index=False)
                st.rerun()

    # --- TABLEAU ---
    st.write(f"📊 **{len(df_display)}** résultats trouvés")
    st.data_editor(df_display, use_container_width=True, num_rows="dynamic")

# =========================================================
# DEVIS (Baqi kima hwa bla ma n-qissou)
# =========================================================
elif page == "Générateur de Devis 📄":
    st.markdown("<h1 class='main-title'>📄 Générateur de Devis</h1>", unsafe_allow_html=True)
    st.write("Section Devis active...")
    # ... L-code dial l-devis dyalk hna ...
