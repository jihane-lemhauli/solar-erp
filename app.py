import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. CONFIGURATION GÉNÉRALE DE LA PAGE ---
st.set_page_config(
    page_title="PropMed ERP & Devis ☀️",
    layout="wide",
    page_icon="☀️"
)

# =========================================================
# 🎨 DESIGN PREMIUM MODERNE (FILTRES & ALIGNEMENT FIXÉS)
# =========================================================
st.markdown("""
<style>

/* Fond général */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Inputs sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
}

/* Titre principal */
.main-title {
    color: #0f172a !important;
    font-size: 34px;
    font-weight: 800;
    border-bottom: 4px solid #2563eb;
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-align: center;
}

/* Cartes KPI */
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

/* Formulaires */
div[data-testid="stForm"], div.stExpander {
    background: #ffffff !important;
    border-radius: 18px !important;
    border: 1px solid #e5e7eb !important;
    padding: 20px !important;
}

/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: none !important;
}

/* Bouton Téléchargement (Download) en Vert */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.6rem 1rem !important;
    width: 100% !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

</style>
""", unsafe_allow_html=True)

# =========================
# UTILISATEURS
# =========================
UTILISATEURS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# CONNEXION
# =========================
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center; padding-top:40px; padding-bottom:30px;">
        <h1 style="color:#0f172a; font-size:42px; font-weight:800;">☀️ PropMed ERP</h1>
        <p style="color:#64748b; font-size:18px;">Système de gestion & génération de devis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        with st.form("form_connexion"):
            st.markdown("### 🔐 Connexion")
            utilisateur = st.text_input("Utilisateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")

            if st.form_submit_button("Se connecter", use_container_width=True):
                if utilisateur in UTILISATEURS and UTILISATEURS[utilisateur] == mot_de_passe:
                    st.session_state.logged_in = True
                    st.session_state.user = utilisateur
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")

    st.stop()

# =========================================================
# GESTION DES DONNÉES
# =========================================================
FICHIER = "Inventaire.xlsx"

def calculer_metriques(df):
    if df is None or df.empty:
        return df

    colonnes = ["Quantity Ordered", "Quantity Used", "Quantity in Inventory"]

    for col in colonnes:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "Quantity Ordered" in df.columns and "Quantity Used" in df.columns:
        df["Quantity in Inventory"] = df["Quantity Ordered"] - df["Quantity Used"]

    return df

def charger_donnees():
    if os.path.exists(FICHIER):
        try:
            df = pd.read_excel(FICHIER, engine="openpyxl")
            if "Client" not in df.columns:
                df.insert(0, "Client", "Client inconnu")
            if "Status" not in df.columns:
                df["Status"] = "En attente"
            return calculer_metriques(df)
        except:
            return pd.DataFrame()
    else:
        colonnes = [
            "Client", "Shipment No.", "Item Ref", "Item No.",
            "Description", "Quantity Ordered", "Quantity Used",
            "Quantity in Inventory", "Unit", "Status"
        ]
        return pd.DataFrame(columns=colonnes)

def sauvegarder_donnees(df):
    df_final = calculer_metriques(df)
    df_final.to_excel(FICHIER, index=False, engine="openpyxl")
    st.success("✅ Données sauvegardées avec succès !")

df_brut = charger_donnees()

# =========================================================
# CLASSE GENERATOR PDF (PropMed Style)
# =========================================================
class PropMedPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 22)
        self.set_text_color(26, 78, 138)
        self.text(10, 22, "PropMed")
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        self.text(10, 28, "Solar Solutions - Tanger, Maroc")
        self.set_fill_color(26, 78, 138)
        self.rect(110, 10, 90, 25, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.set_xy(110, 17)
        self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '---')}", 0, 1, 'C')

# =========================================================
# MENU LATÉRAL
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

page = st.sidebar.radio("Navigation", ["Gestion de l’inventaire 📦", "Générateur de devis 📄"])

st.sidebar.markdown("---")

