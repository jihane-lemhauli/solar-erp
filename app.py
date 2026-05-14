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
# 🎨 DESIGN PREMIUM MODERNE (FIXED)
# =========================================================
st.markdown("""
<style>
/* Background General */
.stApp {
    background: linear-gradient(135deg, #f1f5f9, #e2e8f0) !important;
}

/* Sidebar Fix (L-lawn l-ghameq w hiyad l-byad mn l-filters) */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    background-image: none !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Fix Inputs f Sidebar (Bach maybqaosh baydin) */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Main Titles */
.main-title {
    color: #0f172a !important;
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    padding-bottom: 20px;
}

/* KPI CARDS (Centered Numbers) */
.metric-card {
    background: white !important;
    border-radius: 18px;
    padding: 25px;
    text-align: center; /* Centrage des nombres */
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
}

.metric-title {
    color: #64748b !important;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.metric-value {
    color: #2563eb !important;
    font-size: 36px;
    font-weight: 900;
}

/* Dataframe Styling */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
    background-color: white !important;
    border-radius: 15px !important;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* Forms & Expanders */
div[data-testid="stForm"], div.stExpander {
    background: white !important;
    border-radius: 15px !important;
    border: 1px solid #e2e8f0 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
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
    st.markdown("<div style='text-align:center; padding-top:50px;'><h1>☀️ PropMed ERP</h1><p>Veuillez vous connecter</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        with st.form("login_form"):
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
st.sidebar.markdown("<h1 style='text-align:center;'>☀️ PropMed</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='text-align:center; padding:10px; background:#1e293b; border-radius:10px;'>👤 {st.session_state.user}</div>", unsafe_allow_html=True)
st.sidebar.write("")

page = st.sidebar.radio("Navigation 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])

if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# FENÊTRE 1: GESTION INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":
    FILE_NAME = "Inventaire.xlsx"

    def calculate_metrics(df_to_calc):
        if df_to_calc is None or df_to_calc.empty: return df_to_calc
        cols = ["Quantity Ordered", "Quantity Used", "Quantity in Inventory"]
        for col in cols:
            if col in df_to_calc.columns:
                df_to_calc[col] = pd.to_numeric(df_to_calc[col], errors="coerce").fillna(0)
        if "Quantity Ordered" in df_to_calc.columns and "Quantity Used" in df_to_calc.columns:
            df_to_calc["Quantity in Inventory"] = df_to_calc["Quantity Ordered"] - df_to_calc["Quantity Used"]
        return df_to_calc

    def load_data():
        if os.path.exists(FILE_NAME):
            try:
                df = pd.read_excel(FILE_NAME, engine='openpyxl')
                if "Client" not in df.columns: df.insert(0, "Client", "Client Inconnu")
                return calculate_metrics(df)
            except: return pd.DataFrame()
        return pd.DataFrame(columns=["Client", "Shipment No.", "Item Ref", "Item No.", "Description", "Quantity Ordered", "Quantity Used", "Quantity in Inventory", "Unit", "Status"])

    def save_data(df_to_save):
        df_final = calculate_metrics(df_to_save)
        df_final.to_excel(FILE_NAME, index=False, engine='openpyxl')
        st.success("✅ Sauvegardé !")

    df_raw = load_data()

    # FILTRES SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtres")
    clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    sel_client = st.sidebar.selectbox("Filtrer par Client", clients)
    
    df_display = df_raw.copy()
    if sel_client != "Tous":
        df_display = df_display[df_display["Client"] == sel_client]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire</h1>", unsafe_allow_html=True)

    # KPI CARDS
    ck1, ck2, ck3 = st.columns(3)
    ck1.markdown(f"<div class='metric-card'><div class='metric-title'>Clients</div><div class='metric-value'>{df_raw['Client'].nunique()}</div></div>", unsafe_allow_html=True)
    ck2.markdown(f"<div class='metric-card'><div class='metric-title'>Articles</div><div class='metric-value'>{len(df_raw)}</div></div>", unsafe_allow_html=True)
    stock_total = int(df_raw['Quantity in Inventory'].sum()) if not df_raw.empty else 0
    ck3.markdown(f"<div class='metric-card'><div class='metric-title'>En Stock</div><div class='metric-value'>{stock_total}</div></div>", unsafe_allow_html=True)

    with st.expander("➕ Ajouter une ligne"):
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            n_cli = c1.text_input("Client")
            n_ship = c2.text_input("Shipment No.")
            n_desc = c3.text_input("Description")
            c4, c5 = st.columns(2)
            n_q = c4.number_input("Quantité Commandée", min_value=0)
            n_u = c5.number_input("Quantité Utilisée", min_value=0)
            if st.form_submit_button("Ajouter"):
                new_row = {"Client": n_cli, "Shipment No.": n_ship, "Description": n_desc, "Quantity Ordered": n_q, "Quantity Used": n_u}
                df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_raw)
                st.rerun()

    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True)
    
    colb1, colb2 = st.columns(2)
    if colb1.button("💾 Sauvegarder modifications", use_container_width=True):
        save_data(edited_df if sel_client == "Tous" else pd.concat([df_raw[df_raw["Client"] != sel_client], edited_df]))
        st.rerun()
    
    if os.path.exists(FILE_NAME):
        colb2.download_button("📥 Télécharger Excel", data=open(FILE_NAME, "rb"), file_name=FILE_NAME, use_container_width=True)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (Simplifié pour l'exemple)
# =========================================================
elif page == "Générateur de Devis 📄":
    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)
    st.info("Interface de devis active. Ajoutez vos articles ci-dessous.")
    # Logique de devis (kifma kant 3ndk...)
