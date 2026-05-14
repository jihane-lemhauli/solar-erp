import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. Configuration ---
st.set_page_config(page_title="PropMed ERP ☀️", layout="wide", page_icon="☀️")

# =========================================================
# 🎨 DESIGN & CSS PROFESSIONNEL (Had l-theme li 3jbak)
# =========================================================
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #2c3e50 !important; }
    .main-title {
        color: #1a4e8a;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        text-align: left;
        padding-bottom: 20px;
        border-bottom: 2px solid #1a4e8a;
        margin-bottom: 20px;
    }
    div.stExpander, div[data-testid="stForm"] {
        background-color: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #eee !important;
    }
    .stButton>button {
        background-color: #1a4e8a !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #12345d !important; }
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
                else: st.error("❌ Identifiants incorrects")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown(f"### Bienvenue, **{st.session_state.user}** 👋")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])
st.sidebar.markdown("---")
if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# FENÊTRE 1: GESTION INVENTAIRE
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

    c1, c2 = st.columns(2)
    with c1:
        client_list = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
        sel_client = st.selectbox("👤 Filtrer par Client", client_list)
    with c2:
        ship_list = ["Tous"] + sorted(df_raw["Shipment No."].unique().astype(str).tolist())
        sel_ship = st.selectbox("🚢 Filtrer par Shipment No.", ship_list)

    df_display = df_raw.copy()
    if sel_client != "Tous": df_display = df_display[df_display["Client"] == sel_client]
    if sel_ship != "Tous": df_display = df_display[df_display["Shipment No."].astype(str) == sel_ship]

    with st.expander("➕ Ajouter une nouvelle entrée"):
        with st.form("new_entry"):
            ca, cb, cc = st.columns(3)
            n_cli = ca.text_input("Nom Client")
            n_ship = cb.text_input("Shipment No.")
            n_desc = cc.text_input("Description")
            if st.form_submit_button("Ajouter"):
                new_row = pd.DataFrame([{"Client": n_cli, "Shipment No.": n_ship, "Description": n_desc}])
                df_raw = pd.concat([df_raw, new_row], ignore_index=True)
                df_raw.to_excel(FILE_NAME, index=False)
                st.rerun()

    st.write(f"📊 **{len(df_display)}** résultats")
    st.data_editor(df_display, use_container_width=True, num_rows="dynamic")

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (M-sawab m3a l-theme jdid)
# =========================================================
elif page == "Générateur de Devis 📄":
    CLIENTS_FILE = "Clients.xlsx"
    
    def load_clients():
        if os.path.exists(CLIENTS_FILE):
            return pd.read_excel(CLIENTS_FILE)["Nom"].tolist()
        return ["Client de passage", "BYD Casablanca"]

    def save_new_client(new_name):
        existing = load_clients()
        if new_name and new_name not in existing:
            existing.append(new_name)
            pd.DataFrame({"Nom": existing}).to_excel(CLIENTS_FILE, index=False)
            return True
        return False

    try:
        df_base = pd.read_excel("Clas.xlsx", sheet_name="lista_items")
    except:
        df_base = pd.DataFrame(columns=['Code article', 'Désignation', 'P.U. HT (MAD)'])

    # --- CLASSE PDF ---
    class PropMedPDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 22); self.set_text_color(26, 78, 138)
            self.text(10, 22, "PropMed")
            self.set_font('Arial', '', 9); self.set_text_color(100, 100, 100)
            self.text(10, 28, "Solar Solutions - Tanger, Maroc")
            self.set_fill_color(26, 78, 138); self.rect(110, 10, 90, 25, 'F')
            self.set_text_color(255, 255, 255); self.set_font('Arial', 'B', 16)
            self.set_xy(110, 15); self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '---')}", 0, 1, 'C')

        def footer(self):
            self.set_y(-20); self.set_font('Arial', 'I', 8); self.set_text_color(150, 150, 150)
            self.cell(0, 10, "PropMed SARL | Tanger | ICE: 003241314000056", 0, 0, 'C')

    if 'devis_items' not in st.session_state: st.session_state.devis_items = []

    st.markdown("<h1 class='main-title'>📄 Générateur de Devis</h1>", unsafe_allow_html=True)
    
    # --- Infos Client ---
    with st.container():
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            client_name = st.selectbox("Sélectionner le Client", load_clients())
        with col_c2:
            new_c = st.text_input("➕ Nouveau Client")
            if st.button("Enregistrer Client"):
                if save_new_client(new_c): st.rerun()

        st.session_state.devis_no = st.text_input("N° Devis", "042110")
        modalites_paie = st.text_area("Modalités de paiement", "50 % à la commande / 50 % à la mise en service")

    st.divider()
    
    # --- Gestion Articles ---
    mode_ajout = st.radio("Mode d'ajout :", ["Sélectionner depuis la base", "Saisie manuelle"])
    if mode_ajout == "Sélectionner depuis la base" and not df_base.empty:
        code_sel = st.selectbox("Sélectionner un article", df_base['Code article'].unique())
        qte_sel = st.number_input("Quantité", min_value=1, value=1)
        if st.button("➕ Ajouter l'article"):
            row = df_base[df_base['Code article'] == code_sel].iloc[0]
            st.session_state.devis_items.append({
                "Code": code_sel, "Désignation": row['Désignation'], "Quantité": qte_sel,
                "P.U. HT": row['P.U. HT (MAD)'], "Montant HT": qte_sel * row['P.U. HT (MAD)']
            })
            st.rerun()
    elif mode_ajout == "Saisie manuelle":
        m_desc = st.text_input("Désignation")
        m_pu = st.number_input("Prix HT", min_value=0.0)
        m_qte = st.number_input("Qte", min_value=1)
        if st.button("➕ Ajouter manuel"):
            st.session_state.devis_items.append({
                "Code": "MANUAL", "Désignation": m_desc, "Quantité": m_qte, 
                "P.U. HT": m_pu, "Montant HT": m_qte * m_pu
            })
            st.rerun()

    if st.session_state.devis_items:
        df_curr = pd.DataFrame(st.session_state.devis_items)
        edited = st.data_editor(df_curr, use_container_width=True)
        total_ht = edited['Montant HT'].sum()
        
        if st.button("📄 Générer PDF"):
            pdf = PropMedPDF(); pdf.add_page(); pdf.set_y(40)
            pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, f"Client: {client_name}", 0, 1)
            # (Ba9i l-logic dial PDF dialk...)
            st.success("✅ PDF Prêt!")
