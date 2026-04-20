import streamlit as st
import pandas as pd
import os

# 1. Configuration de la page
st.set_page_config(page_title="ERP Solaire ☀️", layout="wide", page_icon="☀️")

# =========================
# UTILISATEURS
# =========================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# CONFIGURATION DU FICHIER
# =========================
FILE_NAME = "PropMed Inventory (1) (3).xlsx"

# =========================
# FONCTION DE CALCUL AUTOMATIQUE
# =========================
def calculate_metrics(df_to_calc):
    if df_to_calc is None or df_to_calc.empty:
        return df_to_calc

    cols_to_fix = ["Quantity Ordered", "Quantity Used", "Quantity in Inventory"]
    for col in cols_to_fix:
        if col in df_to_calc.columns:
            df_to_calc[col] = pd.to_numeric(df_to_calc[col], errors="coerce").fillna(0)

    if "Quantity Ordered" in df_to_calc.columns and "Quantity Used" in df_to_calc.columns:
        df_to_calc["Quantity in Inventory"] = df_to_calc["Quantity Ordered"] - df_to_calc["Quantity Used"]

    return df_to_calc

# =========================
# LOAD DATA
# =========================
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME, engine='openpyxl')
            df = df.dropna(how='all')
            
            # Ila makanitch l-colonne Status f l-excel, t-creyaha
            if "Status" not in df.columns:
                df["Status"] = "En attente"
                
        except Exception as e:
            st.error(f"Erreur Excel: {e}")
            return pd.DataFrame()
    else:
        columns = ["Shipment No.", "Item Ref", "Item No.", "Description", "Quantity Ordered", "Quantity Used", "Quantity in Inventory", "Unit", "HS-Code - Morocco", "Date", "Status"]
        df = pd.DataFrame(columns=columns)

    return calculate_metrics(df)

# =========================
# SAVE DATA
# =========================
def save_data(df_to_save):
    try:
        df_final_save = calculate_metrics(df_to_save)
        df_final_save.to_excel(FILE_NAME, index=False, engine='openpyxl')
        st.success("✅ Données enregistrées dans Excel !")
        return True
    except PermissionError:
        st.error("❌ Ferme le fichier Excel d'abord !")
        return False

# Chargement des données
df_raw = load_data()

# =========================
# CONNEXION
# =========================
if not st.session_state.logged_in:
    st.title("🔐 Connexion ERP Solaire")
    u = st.text_input("Utilisateur")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if u in USERS and USERS[u] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("❌ Erreur")
    st.stop()

# =========================
# SIDEBAR (FILTRES)
# =========================
st.sidebar.title("☀️ ERP Solaire")
st.sidebar.write(f"👤 **{st.session_state.user}**")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtres de recherche")

# 1. Filtre par Shipment ID (Client ID)
all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist()])
selected_id = st.sidebar.selectbox("Filtrer par Shipment No. (ID)", all_ids)

# 2. Filtre par Statut
if "Status" in df_raw.columns:
    all_status = ["Tous"] + sorted(df_raw["Status"].unique().tolist())
else:
    all_status = ["Tous", "En attente", "Livré", "Facturé"]
selected_status = st.sidebar.selectbox("Filtrer par Statut", all_status)

st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Menu 📋",
    ["Tableau de bord 📊", "Gestion Inventaire 📦"]
)

if st.sidebar.button("Déconnexion 🚪"):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# APPLICATION DES FILTRES
# =========================
df_display = df_raw.copy()

if selected_id != "Tous":
    df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]

if selected_status != "Tous":
    df_display = df_display[df_display["Status"] == selected_status]

# =========================
# DASHBOARD
# =========================
if menu == "Tableau de bord 📊":
    st.title("Tableau de bord 📊")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total Commandé", int(df_display["Quantity Ordered"].sum()))
    c2.metric("📤 Total Utilisé", int(df_display["Quantity Used"].sum()))
    c3.metric("🔋 Stock Dispo", int(df_display["Quantity in Inventory"].sum()))

    st.subheader("Visualisation des stocks filtrés")
    st.bar_chart(df_display.groupby("Shipment No.")["Quantity in Inventory"].sum())

# =========================
# GESTION INVENTAIRE
# =========================
elif menu == "Gestion Inventaire 📦":
    st.title("📦 Gestion de l'inventaire")
    st.info(f"Affichage de **{len(df_display)}** lignes après filtrage.")

    # Éditeur de données
    edited_df = st.data_editor(
        df_display,
        num_rows="dynamic",
        use_container_width=True,
        key="main_editor"
    )

    if st.button("💾 Sauvegarder les modifications"):
        # Fusionner les modifs filtrées avec la base de données globale
        if selected_id == "Tous" and selected_status == "Tous":
            # Si aucun filtre, on remplace tout
            final_df = edited_df
        else:
            # Si filtre activé, on met à jour uniquement les lignes affichées
            # On garde les lignes qui n'étaient pas dans l'affichage
            df_not_in_view = df_raw.drop(df_display.index)
            final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
        
        if save_data(final_df):
            st.rerun()

# =========================
# VUE GLOBALE (Footer)
# =========================
st.markdown("---")
st.subheader("🌐 Aperçu global (sans filtres)")
st.dataframe(df_raw, use_container_width=True)
