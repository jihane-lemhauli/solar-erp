import streamlit as st
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="ERP Solaire ☀️", layout="wide", page_icon="☀️")

# =========================
# UTILISATEURS
# =========================
USERS = {"admin": "1234", "jihane": "1111"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# FONCTION DE CALCUL AUTOMATIQUE
# =========================
def calculate_metrics(df_to_calc):
    """Calcul de la marge, du stock et nettoyage des données"""
    if df_to_calc is None or df_to_calc.empty:
        return df_to_calc

    cols_to_fix = ["Prix_Achat", "Prix_Vente", "Stock_Initial", "Quantité_Vendue", "Montant_Total_TTC"]
    for col in cols_to_fix:
        if col in df_to_calc.columns:
            df_to_calc[col] = pd.to_numeric(df_to_calc[col], errors="coerce").fillna(0)

    if "Prix_Vente" in df_to_calc.columns and "Prix_Achat" in df_to_calc.columns:
        df_to_calc["Marge"] = df_to_calc["Prix_Vente"] - df_to_calc["Prix_Achat"]
        df_to_calc["Marge_%"] = df_to_calc.apply(
            lambda row: (row["Marge"] / row["Prix_Achat"] * 100) if row["Prix_Achat"] > 0 else 0,
            axis=1
        ).round(2)

    if "Stock_Initial" in df_to_calc.columns and "Quantité_Vendue" in df_to_calc.columns:
        df_to_calc["Stock_Restant"] = df_to_calc["Stock_Initial"] - df_to_calc["Quantité_Vendue"]

    return df_to_calc.fillna(0)

# =========================
# CHARGEMENT ET SAUVEGARDE DES DONNÉES
# =========================
def load_data():
    file = "S.xlsx"
    if os.path.exists(file):
        df = pd.read_excel(file)
        df = df.dropna(how='all')
    else:
        df = pd.DataFrame()

    essential_cols = [
        "ID_Facture", "Client_Nom", "Produit_Nom", "Status_Etape",
        "Stock_Initial", "Quantité_Vendue", "Prix_Achat", "Prix_Vente",
        "Montant_Total_TTC", "Status"
    ]

    for c in essential_cols:
        if c not in df.columns:
            df[c] = ""

    return calculate_metrics(df)


def save_data(df_to_save):
    try:
        df_final_save = calculate_metrics(df_to_save)
        df_final_save.to_excel("S.xlsx", index=False)
        st.success("✅ Données enregistrées avec succès !")
        return True
    except PermissionError:
        st.error("❌ Erreur : veuillez fermer le fichier Excel (S.xlsx) avant de sauvegarder !")
        return False


# Chargement des données
df_raw = load_data()

# =========================
# CONFIGURATION DES COLONNES
# =========================
liste_produits = ["Panneau Solaire", "Batterie", "Onduleur", "Support Alu", "Câblage"]
liste_status = ["Lead", "Devis Accepté", "Facturé", "Refusé"]

column_configuration = {
    "Client_Nom": st.column_config.SelectboxColumn(
        "Client 👥",
        options=df_raw["Client_Nom"].unique().tolist(),
        required=True
    ),
    "Produit_Nom": st.column_config.SelectboxColumn(
        "Produit ☀️",
        options=liste_produits,
        required=True
    ),
    "Status_Etape": st.column_config.SelectboxColumn(
        "Étape 🚩",
        options=liste_status
    ),
    "Marge_%": st.column_config.NumberColumn("Marge (%)", format="%.2f %%"),
    "Prix_Achat": st.column_config.NumberColumn("Achat (DH)", format="%.2f"),
    "Prix_Vente": st.column_config.NumberColumn("Vente (DH)", format="%.2f"),
    "Montant_Total_TTC": st.column_config.NumberColumn("Total TTC (DH)", format="%.2f"),
}

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
            st.error("❌ Erreur d'authentification")

    st.stop()

# =========================
# SIDEBAR & FILTRES
# =========================
st.sidebar.title("☀️ ERP Solaire")
st.sidebar.write(f"👤 Utilisateur : **{st.session_state.user}**")

menu = st.sidebar.selectbox(
    "Menu 📋",
    ["Tableau de bord 📊", "Stock 📦", "Factures 📑", "Clients 👥", "Produits Client ☀️"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Recherche / Filtres")

search_client = st.sidebar.text_input("Nom du client")
status_options = ["Tous"] + list(df_raw["Status_Etape"].unique()) if "Status_Etape" in df_raw.columns else ["Tous"] + liste_status
selected_status = st.sidebar.selectbox("Statut", status_options)

df_filtered = df_raw.copy()

if search_client:
    df_filtered = df_filtered[df_filtered["Client_Nom"].str.contains(search_client, case=False, na=False)]

if selected_status != "Tous":
    df_filtered = df_filtered[df_filtered["Status_Etape"] == selected_status]

st.sidebar.markdown("---")

if st.sidebar.button("Déconnexion 🚪"):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# DASHBOARD
# =========================
if menu == "Tableau de bord 📊":
    st.title("Tableau de bord ☀️")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Clients", df_filtered["Client_Nom"].nunique())
    c2.metric("📦 Stock", int(df_filtered["Stock_Restant"].sum()))
    c3.metric("💰 Chiffre d'affaires (DH)", f"{df_filtered['Montant_Total_TTC'].sum():,.2f}")
    c4.metric("📑 Factures", len(df_filtered))

    st.bar_chart(df_filtered.groupby("Client_Nom")["Montant_Total_TTC"].sum())

# =========================
# PRODUITS CLIENT
# =========================
elif menu == "Produits Client ☀️":
    st.title("📦 Gestion des produits par client")

    clients = df_filtered["Client_Nom"].dropna().unique()

    if len(clients) > 0:
        client_sel = st.selectbox("Choisir un client :", clients)

        df_client = df_raw[df_raw["Client_Nom"] == client_sel]

        st.info(f"Produits de : **{client_sel}**")

        edited_prod = st.data_editor(
            df_client,
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_configuration,
            key="prod_editor"
        )

        if st.button("💾 Sauvegarder"):
            new_df = df_raw[df_raw["Client_Nom"] != client_sel]
            edited_prod["Client_Nom"] = client_sel
            new_df = pd.concat([new_df, edited_prod], ignore_index=True)

            if save_data(new_df):
                st.rerun()
    else:
        st.warning("Aucun client ne correspond à la recherche.")

# =========================
# AUTRES MENUS
# =========================
else:
    st.title(f"Gestion : {menu}")

    edited = st.data_editor(
        df_filtered,
        num_rows="dynamic",
        use_container_width=True,
        column_config=column_configuration,
        key=f"editor_{menu}"
    )

    if st.button(f"💾 Sauvegarder {menu}"):
        df_raw.update(edited)

        if save_data(df_raw):
            st.rerun()

# =========================
# VUE GLOBALE
# =========================
st.markdown("---")
st.subheader("🌐 Vue globale (données filtrées)")
st.dataframe(df_filtered, use_container_width=True, column_config=column_configuration)
