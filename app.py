import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="PropMed ERP & Devis ☀️",
    layout="wide",
    page_icon="☀️"
)

# =========================================================
# 🎨 CSS FINAL (MERGED + FIXED)
# =========================================================
st.markdown("""
<style>

/* ================= GLOBAL ================= */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(to bottom right, #f4f7fb, #eef2f7);
}

/* ================= SIDEBAR ================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Sidebar all text white */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar titles */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: white !important;
}

/* Sidebar radio items */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 6px;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.15);
}

/* ================= TITLES ================= */
.main-title {
    color: #0f172a;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 10px;
    padding-bottom: 12px;
    border-bottom: 4px solid #2563eb;
}

/* ================= CARDS ================= */
.metric-card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    text-align: center;
}

.metric-title {
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
}

/* ================= INPUTS ================= */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 14px !important;
    border: 1px solid #dbe4ee !important;
    padding: 10px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
textarea:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}

/* ================= BUTTONS ================= */
.stButton > button {
    width: 100%;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* download button */
.stDownloadButton > button {
    width: 100%;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important;
}

/* ================= RADIO + LABEL FIX ================= */
.stRadio label,
.stSelectbox label,
.stMultiSelect label,
.stTextInput label,
.stNumberInput label {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* radio options */
[data-baseweb="radio"] div {
    color: #0f172a !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# USERS
# =========================================================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# LOGIN
# =========================================================
if not st.session_state.logged_in:

    st.markdown("""
    <div style="text-align:center;padding-top:50px;">
        <h1>☀️ PropMed ERP</h1>
        <p>Système de gestion</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col2:
        with st.form("login"):
            u = st.text_input("Utilisateur")
            p = st.text_input("Mot de passe", type="password")

            if st.form_submit_button("Connexion"):
                if u in USERS and USERS[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Erreur")

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("☀️ PropMed")
st.sidebar.write(f"👤 {st.session_state.user}")

page = st.sidebar.radio(
    "Navigation",
    ["Gestion Inventaire 📦", "Générateur de Devis 📄"]
)

if st.sidebar.button("Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":

    FILE = "Inventaire.xlsx"

    def load():
        if os.path.exists(FILE):
            return pd.read_excel(FILE)
        return pd.DataFrame(columns=[
            "Client","Shipment No.","Description",
            "Quantity Ordered","Quantity Used",
            "Quantity in Inventory","Status"
        ])

    def save(df):
        df.to_excel(FILE, index=False)
        st.success("Sauvegardé")

    df = load()

    st.markdown("<h1 class='main-title'>📦 Inventaire</h1>", unsafe_allow_html=True)

    st.dataframe(df, use_container_width=True)

    if st.button("💾 Save"):
        save(df)

# =========================================================
# DEVIS
# =========================================================
else:

    st.markdown("<h1 class='main-title'>📄 Devis</h1>", unsafe_allow_html=True)

    if "items" not in st.session_state:
        st.session_state.items = []

    code = st.text_input("Code")
    desc = st.text_input("Désignation")
    pu = st.number_input("PU", 0.0)
    qte = st.number_input("Qté", 1)

    if st.button("Ajouter"):
        st.session_state.items.append({
            "Code": code,
            "Désignation": desc,
            "Quantité": qte,
            "PU": pu,
            "Total": pu*qte
        })
        st.rerun()

    if st.session_state.items:
        dfd = pd.DataFrame(st.session_state.items)
        st.dataframe(dfd)

        st.write("Total:", dfd["Total"].sum())
