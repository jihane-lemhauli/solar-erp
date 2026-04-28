import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. Paramètres généraux de la page ---
st.set_page_config(page_title="PropMed ERP & Devis ☀️", layout="wide", page_icon="☀️")

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
    st.title("🔐 Connexion ERP Solaire")
    u = st.text_input("Nom d'utilisateur")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if u in USERS and USERS[u] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("❌ Erreur de connexion")
    st.stop()

# =========================================================
# BARRE LATÉRALE
# =========================================================
st.sidebar.title("☀️ ERP Solaire")
st.sidebar.write(f"👤 **{st.session_state.user}**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Menu 📋", ["Gestion de l'inventaire 📦", "Générateur de devis 📄"])

if st.sidebar.button("Déconnexion 🚪"):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# PAGE 1: INVENTAIRE
# =========================================================
if page == "Gestion de l'inventaire 📦":
    FILE_NAME = "Inventaire.xlsx"

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

    def load_data():
        if os.path.exists(FILE_NAME):
            try:
                df = pd.read_excel(FILE_NAME, engine='openpyxl')
                df = df.dropna(how='all')
                if "Status" not in df.columns:
                    df["Status"] = "En attente"
                return calculate_metrics(df)
            except Exception as e:
                st.error(f"Erreur Excel: {e}")
                return pd.DataFrame()
        else:
            columns = ["Shipment No.", "Item Ref", "Item No.", "Description", "Quantity Ordered", "Quantity Used", "Quantity in Inventory", "Unit", "HS-Code - Morocco", "Date", "Status"]
            return pd.DataFrame(columns=columns)

    def save_data(df_to_save):
        try:
            df_final_save = calculate_metrics(df_to_save)
            df_final_save.to_excel(FILE_NAME, index=False, engine='openpyxl')
            st.success(f"✅ Données enregistrées dans '{FILE_NAME}' !")
            return True
        except PermissionError:
            st.error("❌ Erreur : veuillez fermer le fichier Excel avant l'enregistrement !")
            return False

    df_raw = load_data()
    
    st.sidebar.subheader("🔍 Filtres de recherche")
    all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist() if pd.notna(x)])
    selected_id = st.sidebar.selectbox("Filtrer par numéro d'expédition", all_ids)
    
    if "Status" in df_raw.columns:
        all_status = ["Tous"] + sorted([str(x) for x in df_raw["Status"].unique().tolist() if pd.notna(x)])
    else:
        all_status = ["Tous", "En attente", "Livré", "Facturé"]
    selected_status = st.sidebar.selectbox("Filtrer par statut", all_status)

    df_display = df_raw.copy()
    if selected_id != "Tous":
        df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]
    if selected_status != "Tous":
        df_display = df_display[df_display["Status"] == selected_status]

    st.title("📦 Gestion de l'inventaire")
    st.info(f"Affichage de **{len(df_display)}** lignes après filtrage.")

    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True, key="main_editor")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Enregistrer dans Excel"):
            if selected_id == "Tous" and selected_status == "Tous":
                final_df = edited_df
            else:
                df_not_in_view = df_raw.drop(df_display.index)
                final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
            if save_data(final_df):
                st.rerun()

    with col2:
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "rb") as f:
                st.download_button(
                    label="📥 Télécharger une copie (sauvegarde)",
                    data=f,
                    file_name=FILE_NAME,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    st.markdown("---")
    st.subheader("🌐 Aperçu global (base de données)")
    st.dataframe(df_raw, use_container_width=True)

# =========================================================
# PAGE 2: DEVIS
# =========================================================
elif page == "Générateur de devis 📄":
    try:
        df_base = pd.read_excel("Clas.xlsx", sheet_name="lista_items")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier Clas.xlsx: {e}")
        df_base = pd.DataFrame(columns=['Code article', 'Désignation', 'P.U. HT (MAD)'])

    class PropMedPDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 22)
            self.set_text_color(26, 78, 138)
            self.text(10, 22, "PropMed")
            self.set_font('Arial', '', 9)
            self.set_text_color(100, 100, 100)
            self.text(10, 28, "Solutions solaires - Tanger, Maroc")
            self.set_fill_color(26, 78, 138)
            self.rect(110, 10, 90, 25, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 16)
            self.set_xy(110, 15)
            self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '---')}", 0, 1, 'C')

        def footer(self):
            self.set_y(-20)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "PropMed SARL | Tanger", 0, 0, 'C')

    if 'devis_items' not in st.session_state:
        st.session_state.devis_items = []

    st.subheader("📋 Informations du devis")
    st.session_state.devis_no = st.text_input("Numéro du devis", "042110")
    client_name = st.text_input("Nom du client", "Client")

    st.subheader("📦 Articles")

    if st.button("➕ Ajouter un article test"):
        st.session_state.devis_items.append({
            "Code": "TEST",
            "Désignation": "Article test",
            "Quantité": 1,
            "P.U. HT": 100,
            "Montant HT": 100
        })
        st.rerun()

    if st.session_state.devis_items:
        df_current = pd.DataFrame(st.session_state.devis_items)
        st.table(df_current)

        total_ht = df_current['Montant HT'].sum()
        tva = total_ht * 0.2
        total_ttc = total_ht + tva

        st.write(f"Total HT: {total_ht} MAD")
        st.write(f"TVA: {tva} MAD")
        st.write(f"Total TTC: {total_ttc} MAD")

        if st.button("📄 Générer le PDF"):
            pdf = PropMedPDF()
            pdf.add_page()
            st.session_state.pdf_blob = pdf.output(dest='S').encode('latin-1')
            st.success("PDF généré !")

        if 'pdf_blob' in st.session_state:
            st.download_button("📥 Télécharger le PDF", st.session_state.pdf_blob, file_name="devis.pdf")
