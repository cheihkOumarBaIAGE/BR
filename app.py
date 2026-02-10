# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO
import zipfile

# -----------------------
# 1. AUTHENTICATION SETUP
# -----------------------
# You can move this to st.secrets for better security later
USER_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "ecole_user": {"password": "ism2025", "role": "manager"},
    "quick_user": {"password": "quickpax", "role": "quick_user"}
}

def check_password():
    """Returns True if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Accès Restreint - ISM Automation")
        user = st.text_input("Nom d'utilisateur")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if user in USER_DB and USER_DB[user]["password"] == pwd:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = USER_DB[user]["role"]
                st.rerun()
            else:
                st.error("Utilisateur ou mot de passe incorrect.")
        return False
    return True

# -----------------------
# 2. APP CONFIG & HELPERS
# -----------------------
if check_password():
    # Only run the app if authenticated
    st.set_page_config(page_title="ISM Automation Hub", layout="wide")

    # (Original Mappings & Helpers go here - truncated for brevity in display)
    # [KEEP ALL YOUR SCHOOL_MAPPINGS AND HELPER FUNCTIONS FROM THE PREVIOUS CODE]
    
    # ... [Insert SCHOOL_MAPPINGS here] ...
    # ... [Insert all def read_emails_txt, normalize_and_clean_df, etc. here] ...

    # Sidebar Logout
    with st.sidebar:
        st.write(f"Connecté en tant que : **{st.session_state['user_role'].upper()}**")
        if st.button("Se déconnecter"):
            st.session_state["authenticated"] = False
            st.rerun()
        st.markdown("---")

    # -------------------------------------------
    # 3. CONDITIONAL RENDERING BASED ON ROLES
    # -------------------------------------------
    user_role = st.session_state["user_role"]

    # --- SECTION A: GÉNÉRATEUR MANUEL RAPIDE ---
    # Visible by 'admin' and 'quick_user'
    if user_role in ["admin", "quick_user"]:
        with st.expander("🛠️ GÉNÉRATEUR MANUEL RAPIDE", expanded=(user_role == "quick_user")):
            st.write("Idéal pour attribuer un code de cours à une liste d'emails.")
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                manual_code = st.text_input("Code du cours", key="manual_code_input")
            with col_m2:
                manual_emails_input = st.text_area("Emails (un par ligne)", key="manual_emails_input")
            
            if st.button("Générer le CSV Manuel"):
                if manual_code and manual_emails_input:
                    emails = [e.strip() for e in manual_emails_input.splitlines() if e.strip()]
                    manual_df = pd.DataFrame({"code": [manual_code] * len(emails), "email": emails})
                    csv_buffer = BytesIO()
                    manual_df.to_csv(csv_buffer, index=False, header=False, encoding="utf-8-sig")
                    csv_buffer.seek(0)
                    st.download_button("📥 Télécharger CSV", csv_buffer, f"manuel_{manual_code}.csv")
                else:
                    st.warning("Remplissez tous les champs.")

    # --- SECTION B: TRAITEMENT PRINCIPAL ---
    # Visible by 'admin' and 'manager'
    if user_role in ["admin", "manager"]:
        st.markdown("---")
        st.subheader("🎓 TRAITEMENT PRINCIPAL — ECOLE")
        
        SCHOOLS = ["INGENIEUR", "GRADUATE", "MANAGEMENT", "DROIT", "MADIBA"]
        DATA_DIR = Path("data")
        
        selected_school = st.selectbox("Choisir l'école", SCHOOLS)
        uploaded_excel = st.file_uploader("Importer le fichier Excel", type=["xls", "xlsx"])
        
        if st.button("🚀 Lancer le traitement global", type="primary"):
            if not uploaded_excel:
                st.error("Fichier manquant.")
            else:
                # [KEEP ALL YOUR MAIN PROCESSING LOGIC HERE]
                # (Same logic as before: loading mappings, process_dataframe, generating files)
                st.success("Traitement terminé pour " + selected_school)
                # ... [Insert Download Buttons Logic here] ...

    # If role has access to nothing (safety check)
    if user_role not in ["admin", "manager", "quick_user"]:
        st.warning("Vous n'avez pas de permissions assignées. Contactez l'administrateur.")
