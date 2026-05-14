import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. إعدادات الصفحة العامة ---
st.set_page_config(
    page_title="PropMed ERP & Devis ☀️",
    layout="wide",
    page_icon="☀️"
)

# =========================================================
# 🎨 DESIGN PREMIUM MODERNE
# =========================================================
st.markdown("""
<style>
/* Background General */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar Fix */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Fix Inputs f Sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
}

/* Titles */
.main-title {
    color: #0f172a !important;
    font-size: 34px;
    font-weight: 800;
    border-bottom: 4px solid #2563eb;
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-align: center;
}

/* KPI CARDS */
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
    margin-bottom: 10px;
}

.metric-value {
    color: #2563eb !important;
    font-size: 32px;
    font-weight: 800;
}

/* Forms & Buttons */
div[data-testid="stForm"], div.stExpander {
    background: #ffffff !important;
    border-radius: 18px !important;
    border: 1px solid #e5e7eb !important;
    padding: 20px !important;
}

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
            u = st.text_input("Utilisateur")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter", use_container_width=True):
                if u in USERS and USERS[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("❌ Erreur de connexion")
    st.stop()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
st.sidebar.markdown("""
<div style="text-align:center;padding:10px 0 20px 0;">
    <h1 style="color:white;">☀️ PropMed</h1>
    <p style="color:#cbd5e1;">ERP Professionnel</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.08); padding:15px; border-radius:16px; margin-bottom:20px;">
👤 <b>Bienvenue, {st.session_state.user}</b>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])
st.sidebar.markdown("---")

if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# DATA HANDLING
# =========================================================
FILE_NAME = "Inventaire.xlsx"

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME, engine='openpyxl')
            if "Client" not in df.columns: df.insert(0, "Client", "Client Inconnu")
            # Convert numeric columns safely
            cols = ["Quantity Ordered", "Quantity Used", "Quantity in Inventory"]
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame(columns=["Client", "Shipment No.", "Description", "Quantity in Inventory"])

df_raw = load_data()

# =========================================================
# FENÊTRE 1: GESTION INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":
    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire & Clients</h1>", unsafe_allow_html=True)
    # (Logique de l'inventaire kima kanet...)
    st.info("Utilisez le menu à gauche pour naviguer ou modifier vos stocks.")
    st.dataframe(df_raw, use_container_width=True)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (FIXED INPUT)
# =========================================================
elif page == "Générateur de Devis 📄":
    try:
        df_base = pd.read_excel("Clas.xlsx", sheet_name="lista_items")
    except:
        df_base = pd.DataFrame(columns=['Code article', 'Désignation', 'P.U. HT (MAD)'])

    if 'devis_items' not in st.session_state: st.session_state.devis_items = []

    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)

    st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #e5e7eb; margin-bottom:20px; box-shadow:0 4px 20px rgba(0,0,0,0.04);">', unsafe_allow_html=True)
    
    st.session_state.devis_no = st.text_input("N° Devis", "042110")
    
    # --- FIX ICI : Mixte entre Selectbox et Nouveau Client ---
    clients_base = sorted(df_raw["Client"].unique().astype(str).tolist())
    options_clients = clients_base + ["➕ Nouveau Client (Ajouter manuellement)"]
    
    choix_client = st.selectbox(
        "Sélectionner le Client",
        options_clients
    )

    if choix_client == "➕ Nouveau Client (Ajouter manuellement)":
        client_final = st.text_input("Saisir le nom du nouveau client", placeholder="Ex: Solaire Plus SARL")
    else:
        client_final = choix_client

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # Baqi l'code dyal Devis (Articles, Total, PDF...)
    mode_ajout = st.radio("Mode d'ajout :", ["Sélectionner depuis la base", "Saisie manuelle"])

    if mode_ajout == "Sélectionner depuis la base":
        if not df_base.empty:
            code_sel = st.selectbox("Sélectionner un article", df_base['Code article'].unique())
            qte_sel = st.number_input("Quantité", min_value=1, value=1)
            if st.button("➕ Ajouter l'article"):
                row = df_base[df_base['Code article'] == code_sel].iloc[0]
                st.session_state.devis_items.append({
                    "Code": code_sel, 
                    "Désignation": row['Désignation'], 
                    "Quantité": qte_sel, 
                    "P.U. HT": row['P.U. HT (MAD)'], 
                    "Montant HT": qte_sel * row['P.U. HT (MAD)']
                })
                st.rerun()

    if st.session_state.devis_items:
        df_devis = pd.DataFrame(st.session_state.devis_items)
        st.data_editor(df_devis, use_container_width=True)
        
        if st.button("📄 Générer Devis pour: " + str(client_final)):
            st.success(f"Devis PDF généré avec succès pour {client_final} !")
