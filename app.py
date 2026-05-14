import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. إعدادات الصفحة العامة ---
st.set_page_config(page_title="PropMed ERP & Devis ☀️", layout="wide", page_icon="☀️")

# =========================================================
# 🎨 DESIGN & CSS CUSTOM (PropMed Style)
# =========================================================
st.markdown("""
<style>
    .stApp {
        background-color: #f0f4f8;
    }
    [data-testid="stSidebar"] {
        background-color: #1a4e8a;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .main-title {
        color: #1a4e8a;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
        text-align: center;
        padding: 10px;
    }
    .stButton>button {
        background-color: #1a4e8a;
        color: white;
        border-radius: 5px;
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
    st.markdown("<h1 class='main-title'>🔐 Connexion ERP PropMed</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        u = st.text_input("Utilisateur")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
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
st.sidebar.title("☀️ PropMed ERP")
st.sidebar.write(f"👤 **Bienvenue, {st.session_state.user}**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Menu 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])

if st.sidebar.button("Déconnexion 🚪"):
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
    # Filtre par Client (جديد)
    all_clients = ["Tous"] + sorted(df_raw["Client"].unique().astype(str).tolist())
    selected_client = st.sidebar.selectbox("Filtrer par Client 👤", all_clients)
    
    # Filtre par Shipment
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

    if st.button("💾 Sauvegarder les modifications du tableau"):
        if selected_client == "Tous" and selected_id == "Tous":
            final_df = edited_df
        else:
            df_not_in_view = df_raw.drop(df_display.index)
            final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
        save_data(final_df)
        st.rerun()

    st.download_button("📥 Télécharger Backup Excel", data=open(FILE_NAME, "rb"), file_name=FILE_NAME)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (Bla ma nbdlo fiha walo)
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
    
    # Formulaire Devis
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

        if st.button("📄 Générer le PDF"):
            # (Logique PDF dialk li knt 3ndk...)
            st.success("PDF Généré (Simulation)")

        if st.button("🗑️ Vider"):
            st.session_state.devis_items = []
            st.rerun()
