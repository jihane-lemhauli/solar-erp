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
# 🎨 DESIGN PREMIUM MODERNE (FIXED SIDEBAR FILTERS)
# =========================================================
st.markdown("""
<style>

/* Background General */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar Fix (Dark background and clear text) */
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

/* KPI CARDS (Centrage des nombres) */
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

/* Formulaires et Boutons */
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
# FENÊTRE 1: GESTION INVENTAIRE
# =========================================================
FILE_NAME = "Inventaire.xlsx"

def calculate_metrics(df_to_calc):
    if df_to_calc is None or df_to_calc.empty: return df_to_calc
    cols_to_fix = ["Quantity Ordered", "Quantity Used", "Quantity in Inventory"]
    for col in cols_to_fix:
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
            if "Status" not in df.columns: df["Status"] = "En attente"
            return calculate_metrics(df)
        except: return pd.DataFrame()
    else:
        columns = ["Client", "Shipment No.", "Item Ref", "Item No.", "Description", "Quantity Ordered", "Quantity Used", "Quantity in Inventory", "Unit", "Status"]
        return pd.DataFrame(columns=columns)

def save_data(df_to_save):
    df_final_save = calculate_metrics(df_to_save)
    df_final_save.to_excel(FILE_NAME, index=False, engine='openpyxl')
    st.success(f"✅ Sauvegardé !")

df_raw = load_data()

if page == "Gestion Inventaire 📦":
    # --- FILTRES ---
    st.sidebar.subheader("🔍 Filtres")
    all_clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    selected_client = st.sidebar.selectbox("Filtrer par Client 👤", all_clients)

    all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist() if pd.notna(x)])
    selected_id = st.sidebar.selectbox("Shipment No. (ID)", all_ids)

    df_display = df_raw.copy()
    if selected_client != "Tous": df_display = df_display[df_display["Client"] == selected_client]
    if selected_id != "Tous": df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire & Clients</h1>", unsafe_allow_html=True)

    colk1, colk2, colk3 = st.columns(3)
    with colk1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Clients</div><div class="metric-value">{df_raw["Client"].nunique()}</div></div>', unsafe_allow_html=True)
    with colk2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Articles</div><div class="metric-value">{len(df_raw)}</div></div>', unsafe_allow_html=True)
    with colk3:
        stock_val = int(df_raw['Quantity in Inventory'].sum()) if 'Quantity in Inventory' in df_raw.columns else 0
        st.markdown(f'<div class="metric-card"><div class="metric-title">En Stock</div><div class="metric-value">{stock_val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("➕ Ajouter ou Modifier une ligne"):
        with st.form("add_form"):
            c1, c2, c3 = st.columns(3)
            new_client = c1.text_input("Nom du Client")
            new_ship = c2.text_input("Shipment No.")
            new_desc = c3.text_input("Description Article")
            c4, c5, c6 = st.columns(3)
            new_qte = c4.number_input("Quantité Commandée", min_value=0)
            new_used = c5.number_input("Quantité Utilisée", min_value=0)
            new_status = c6.selectbox("Statut", ["En attente", "Livré", "Facturé"])
            if st.form_submit_button("Ajouter à l'inventaire"):
                new_row = {"Client": new_client, "Shipment No.": new_ship, "Description": new_desc, "Quantity Ordered": new_qte, "Quantity Used": new_used, "Status": new_status}
                df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_raw)
                st.rerun()

    st.info(f"📍 {len(df_display)} lignes trouvées.")
    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True, key="main_editor")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Sauvegarder les modifications", use_container_width=True):
            if selected_client == "Tous" and selected_id == "Tous": final_df = edited_df
            else:
                df_not_in_view = df_raw.drop(df_display.index)
                final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
            save_data(final_df)
            st.rerun()
    with col_btn2:
        if os.path.exists(FILE_NAME):
            st.download_button("📥 Télécharger Backup Excel", data=open(FILE_NAME, "rb"), file_name=FILE_NAME, use_container_width=True)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS
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
    
    # --- MODIFICATION ICI : Récupérer les clients existants ---
    clients_existants = sorted(df_raw["Client"].unique().astype(str).tolist())
    
    client_name = st.selectbox(
        "Sélectionner le Client (ou taper son nom)",
        clients_existants
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    mode_ajout = st.radio("Mode d'ajout :", ["Sélectionner depuis la base", "Saisie manuelle"])

    if mode_ajout == "Sélectionner depuis la base":
        if not df_base.empty:
            code_sel = st.selectbox("Sélectionner un article", df_base['Code article'].unique())
            qte_sel = st.number_input("Quantité", min_value=1, value=1)
            if st.button("➕ Ajouter l'article"):
                row = df_base[df_base['Code article'] == code_sel].iloc[0]
                st.session_state.devis_items.append({"Code": code_sel, "Désignation": row['Désignation'], "Quantité": qte_sel, "P.U. HT": row['P.U. HT (MAD)'], "Montant HT": qte_sel * row['P.U. HT (MAD)']})
                st.rerun()
    else:
        m_code = st.text_input("Code Article")
        m_desc = st.text_input("Désignation")
        m_pu = st.number_input("P.U. HT (MAD)", min_value=0.0)
        m_qte = st.number_input("Quantité", min_value=1)
        if st.button("➕ Ajouter manuellement"):
            st.session_state.devis_items.append({"Code": m_code, "Désignation": m_desc, "Quantité": m_qte, "P.U. HT": m_pu, "Montant HT": m_qte * m_pu})
            st.rerun()

    if st.session_state.devis_items:
        df_devis = pd.DataFrame(st.session_state.devis_items)
        edited_devis = st.data_editor(df_devis, use_container_width=True)
        total_ht = edited_devis['Montant HT'].sum()
        total_ttc = total_ht * 1.2

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL HT</div><div class="metric-value">{total_ht:,.2f} MAD</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL TTC</div><div class="metric-value">{total_ttc:,.2f} MAD</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_final1, col_final2 = st.columns(2)
        with col_final1:
            if st.button("📄 Générer le Devis PDF", use_container_width=True):
                st.success(f"Devis PDF pour {client_name} en cours (Simulation)")
        with col_final2:
            if st.button("🗑️ Vider la liste", use_container_width=True):
                st.session_state.devis_items = []
                st.rerun()