if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# PAGE 1 : INVENTAIRE
# =========================================================
if page == "Gestion de l’inventaire 📦":

    st.sidebar.subheader("🔍 Filtres")

    clients = ["Tous"] + sorted(df_brut["Client"].unique().astype(str).tolist())
    client_selectionne = st.sidebar.selectbox("Filtrer par client", clients)

    ids = ["Tous"] + sorted([str(x) for x in df_brut["Shipment No."].unique().tolist() if pd.notna(x)])
    id_selectionne = st.sidebar.selectbox("Numéro de shipment", ids)

    df_affiche = df_brut.copy()

    if client_selectionne != "Tous":
        df_affiche = df_affiche[df_affiche["Client"] == client_selectionne]

    if id_selectionne != "Tous":
        df_affiche = df_affiche[df_affiche["Shipment No."].astype(str) == id_selectionne]

    st.markdown("<h1 class='main-title'>📦 Gestion de l’inventaire & clients</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Clients</div><div class='metric-value'>{df_brut['Client'].nunique()}</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Articles</div><div class='metric-value'>{len(df_brut)}</div></div>", unsafe_allow_html=True)

    with col3:
        stock = int(df_brut["Quantity in Inventory"].sum()) if "Quantity in Inventory" in df_brut.columns else 0
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Stock</div><div class='metric-value'>{stock}</div></div>", unsafe_allow_html=True)

    st.info(f"📍 {len(df_affiche)} lignes trouvées")

    df_modifie = st.data_editor(df_affiche, num_rows="dynamic", use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Sauvegarder"):
            if client_selectionne == "Tous" and id_selectionne == "Tous":
                final = df_modifie
            else:
                hors_vue = df_brut.drop(df_affiche.index)
                final = pd.concat([hors_vue, df_modifie], ignore_index=True)

            sauvegarder_donnees(final)
            st.rerun()

    with col2:
        if os.path.exists(FICHIER):
            st.download_button("📥 Télécharger Excel", data=open(FICHIER, "rb"), file_name=FICHIER)

# =========================================================
# PAGE 2 : DEVIS
# =========================================================
elif page == "Générateur de devis 📄":

    try:
        df_base = pd.read_excel("Clas.xlsx", sheet_name="lista_items")
    except:
        df_base = pd.DataFrame(columns=["Code article", "Désignation", "P.U. HT (MAD)"])

    if "devis_items" not in st.session_state:
        st.session_state.devis_items = []

    st.markdown("<h1 class='main-title'>📄 Création de devis</h1>", unsafe_allow_html=True)

    st.session_state.devis_no = st.text_input("Numéro de devis", "042110")

    clients_existants = sorted(df_brut["Client"].unique().astype(str).tolist())
    options = clients_existants + ["➕ Nouveau client"]

    choix_client = st.selectbox("Client", options)

    if choix_client == "➕ Nouveau client":
        client_final = st.text_input("Nom du client")
    else:
        client_final = choix_client

    mode = st.radio("Mode d’ajout", ["Base articles", "Saisie manuelle"])

    if mode == "Base articles":
        if not df_base.empty:
            code = st.selectbox("Article", df_base["Code article"].unique())
            qte = st.number_input("Quantité", min_value=1, value=1)

            if st.button("➕ Ajouter"):
                row = df_base[df_base["Code article"] == code].iloc[0]
                st.session_state.devis_items.append({
                    "Code": code,
                    "Désignation": row["Désignation"],
                    "Quantité": qte,
                    "P.U. HT": row["P.U. HT (MAD)"],
                    "Montant HT": qte * row["P.U. HT (MAD)"]
                })
                st.rerun()

    else:
        code = st.text_input("Code article")
        desc = st.text_input("Désignation")
        pu = st.number_input("Prix unitaire HT", min_value=0.0)
        qte = st.number_input("Quantité", min_value=1)

        if st.button("➕ Ajouter"):
            st.session_state.devis_items.append({
                "Code": code,
                "Désignation": desc,
                "Quantité": qte,
                "P.U. HT": pu,
                "Montant HT": qte * pu
            })
            st.rerun()

    if st.session_state.devis_items:
        df_devis = pd.DataFrame(st.session_state.devis_items)
        df_devis = st.data_editor(df_devis, use_container_width=True)

        total_ht = df_devis["Montant HT"].sum()
        total_ttc = total_ht * 1.2

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>TOTAL HT</div><div class='metric-value'>{total_ht:,.2f} MAD</div></div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>TOTAL TTC</div><div class='metric-value'>{total_ttc:,.2f} MAD</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            # --- GÉNÉRATION RÉELLE DU PDF & TÉLÉCHARGEMENT ---
            try:
                pdf = PropMedPDF()
                pdf.add_page()
                pdf.set_y(45)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(100, 10, f"Client : {client_final}", 0, 1)
                pdf.cell(100, 10, f"Date : {date.today().strftime('%d/%m/%Y')}", 0, 1)
                pdf.ln(5)
                
                # Entête du Tableau
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(30, 8, "Code", 1)
                pdf.cell(75, 8, u"Désignation", 1)
                pdf.cell(20, 8, "Qte", 1, 0, 'C')
                pdf.cell(25, 8, "P.U. HT", 1, 0, 'C')
                pdf.cell(40, 8, "Montant HT", 1, 1, 'C')
                
                # Remplissage des articles
                pdf.set_font('Arial', '', 10)
                for index, row in df_devis.iterrows():
                    pdf.cell(30, 8, str(row['Code']), 1)
                    pdf.cell(75, 8, str(row[u'Désignation']), 1)
                    pdf.cell(20, 8, str(row[u'Quantité']), 1, 0, 'C')
                    pdf.cell(25, 8, f"{row['P.U. HT']:,.2f}", 1, 0, 'C')
                    pdf.cell(40, 8, f"{row['Montant HT']:,.2f}", 1, 1, 'C')
                
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(150, 8, "TOTAL HT", 1, 0, 'R')
                pdf.cell(40, 8, f"{total_ht:,.2f} MAD", 1, 1, 'C')
                pdf.cell(150, 8, "TOTAL TTC (Avec TVA 20%)", 1, 0, 'R')
                pdf.cell(40, 8, f"{total_ttc:,.2f} MAD", 1, 1, 'C')
                
                # Encodage du PDF en bytes pour le bouton
                pdf_output = pdf.output(dest='S').encode('latin-1')
                
                st.download_button(
                    label="📥 Télécharger Devis PDF",
                    data=pdf_output,
                    file_name=f"Devis_{st.session_state.devis_no}_{client_final}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF: {e}")

        with col2:
            if st.button("🗑️ Vider", use_container_width=True):
                st.session_state.devis_items = []
                st.rerun()
