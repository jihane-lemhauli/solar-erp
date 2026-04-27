import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# --- 1. إعدادات الصفحة العامة ---
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

# =========================================================
# SIDEBAR NAVIGATION (التحكم في النوافذ)
# =========================================================
st.sidebar.title("☀️ ERP Solaire")
st.sidebar.write(f"👤 **{st.session_state.user}**")
st.sidebar.markdown("---")

# اختيار الصفحة (Fenêtre)
page = st.sidebar.radio("Menu 📋", ["Gestion Inventaire 📦", "Générateur de Devis 📄"])

if st.sidebar.button("Déconnexion 🚪"):
    st.session_state.logged_in = False
    st.rerun()

# =========================================================
# FENÊTRE 1: GESTION INVENTAIRE (الكود الثاني ديالك)
# =========================================================
if page == "Gestion Inventaire 📦":
    FILE_NAME = "PropMed Inventory (1) (3).xlsx"

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
            except Exception as e:
                st.error(f"Erreur Excel: {e}")
                return pd.DataFrame()
        else:
            columns = ["Shipment No.", "Item Ref", "Item No.", "Description", "Quantity Ordered", "Quantity Used", "Quantity in Inventory", "Unit", "HS-Code - Morocco", "Date", "Status"]
            df = pd.DataFrame(columns=columns)
        return calculate_metrics(df)

    def save_data(df_to_save):
        try:
            df_final_save = calculate_metrics(df_to_save)
            df_final_save.to_excel(FILE_NAME, index=False, engine='openpyxl')
            st.success("✅ Données enregistrées dans Excel !")
            return True
        except PermissionError:
            st.error("❌ Ferme le fichier Excel d'abord !")
            return False

    df_raw = load_data()
    
    st.sidebar.subheader("🔍 Filtres de recherche")
    all_ids = ["Tous"] + sorted([str(x) for x in df_raw["Shipment No."].unique().tolist()])
    selected_id = st.sidebar.selectbox("Filtrer par Shipment No. (ID)", all_ids)
    
    if "Status" in df_raw.columns:
        all_status = ["Tous"] + sorted(df_raw["Status"].unique().tolist())
    else:
        all_status = ["Tous", "En attente", "Livré", "Facturé"]
    selected_status = st.sidebar.selectbox("Filtrer par Statut", all_status)

    df_display = df_raw.copy()
    if selected_id != "Tous":
        df_display = df_display[df_display["Shipment No."].astype(str) == selected_id]
    if selected_status != "Tous":
        df_display = df_display[df_display["Status"] == selected_status]

    st.title("📦 Gestion de l'inventaire")
    st.info(f"Affichage de **{len(df_display)}** lignes après filtrage.")

    edited_df = st.data_editor(df_display, num_rows="dynamic", use_container_width=True, key="main_editor")

    if st.button("💾 Sauvegarder les modifications"):
        if selected_id == "Tous" and selected_status == "Tous":
            final_df = edited_df
        else:
            df_not_in_view = df_raw.drop(df_display.index)
            final_df = pd.concat([df_not_in_view, edited_df], ignore_index=True)
        if save_data(final_df):
            st.rerun()

    st.markdown("---")
    st.subheader("🌐 Aperçu global (sans filtres)")
    st.dataframe(df_raw, use_container_width=True)

