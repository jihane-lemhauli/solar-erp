import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import date

# ==========================================
# 1. Configuration de la page
# ==========================================
st.set_page_config(page_title="PropMed ERP", layout="wide", page_icon="☀️")

# Header design
st.markdown("""
    <style>
    .main-header {
        background-color: #1a4e8a;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. Système de connexion
# ==========================================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-header"><h1>🔐 Connexion - PropMed ERP</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("Nom d'utilisateur")
        p = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect")

    st.stop()

# ==========================================
# 3. Fonctions (Inventaire & PDF)
# ==========================================

def load_inventory(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)

        if "Quantity Ordered" in df.columns and "Quantity Used" in df.columns:
            df["Quantity in Inventory"] = df["Quantity Ordered"].fillna(0) - df["Quantity Used"].fillna(0)

        return df
    return pd.DataFrame()

class PropMedPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 22)
        self.set_text_color(26, 78, 138)
        self.text(10, 22, "PropMed")

        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        self.text(10, 28, "Solutions Solaires - Tanger, Maroc")

        self.set_fill_color(26, 78, 138)
        self.rect(110, 10, 90, 25, 'F')

        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.set_xy(110, 15)
        self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '')}", 0, 1, 'C')

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "PropMed SARL | Tanger | RC: 137001 | IF: 53625661", 0, 0, 'C')

# ==========================================
# 4. Navigation
# ==========================================
st.sidebar.markdown(f"### 👤 Connecté : {st.session_state.user.upper()}")

choice = st.sidebar.radio("Menu principal 📋", ["📊 Tableau de bord & Stock", "📄 Créer un Devis"])

if st.sidebar.button("Se déconnecter 🚪"):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# 5. Interface Stock
# ==========================================
if choice == "📊 Tableau de bord & Stock":
    st.markdown('<div class="main-header"><h1>📦 Gestion du stock</h1></div>', unsafe_allow_html=True)

    file_inv = "PropMed Inventory (1) (3).xlsx"
    df_inv = load_inventory(file_inv)

    if not df_inv.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total commandé", int(df_inv["Quantity Ordered"].sum()))
        c2.metric("Total utilisé", int(df_inv["Quantity Used"].sum()))
        c3.metric("Stock disponible", int(df_inv["Quantity in Inventory"].sum()))

        st.divider()
        st.subheader("📝 Modifier le stock")

        edited_df = st.data_editor(df_inv, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Enregistrer dans Excel"):
            edited_df.to_excel(file_inv, index=False)
            st.success("✅ Fichier Excel mis à jour avec succès !")
    else:
        st.warning("⚠️ Fichier stock introuvable ou vide.")

# ==========================================
# 6. Interface Devis
# ==========================================
elif choice == "📄 Créer un Devis":
    st.markdown('<div class="main-header"><h1>📄 Nouveau Devis</h1></div>', unsafe_allow_html=True)

    if 'items_list' not in st.session_state:
        st.session_state.items_list = []

    with st.expander("📝 Informations client", expanded=True):
        col_a, col_b = st.columns(2)
        st.session_state.devis_no = col_a.text_input("N° Devis", "042110")
        client = col_b.text_input("Nom du client", "Jihane")

    st.subheader("🛒 Ajouter des articles")

    try:
        base_art = pd.read_excel("Classeur1.xlsx", sheet_name="lista_items")

        selected_art = st.selectbox("Choisir un article", base_art['Code article'].unique())
        qte_art = st.number_input("Quantité", min_value=1, value=1)

        if st.button("➕ Ajouter"):
            row = base_art[base_art['Code article'] == selected_art].iloc[0]

            st.session_state.items_list.append({
                "Code": selected_art,
                "Désignation": row['Désignation'],
                "Quantité": qte_art,
                "P.U HT": row['P.U. HT (MAD)'],
                "Total": qte_art * row['P.U. HT (MAD)']
            })
            st.rerun()

    except:
        st.error("❌ Fichier 'Classeur1.xlsx' introuvable.")

    if st.session_state.items_list:
        df_temp = pd.DataFrame(st.session_state.items_list)
        st.table(df_temp)

        if st.button("🗑️ Vider la liste"):
            st.session_state.items_list = []
            st.rerun()

        if st.button("📄 Télécharger le PDF"):
            pdf = PropMedPDF()
            pdf.add_page()

            pdf.set_font("Arial", size=12)
            pdf.ln(40)
            pdf.cell(0, 10, f"Client : {client}", 0, 1)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')

            st.download_button(
                "📥 Télécharger maintenant",
                data=pdf_bytes,
                file_name=f"Devis_{client}.pdf"
            )
