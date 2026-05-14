import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="PropMed ERP & Devis ☀️",
    layout="wide",
    page_icon="☀️"
)

# =========================================================
# 🎨 DESIGN PREMIUM (SIDEBAR SOMBRE & KPI CENTRÉS)
# =========================================================
st.markdown("""
<style>

/* Fond général */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar : Dark Mode Fix */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Correction des Filtres (Fond sombre pour que le texte blanc soit visible) */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Titres */
.main-title {
    color: #0f172a !important;
    font-size: 34px;
    font-weight: 800;
    border-bottom: 4px solid #2563eb;
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-align: center;
}

/* Cartes KPI (Nombres centrés au milieu) */
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

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: none !important;
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

    c1, c2, c3 = st.columns([1,1,1])
    with c2:
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
# GESTION DES DONNÉES
# =========================================================
FILE_NAME = "Inventaire.xlsx"

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME, engine='openpyxl')
            if "Client" not in df.columns: df.insert(0, "Client", "Inconnu")
            cols = ["Quantity Ordered", "Quantity Used", "Stock"]
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame(columns=["Client", "Shipment No.", "Description", "Quantity Ordered", "Quantity Used", "Stock"])

def save_data(df):
    df["Stock"] = df["Quantity Ordered"] - df["Quantity Used"]
    df.to_excel(FILE_NAME, index=False, engine='openpyxl')
    st.success("✅ Sauvegardé avec succès !")

df_raw = load_data()

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
# FENÊTRE 1: GESTION INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":
    st.sidebar.subheader("🔍 Filtres")
    all_clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    selected_client = st.sidebar.selectbox("Filtrer par Client 👤", all_clients)

    df_display = df_raw.copy()
    if selected_client != "Tous":
        df_display = df_display[df_display["Client"] == selected_client]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire</h1>", unsafe_allow_html=True)

    # KPIs centrés
    ck1, ck2, ck3 = st.columns(3)
    ck1.markdown(f'<div class="metric-card"><div class="metric-title">Clients</div><div class="metric-value">{df_raw["Client"].nunique()}</div></div>', unsafe_allow_html=True)
    ck2.markdown(f'<div class="metric-card"><div class="metric-title">Articles</div><div class="metric-value">{len(df_raw)}</div></div>', unsafe_allow_html=True)
    total_stock = int(df_raw['Stock'].sum()) if not df_raw.empty else 0
    ck3.markdown(f'<div class="metric-card"><div class="metric-title">Total Stock</div><div class="metric-value">{total_stock}</div></div>', unsafe_allow_html=True)

    with st.expander("➕ Ajouter un nouvel article"):
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            n_cli = c1.text_input("Nom du Client")
            n_ship = c2.text_input("Shipment No.")
            n_desc = c3.text_input("Description")
            c4, c5 = st.columns(2)
            n_q = c4.number_input("Quantité Commandée", min_value=0)
            n_u = c5.number_input("Quantité Utilisée", min_value=0)
            if st.form_submit_button("Ajouter à l'inventaire"):
                new_row = {"Client": n_cli, "Shipment No.": n_ship, "Description": n_desc, "Quantity Ordered": n_q, "Quantity Used": n_u}
                df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_raw)
                st.rerun()

    st.info(f"📍 {len(df_display)} lignes trouvées.")
    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Sauvegarder les modifications", use_container_width=True):
        if selected_client == "Tous":
            save_data(edited_df)
        else:
            final_df = pd.concat([df_raw[df_raw["Client"] != selected_client], edited_df], ignore_index=True)
            save_data(final_df)
        st.rerun()

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS
# =========================================================
elif page == "Générateur de Devis 📄":
    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)
    
    if 'devis_items' not in st.session_state:
        st.session_state.devis_items = []

    st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #e5e7eb; margin-bottom:20px;">', unsafe_allow_html=True)
    
    # --- CHOIX DU CLIENT (EXISTANT OU NOUVEAU) ---
    clients_existants = sorted(df_raw["Client"].unique().astype(str).tolist())
    options = clients_existants + ["➕ Nouveau Client (Ajouter manuellement)"]
    choix_cli = st.selectbox("Sélectionner le Client", options)

    if choix_cli == "➕ Nouveau Client (Ajouter manuellement)":
        client_final = st.text_input("Saisir le nom du client")
    else:
        client_final = choix_cli
    st.markdown('</div>', unsafe_allow_html=True)

    # Ajout d'articles
    with st.expander("📝 Ajouter un article au devis", expanded=True):
        col1, col2, col3 = st.columns([2,1,1])
        art_desc = col1.text_input("Désignation")
        art_pu = col2.number_input("Prix Unitaire (MAD)", min_value=0.0)
        art_qte = col3.number_input("Quantité", min_value=1, value=1)
        
        if st.button("➕ Ajouter au Devis"):
            st.session_state.devis_items.append({
                "Description": art_desc,
                "PU HT": art_pu,
                "Qte": art_qte,
                "Total HT": art_pu * art_qte
            })
            st.rerun()

    if st.session_state.devis_items:
        df_devis = pd.DataFrame(st.session_state.devis_items)
        st.table(df_devis)
        
        total_ht = df_devis["Total HT"].sum()
        total_ttc = total_ht * 1.2

        c_ht, c_ttc = st.columns(2)
        c_ht.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL HT</div><div class="metric-value">{total_ht:,.2f} MAD</div></div>', unsafe_allow_html=True)
        c_ttc.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL TTC</div><div class="metric-value">{total_ttc:,.2f} MAD</div></div>', unsafe_allow_html=True)

        colf1, colf2 = st.columns(2)
        if colf1.button("📄 Générer Devis PDF", use_container_width=True):
            st.success(f"PDF généré pour {client_final}")
        if colf2.button("🗑️ Vider le panier", use_container_width=True):
            st.session_state.devis_items = []
            st.rerun()
