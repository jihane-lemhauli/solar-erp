import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. إعدادات الصفحة العامة ---
st.set_page_config(page_title="PropMed ERP & Devis ☀️", layout="wide", page_icon="☀️")

# =========================================================
# 🎨 DESIGN & CSS PROFESSIONNEL (Clair & Lisible)
# =========================================================
st.markdown("""
<style>
    /* Khalfia dial l-app (Gris très clair) */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Sidebar (Design Pro - Blanc & Gris) */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Kataba f Sidebar t-welli ka7la bach t-ban mzyan */
    [data-testid="stSidebar"] * {
        color: #2c3e50 !important;
    }

    /* Titre principal (Bleu Marine PropMed) */
    .main-title {
        color: #1a4e8a;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        text-align: left;
        padding-bottom: 15px;
        border-bottom: 2px solid #1a4e8a;
        margin-bottom: 25px;
    }

    /* Card Design pour les formulaires */
    div.stExpander, div[data-testid="stForm"] {
        background-color: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: 1px solid #eee !important;
        padding: 15px;
    }

    /* Buttons Style */
    .stButton>button {
        background-color: #1a4e8a !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #12345d !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }

    /* Input focus color */
    input:focus {
        border-color: #1a4e8a !important;
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
    st.markdown("<h1 class='main-title' style='text-align:center;'>🔐 Connexion ERP PropMed</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
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
st.sidebar.markdown(f"### ☀️ PropMed ERP")
st.sidebar.write(f"👤 **Bienvenue, {st.session_state.user}**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Menu 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])

st.sidebar.markdown("---")
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
        st.success(f"✅ Sauvegardé dans '{FILE_NAME}' !")

    df_raw = load_data()

    # --- FILTRES (Sidebar) ---
    st.sidebar.subheader("🔍 Filtres")
    all_clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    selected_client = st.sidebar.selectbox("Filtrer par Client 👤", all_clients)
    
    all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist() if pd.notna(x)])
    selected_id = st.sidebar.selectbox("Shipment No. (ID)", all_ids)

    df_display = df_raw.copy()
    if selected_client != "Tous":
        df_display = df_display[df_display["Client"] == selected_client]
    if selected_id != "Tous":
        df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire & Clients</h1>", unsafe_allow_html=True)

    # --- AJOUTER / MODIFIER CLIENT ---
    with st.expander("➕ Ajouter ou Modifier une ligne (Client/Shipment)"):
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
                new_row = {
                    "Client": new_client, "Shipment No.": new_ship, "Description": new_desc,
                    "Quantity Ordered": new_qte, "Quantity Used": new_used, "Status": new_status
                }
                df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_raw)
                st.rerun()

    st.info(f"📍 **{len(df_display)}** lignes trouvées.")
    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True, key="main_editor")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Sauvegarder les modifications", use_container_width=True):
            if selected_client == "Tous" and selected_id == "Tous":
                final_df = edited_df
            else:
                df_not_in_view = df_raw.drop(df_display.index)
                final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
            save_data(final_df)
            st.rerun()

    with col_btn2:
        st.download_button("📥 Télécharger Backup Excel", data=open(FILE_NAME, "rb"), file_name=FILE_NAME, use_container_width=True)

    st.markdown("---")
    st.subheader("🌐 Aperçu global (Base de données)")
    st.dataframe(df_raw, use_container_width=True)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS
# =========================================================
elif page == "Générateur de Devis 📄":
    try:
        df_base = pd.read_excel("Clas.xlsx", sheet_name="lista_items")
    except:
        df_base = pd.DataFrame(columns=['Code article', 'Désignation', 'P.U. HT (MAD)'])

    class PropMedPDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 22); self.set_text_color(26, 78, 138)
            self.text(10, 22, "PropMed")
            self.set_font('Arial', '', 9); self.set_text_color(100, 100, 100)
            self.text(10, 28, "Solar Solutions - Tanger, Maroc")
            self.set_fill_color(26, 78, 138); self.rect(110, 10, 90, 25, 'F')
            self.set_text_color(255, 255, 255); self.set_font('Arial', 'B', 16)
            self.set_xy(110, 15); self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '---')}", 0, 1, 'C')

    if 'devis_items' not in st.session_state: st.session_state.devis_items = []

    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.session_state.devis_no = st.text_input("N° Devis", "042110")
        client_name = st.text_input("Nom du Client", "Client")
        
    st.divider()
    mode_ajout = st.radio("Mode d'ajout :", ["Sélectionner depuis la base", "Saisie manuelle"])

    if mode_ajout == "Sélectionner depuis la base":
        if not df_base.empty:
            code_sel = st.selectbox("Sélectionner un article", df_base['Code article'].unique())
            qte_sel = st.number_input("Quantité", min_value=1, value=1)
            if st.button("➕ Ajouter l'article"):
                row = df_base[df_base['Code article'] == code_sel].iloc[0]
                st.session_state.devis_items.append({
                    "Code": code_sel, "Désignation": row['Désignation'], "Quantité": qte_sel,
                    "P.U. HT": row['P.U. HT (MAD)'], "Montant HT": qte_sel * row['P.U. HT (MAD)']
                })
                st.rerun()
    else:
        m_code = st.text_input("Code Article")
        m_desc = st.text_input("Désignation")
        m_pu = st.number_input("P.U. HT (MAD)", min_value=0.0)
        m_qte = st.number_input("Quantité", min_value=1)
        if st.button("➕ Ajouter manuellement"):
            st.session_state.devis_items.append({
                "Code": m_code, "Désignation": m_desc, "Quantité": m_qte, "P.U. HT": m_pu, "Montant HT": m_qte * m_pu
            })
            st.rerun()

    if st.session_state.devis_items:
        df_devis = pd.DataFrame(st.session_state.devis_items)
        edited_devis = st.data_editor(df_devis, use_container_width=True)
        
        total_ht = edited_devis['Montant HT'].sum()
        total_ttc = total_ht * 1.2

        col_final1, col_final2 = st.columns(2)
        with col_final1:
            if st.button("📄 Générer le Devis PDF", use_container_width=True):
                st.success("PDF Généré (Simulation)")
        with col_final2:
            if st.button("🗑️ Vider la liste", use_container_width=True):
                st.session_state.devis_items = []
                st.rerun()
