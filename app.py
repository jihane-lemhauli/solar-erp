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
# 🎨 DESIGN PREMIUM MODERNE (FIXED FILTERS & ALIGNMENT)
# =========================================================
st.markdown("""
<style>

/* Background General */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
}

/* =====================================================
   SIDEBAR FIX (L-lawn l-ghameq f les inputs)
===================================================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

/* Hada houwa l-fix dyal dik l-byad f les filtres */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important; /* Lawn ghameq bach tban ktaba bayda */
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
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

/* KPI CARDS (Centrage des nombres) */
.metric-card {
    background: white !important;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    padding: 20px;
    text-align: center; /* Nombres au milieu */
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

/* Inputs lli f wast l'page (mashi sidebar) khalihom byadin */
div[data-testid="stForm"] input, .stTextInput input {
    background-color: white !important;
    color: #0f172a !important;
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

    # --- FILTRES SIDEBAR (FIXED STYLE) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtres")
    all_clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    selected_client = st.sidebar.selectbox("Filtrer par Client 👤", all_clients)

    all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist() if pd.notna(x)])
    selected_id = st.sidebar.selectbox("Shipment No. (ID)", all_ids)

    df_display = df_raw.copy()
    if selected_client != "Tous": df_display = df_display[df_display["Client"] == selected_client]
    if selected_id != "Tous": df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire & Clients</h1>", unsafe_allow_html=True)

    # KPI DESIGN (CENTRED NUMBERS)
    colk1, colk2, colk3 = st.columns(3)
    with colk1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Clients</div><div class="metric-value">{df_raw["Client"].nunique()}</div></div>', unsafe_allow_html=True)
    with colk2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Articles</div><div class="metric-value">{len(df_raw)}</div></div>', unsafe_allow_html=True)
    with colk3:
        stock_val = int(df_raw['Quantity in Inventory'].sum()) if not df_raw.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-title">En Stock</div><div class="metric-value">{stock_val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("➕ Ajouter une ligne"):
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            new_client = c1.text_input("Nom du Client")
            new_ship = c2.text_input("Shipment No.")
            new_desc = c3.text_input("Description Article")
            if st.form_submit_button("Ajouter"):
                new_row = {"Client": new_client, "Shipment No.": new_ship, "Description": new_desc}
                df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_raw)
                st.rerun()

    st.info(f"📍 {len(df_display)} lignes trouvées.")
    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Sauvegarder les modifications", use_container_width=True):
        save_data(edited_df if selected_client == "Tous" else pd.concat([df_raw[df_raw["Client"] != selected_client], edited_df]))
        st.rerun()

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (Simplifié)
# =========================================================
elif page == "Générateur de Devis 📄":
    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)
    st.info("Interface de devis active.")

if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()
