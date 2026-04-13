import streamlit as st
import pandas as pd
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ERP Solaire", layout="wide", page_icon="☀️")

# =========================
# USERS (SECURITY)
# =========================
USERS = {
    "admin": "1234",
    "jihane": "1111"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# LOAD DATA
# =========================
def load_data():
    file_path = "S.xlsx"
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        st.error("Fichier S.xlsx introuvable")
        return pd.DataFrame()

def save_data(df):
    df.to_excel("S.xlsx", index=False)

df = load_data()

# =========================
# LOGIN SYSTEM
# =========================
if not st.session_state.logged_in:

    st.title("🔐 ERP Solaire Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("✅ Login success")
            st.rerun()
        else:
            st.error("❌ Username ou password incorrect")

    st.stop()

# =========================
# STYLE
# =========================
def style_payment(val):
    if val == "Yes":
        return "background-color:#d4edda; color:#155724; font-weight:bold"
    elif val == "No":
        return "background-color:#f8d7da; color:#721c24; font-weight:bold"
    return ""

# =========================
# APP START
# =========================
if df is not None and not df.empty:

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("☀️ ERP Solaire")

    st.sidebar.write(f"👤 User: {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Dashboard", "Stock", "Factures", "Clients", "Edit Client", "Add Client"]
    )

    # ---------------- STOCK CALC ----------------
    if "Stock_Initial" in df.columns and "Quantité_Vendue" in df.columns:
        df["Stock_Restant"] = df["Stock_Initial"] - df["Quantité_Vendue"]

    # ---------------- FILTERS ----------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtres")

    search = st.sidebar.text_input("🔍 Client")

    if "Magasinier_Nom" in df.columns:
        magasinier = st.sidebar.selectbox(
            "Magasinier",
            ["Tous"] + list(df["Magasinier_Nom"].dropna().unique())
        )
    else:
        magasinier = "Tous"

    df_final = df.copy()

    if search and "Client_Nom" in df.columns:
        df_final = df_final[df_final["Client_Nom"].str.contains(search, case=False, na=False)]

    if magasinier != "Tous":
        df_final = df_final[df_final["Magasinier_Nom"] == magasinier]

    # =========================
    # TITLE
    # =========================
    st.title("☀️ Solar ERP System")
    st.markdown(f"Page : **{menu}**")
    st.markdown("---")

    # =========================
    # DASHBOARD
    # =========================
    if menu == "Dashboard":

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("👥 Clients", df["Client_Nom"].nunique() if "Client_Nom" in df.columns else 0)
        c2.metric("📦 Stock", int(df["Stock_Restant"].sum()) if "Stock_Restant" in df.columns else 0)
        c3.metric("💰 CA", f"{df['Montant_Total_TTC'].sum():,.2f} DH" if "Montant_Total_TTC" in df.columns else 0)
        c4.metric("📄 Factures", len(df))

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Ventes par Client")
            if "Client_Nom" in df.columns:
                st.bar_chart(df.groupby("Client_Nom")["Montant_Total_TTC"].sum())

        with col2:
            st.subheader("📦 Stock par Produit")
            if "Produit_Nom" in df.columns and "Stock_Restant" in df.columns:
                st.bar_chart(df.groupby("Produit_Nom")["Stock_Restant"].sum())

    # =========================
    # STOCK PAGE
    # =========================
    elif menu == "Stock":

        st.title("📦 Stock")

        if "Produit_Nom" in df.columns:
            st.dataframe(df[["Produit_Nom","Stock_Initial","Quantité_Vendue","Stock_Restant"]],
                         use_container_width=True)

        st.subheader("⚠️ Stock faible")
        if "Stock_Restant" in df.columns:
            st.dataframe(df[df["Stock_Restant"] <= 2], use_container_width=True)

    # =========================
    # FACTURES
    # =========================
    elif menu == "Factures":

        st.title("📄 Factures")

        cols = [c for c in [
            "Client_Nom",
            "Date_Creation",
            "Montant_Total_TTC",
            "Avance_50_Payé",
            "Reste_50_Payé"
        ] if c in df.columns]

        st.dataframe(df[cols], use_container_width=True)

        if "Avance_50_Payé" in df.columns:
            paid = (df["Avance_50_Payé"] == "Yes").sum()
            st.progress(paid / len(df))

    # =========================
    # CLIENTS
    # =========================
    elif menu == "Clients":

        st.title("👥 Clients")

        cols = [c for c in ["Client_Nom","Magasinier_Nom","Montant_Total_TTC"] if c in df.columns]

        st.dataframe(df[cols], use_container_width=True)

    # =========================
    # EDIT CLIENT
    # =========================
    elif menu == "Edit Client":

        st.title("✏️ Modifier Client")

        if "Client_Nom" in df.columns:

            clients = df["Client_Nom"].dropna().unique().tolist()
            selected = st.selectbox("Choisir Client", clients)

            row = df[df["Client_Nom"] == selected].iloc[0]

            st.subheader("📄 Actuel")
            st.dataframe(row.to_frame())

            st.subheader("✏️ Modifier")

            new_name = st.text_input("Nom", row["Client_Nom"])

            new_amount = row["Montant_Total_TTC"] if "Montant_Total_TTC" in df.columns else 0
            if "Montant_Total_TTC" in df.columns:
                new_amount = st.number_input("Montant", value=float(row["Montant_Total_TTC"]))

            new_mag = row["Magasinier_Nom"] if "Magasinier_Nom" in df.columns else ""
            if "Magasinier_Nom" in df.columns:
                new_mag = st.text_input("Magasinier", row["Magasinier_Nom"])

            if st.button("💾 Sauvegarder"):

                idx = df[df["Client_Nom"] == selected].index[0]

                df.at[idx, "Client_Nom"] = new_name

                if "Montant_Total_TTC" in df.columns:
                    df.at[idx, "Montant_Total_TTC"] = new_amount

                if "Magasinier_Nom" in df.columns:
                    df.at[idx, "Magasinier_Nom"] = new_mag

                save_data(df)

                st.success("✅ Modifié et sauvegardé!")
                st.rerun()

    # =========================
    # ADD CLIENT
    # =========================
    elif menu == "Add Client":

        st.title("➕ Ajouter Client")

        nom = st.text_input("Nom Client")
        montant = st.number_input("Montant Total TTC", min_value=0.0, value=0.0)

        magasinier = st.text_input("Magasinier") if "Magasinier_Nom" in df.columns else ""

        avance = st.selectbox("Avance Payée", ["Yes", "No"])
        reste = st.selectbox("Reste Payé", ["Yes", "No"])

        if st.button("💾 Ajouter"):

            new_row = {
                "Client_Nom": nom,
                "Montant_Total_TTC": montant,
                "Magasinier_Nom": magasinier,
                "Avance_50_Payé": avance,
                "Reste_50_Payé": reste
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            save_data(df)

            st.success("✅ Client ajouté!")
            st.rerun()

    # =========================
    # TABLE
    # =========================
    st.markdown("---")
    st.subheader("📋 Données")

    styled = df_final.style.applymap(
        style_payment,
        subset=[c for c in ["Avance_50_Payé","Reste_50_Payé"] if c in df_final.columns]
    )

    st.dataframe(styled, use_container_width=True)

else:
    st.warning("📂 Fichier vide ou introuvable")