# =========================================================
# FENÊTRE 2: GÉNÉRATEUR DE DEVIS (الكود الأول ديالك)
# =========================================================
elif page == "Générateur de Devis 📄":
    try:
        df_base = pd.read_excel("Classeur1.xlsx", sheet_name="lista_items")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier Excel: {e}")
        df_base = pd.DataFrame(columns=['Code article', 'Désignation', 'P.U. HT (MAD)'])

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
            self.set_font('Arial', 'B', 16)
            self.set_xy(110, 15)
            self.cell(90, 10, f"DEVIS : {st.session_state.get('devis_no', '---')}", 0, 1, 'C')
            self.set_font('Arial', '', 9)
            self.set_xy(110, 23)
            self.cell(90, 10, f"Systeme PV Hybride - {date.today().year}", 0, 1, 'C')

        def footer(self):
            self.set_y(-20)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(150, 150, 150)
            line = "PropMed SARL | Tanger | RC: 137001 | IF: 53625661 | ICE: 003241314000056"
            self.cell(0, 10, line, 0, 0, 'C')

    if 'devis_items' not in st.session_state:
        st.session_state.devis_items = []

    st.markdown(f"""
        <div style="background-color:#1a4e8a; padding:20px; border-radius:10px; color:white; text-align:center; margin-bottom:20px;">
            <h1 style="margin:0;">PropMed Solar Solutions</h1>
            <p style="margin:0;">Générateur de Devis Professionnel</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 Informations du Devis")
    st.session_state.devis_no = st.text_input("N° Devis", "042110")
    st.session_state.date_devis = st.date_input("Date du Devis", date.today())
    client_name = st.text_input("Nom du Client", "Jihane")
    validite_offre = st.text_input("Validité de l'offre", "10 Jours")
    delai_exec = st.text_input("Délai d'exécution", "3 Jours")
    modalites_paie = st.text_area("Modalités de paiement", "50 % à la commande / 50 % à la mise en service")

    st.divider()
    st.subheader("📦 Gestion des Articles")
    mode_ajout = st.radio("Mode d'ajout :", ["Sélectionner depuis la base", "Saisie manuelle"])

    if mode_ajout == "Sélectionner depuis la base":
        if not df_base.empty:
            code_sel = st.selectbox("Sélectionner un article", df_base['Code article'].unique())
            qte_sel = st.number_input("Quantité", min_value=1, value=1, key="qte_base")
            if st.button("➕ Ajouter l'article sélectionné"):
                row = df_base[df_base['Code article'] == code_sel].iloc[0]
                st.session_state.devis_items.append({
                    "Code": code_sel, "Désignation": row['Désignation'], "Quantité": qte_sel,
                    "P.U. HT": row['P.U. HT (MAD)'], "Montant HT": qte_sel * row['P.U. HT (MAD)']
                })
                st.rerun()
    else:
        m_code = st.text_input("Code Article (Manuel)")
        m_desc = st.text_input("Désignation (Manuel)")
        m_pu = st.number_input("Prix Unitaire HT (MAD)", min_value=0.0)
        m_qte = st.number_input("Quantité ", min_value=1, value=1, key="qte_man")
        if st.button("➕ Ajouter l'article manuellement"):
            st.session_state.devis_items.append({
                "Code": m_code, "Désignation": m_desc, "Quantité": m_qte, "P.U. HT": m_pu, "Montant HT": m_qte * m_pu
            })
            st.rerun()

    if st.session_state.devis_items:
        df_current = pd.DataFrame(st.session_state.devis_items)
        st.table(df_current)
        total_ht = df_current['Montant HT'].sum()
        tva_20 = total_ht * 0.2
        total_ttc = total_ht + tva_20
        st.write(f"**Total HT:** {total_ht:,.2f} MAD | **TVA 20%:** {tva_20:,.2f} MAD | **Total TTC:** {total_ttc:,.2f} MAD")

        if st.button("🗑️ Vider la liste"):
            st.session_state.devis_items = []
            if 'pdf_blob' in st.session_state: del st.session_state.pdf_blob
            st.rerun()

        if st.button("📄 Générer le Devis PDF"):
            pdf = PropMedPDF()
            pdf.add_page()
            pdf.set_y(40)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 10, f"Client: {client_name}", 0, 1)
            pdf.ln(5)
            pdf.set_fill_color(26, 78, 138); pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(30, 10, "Code", 1, 0, 'C', True); pdf.cell(90, 10, "Designation", 1, 0, 'C', True)
            pdf.cell(15, 10, "Qte", 1, 0, 'C', True); pdf.cell(30, 10, "P.U. HT", 1, 0, 'C', True)
            pdf.cell(30, 10, "Montant", 1, 1, 'C', True)
            pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 8)
            for item in st.session_state.devis_items:
                clean_d = str(item['Désignation']).encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(30, 8, str(item['Code']), 1)
                pdf.cell(90, 8, clean_d[:55], 1)
                pdf.cell(15, 8, str(item['Quantité']), 1, 0, 'C')
                pdf.cell(30, 8, f"{item['P.U. HT']:,.2f}", 1, 0, 'R')
                pdf.cell(30, 8, f"{item['Montant HT']:,.2f}", 1, 1, 'R')
            pdf.ln(5); pdf.set_x(135); pdf.set_font('Arial', 'B', 9)
            pdf.cell(35, 8, "Total HT", 1, 0); pdf.cell(30, 8, f"{total_ht:,.2f}", 1, 1, 'R')
            pdf.set_x(135); pdf.cell(35, 8, "TVA 20%", 1, 0); pdf.cell(30, 8, f"{tva_20:,.2f}", 1, 1, 'R')
            pdf.set_x(135); pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255)
            pdf.cell(35, 10, "NET A PAYER", 1, 0, '', True); pdf.cell(30, 10, f"{total_ttc:,.2f}", 1, 1, 'R', True)
            pdf.ln(10); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 8, "Conditions & Coordonnees Bancaires", "B", 1)
            pdf.set_font('Arial', '', 8)
            bank_txt = (f"Validite: {validite_offre} | Delai: {delai_exec}\n"
                        f"Modalites: {modalites_paie}\n"
                        f"Banque: Attijariwafa Bank | RIB: 007 640 0000903000016328 55")
            pdf.multi_cell(0, 5, bank_txt)
            st.session_state.pdf_blob = pdf.output(dest='S').encode('latin-1')
            st.success("✅ PDF généré!")

        if 'pdf_blob' in st.session_state:
            st.download_button(label="📥 Télécharger le PDF", data=st.session_state.pdf_blob, file_name=f"Devis_{client_name}.pdf", mime="application/pdf")
    else:
        st.info("Ajoutez des articles pour commencer.")