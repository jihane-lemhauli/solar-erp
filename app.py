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
# 🎨 DESIGN PREMIUM (SIDEBAR SOMBRE & FILTRES LISIBLES)
# =========================================================
st.markdown("""
<style>

/* Fond général de l'application */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #e8edf5) !important;
    color: #0f172a;
}

/* Sidebar : Fond sombre et texte blanc */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Correction des Filtres dans le Sidebar (Fond sombre pour lisibilité) */
section[data-testid="stSidebar"] div[data-baseweb="select"], 
section[data-testid="stSidebar"] div[data-baseweb="base-input"],
section[data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Titres principaux */
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
    text-align: center; /* Aligné au milieu */
}

.metric-title {
    color: #64748b !important;
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 10px;
    text-transform: uppercase;
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
    border: none !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# GESTION DES UTILISATEURS
# =========================
UTILISATEURS = {"admin": "1234", "jihane": "1111"}

if "connecte" not in st.session_state:
    st.session_state.connecte = False

# =========================
# PAGE DE CONNEXION
# =========================
if not st.session_state.connecte:
    st.markdown("""
    <div style="text-align:center; padding-top:40px; padding-bottom:30px;">
        <h1 style="color:#0f172a; font-size:42px; font-weight:800;">☀️ PropMed ERP</h1>
        <p style="color:#64748b; font-size:18px;">Système de Gestion Solaire & Générateur de Devis</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        with st.form("form_connexion"):
            st.markdown("### 🔐 Connexion")
            nom_u = st.text_input("Utilisateur")
            mdp_u = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter", use_container_width=True):
                if nom_u in UTILISATEURS and UTILISATEURS[nom_u] == mdp_u:
                    st.session_state.connecte = True
                    st.session_state.utilisateur = nom_u
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
    st.stop()

# =========================================================
# CHARGEMENT DES DONNÉES
# =========================================================
FICHIER_INVENTAIRE = "Inventaire.xlsx"

def charger_donnees():
    if os.path.exists(FICHIER_INVENTAIRE):
        try:
            df = pd.read_excel(FICHIER_INVENTAIRE, engine='openpyxl')
            if "Client" not in df.columns: df.insert(0, "Client", "Inconnu")
            colonnes_num = ["Quantité Commandée", "Quantité Utilisée", "Stock Restant"]
            for col in colonnes_num:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame(columns=["Client", "N° Expédition", "Référence", "Description", "Quantité Commandée", "Quantité Utilisée", "Stock Restant", "Statut"])

def sauvegarder_donnees(df):
    df["Stock Restant"] = df["Quantité Commandée"] - df["Quantité Utilisée"]
    df.to_excel(FICHIER_INVENTAIRE, index=False, engine='openpyxl')
    st.success("✅ Données sauvegardées !")

df_global = charger_donnees()

# =========================================================
# BARRE LATÉRALE (SIDEBAR)
# =========================================================
st.sidebar.markdown("""
<div style="text-align:center;padding:10px 0 20px 0;">
    <h1 style="color:white;">☀️ PropMed</h1>
    <p style="color:#cbd5e1;">Logiciel de Gestion</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.08); padding:15px; border-radius:16px; margin-bottom:20px;">
👤 <b>Bienvenue, {st.session_state.utilisateur}</b>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])
st.sidebar.markdown("---")

# =========================================================
# PAGE 1 : GESTION INVENTAIRE
# =========================================================
if page == "Gestion Inventaire 📦":
    st.sidebar.subheader("🔍 Filtres")
    liste_clients = ["Tous"] + sorted(df_global["Client"].unique().astype(str).tolist())
    client_choisi = st.sidebar.selectbox("Filtrer par Client", liste_clients)

    df_filtre = df_global.copy()
    if client_choisi != "Tous":
        df_filtre = df_filtre[df_filtre["Client"] == client_choisi]

    st.markdown("<h1 class='main-title'>📦 Gestion de l'Inventaire</h1>", unsafe_allow_html=True)

    # Cartes KPI
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.markdown(f'<div class="metric-card"><div class="metric-title">Total Clients</div><div class="metric-value">{df_global["Client"].nunique()}</div></div>', unsafe_allow_html=True)
    kpi2.markdown(f'<div class="metric-card"><div class="metric-title">Articles Référencés</div><div class="metric-value">{len(df_global)}</div></div>', unsafe_allow_html=True)
    total_stock = int(df_global["Stock Restant"].sum()) if not df_global.empty else 0
    kpi3.markdown(f'<div class="metric-card"><div class="metric-title">Articles en Stock</div><div class="metric-value">{total_stock}</div></div>', unsafe_allow_html=True)

    st.write("")

    with st.expander("➕ Ajouter une nouvelle ligne"):
        with st.form("form_ajout"):
            c1, c2, c3 = st.columns(3)
            n_cli = c1.text_input("Nom du Client")
            n_exp = c2.text_input("N° Expédition / Shipment")
            n_des = c3.text_input("Description de l'article")
            c4, c5 = st.columns(2)
            n_qc = c4.number_input("Quantité Commandée", min_value=0)
            n_qu = c5.number_input("Quantité Utilisée", min_value=0)
            if st.form_submit_button("Ajouter à la base"):
                nouvelle_ligne = {"Client": n_cli, "N° Expédition": n_exp, "Description": n_des, "Quantité Commandée": n_qc, "Quantité Utilisée": n_qu}
                df_global = pd.concat([df_global, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                sauvegarder_donnees(df_global)
                st.rerun()

    st.info(f"📍 {len(df_filtre)} lignes affichées.")
    df_edite = st.data_editor(df_filtre, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Sauvegarder les modifications", use_container_width=True):
        if client_choisi == "Tous":
            sauvegarder_donnees(df_edite)
        else:
            df_final = pd.concat([df_global[df_global["Client"] != client_choisi], df_edite], ignore_index=True)
            sauvegarder_donnees(df_final)
        st.rerun()

# =========================================================
# PAGE 2 : GÉNÉRATEUR DE DEVIS
# =========================================================
elif page == "Générateur de Devis 📄":
    st.markdown("<h1 class='main-title'>📄 Création de Devis</h1>", unsafe_allow_html=True)
    
    if 'panier_devis' not in st.session_state:
        st.session_state.panier_devis = []

    with st.container():
        st.markdown('<div style="background:white; padding:20px; border-radius:20px; border:1px solid #e5e7eb;">', unsafe_allow_html=True)
        st.subheader("Informations Client")
        
        # Choix Client : Existant ou Nouveau
        liste_base = sorted(df_global["Client"].unique().astype(str).tolist())
        options = liste_base + ["➕ Nouveau Client (Saisie manuelle)"]
        choix = st.selectbox("Sélectionner le client pour le devis", options)

        if choix == "➕ Nouveau Client (Saisie manuelle)":
            client_final = st.text_input("Entrez le nom du nouveau client")
        else:
            client_final = choix
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Formulaire d'ajout d'article
    with st.expander("📝 Ajouter des articles au devis", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        article_nom = col1.text_input("Désignation de l'article")
        article_prix = col2.number_input("Prix Unitaire (MAD)", min_value=0.0)
        article_qte = col3.number_input("Quantité", min_value=1, value=1)
        
        if st.button("➕ Ajouter au panier"):
            st.session_state.panier_devis.append({
                "Désignation": article_nom,
                "Prix HT": article_prix,
                "Quantité": article_qte,
                "Total HT": article_prix * article_qte
            })
            st.rerun()

    # Affichage du panier
    if st.session_state.panier_devis:
        st.subheader("Articles dans le devis")
        df_devis = pd.DataFrame(st.session_state.panier_devis)
        st.table(df_devis)

        total_ht = df_devis["Total HT"].sum()
        total_ttc = total_ht * 1.20 # TVA 20%

        c_t1, c_t2 = st.columns(2)
        c_t1.markdown(f'<div class="metric-card"><div class="metric-title">Total HT</div><div class="metric-value">{total_ht:,.2f} MAD</div></div>', unsafe_allow_html=True)
        c_t2.markdown(f'<div class="metric-card"><div class="metric-title">Total TTC (TVA 20%)</div><div class="metric-value">{total_ttc:,.2f} MAD</div></div>', unsafe_allow_html=True)

        st.write("")
        col_f1, col_f2 = st.columns(2)
        if col_f1.button("📄 Générer Devis PDF", use_container_width=True):
            st.success(f"Génération du PDF pour {client_final}...")
        
        if col_f2.button("🗑️ Vider le panier", use_container_width=True):
            st.session_state.panier_devis = []
            st.rerun()

# Bouton de déconnexion dans le sidebar
if st.sidebar.button("Déconnexion 🚪", use_container_width=True):
    st.session_state.connecte = False
    st.rerun()
