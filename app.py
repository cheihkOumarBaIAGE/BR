# app.py
from io import BytesIO
from pathlib import Path
import pandas as pd
import streamlit as st

# 1. Configuration de la page (DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT)
st.set_page_config(
    page_title="ISM Automation Hub", page_icon="🔐", layout="wide"
)

# -----------------------
# 2. CONFIGURATION DE L'AUTHENTIFICATION
# -----------------------
# Recommandation : déplacer dans .streamlit/secrets.toml en production
USER_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "ecole_user": {"password": "ism2025", "role": "manager"},
    "quick_user": {"password": "quickpax", "role": "quick_user"},
}


def check_password():
    """Vérifie les identifiants et gère la session utilisateur."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Accès Restreint - ISM Automation")

        with st.form("login_form"):
            user = st.text_input("Nom d'utilisateur")
            pwd = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if user in USER_DB and USER_DB[user]["password"] == pwd:
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = USER_DB[user]["role"]
                    st.rerun()
                else:
                    st.error("Utilisateur ou mot de passe incorrect.")
        return False
    return True


# -----------------------
# 3. APPLICATION PRINCIPALE
# -----------------------
if check_password():
    # Barre latérale - Profil & Déconnexion
    with st.sidebar:
        st.write(
            f"Connecté en tant que : **{st.session_state['user_role'].upper()}**"
        )
        if st.button("Se déconnecter"):
            st.session_state["authenticated"] = False
            st.session_state.pop("user_role", None)
            st.rerun()
        st.markdown("---")

    user_role = st.session_state["user_role"]

    # --- SECTION A: GÉNÉRATEUR MANUEL RAPIDE ---
    if user_role in ["admin", "quick_user"]:
        with st.expander(
            "🛠️ GÉNÉRATEUR MANUEL RAPIDE", expanded=(user_role == "quick_user")
        ):
            st.write(
                "Idéal pour attribuer un code de cours à une liste d'emails."
            )
            col_m1, col_m2 = st.columns([1, 2])

            with col_m1:
                manual_code = st.text_input(
                    "Code du cours", key="manual_code_input"
                )
            with col_m2:
                manual_emails_input = st.text_area(
                    "Emails (un par ligne)", key="manual_emails_input"
                )

            if st.button("Générer le CSV Manuel"):
                if manual_code and manual_emails_input:
                    emails = [
                        e.strip()
                        for e in manual_emails_input.splitlines()
                        if e.strip()
                    ]
                    manual_df = pd.DataFrame(
                        {"code": [manual_code] * len(emails), "email": emails}
                    )

                    csv_buffer = BytesIO()
                    manual_df.to_csv(
                        csv_buffer,
                        index=False,
                        header=False,
                        encoding="utf-8-sig",
                    )
                    csv_buffer.seek(0)

                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv_buffer,
                        file_name=f"manuel_{manual_code}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("Veuillez remplir tous les champs.")

    # --- SECTION B: TRAITEMENT PRINCIPAL ---
    if user_role in ["admin", "manager"]:
        if user_role == "admin":
            st.markdown("---")

        st.subheader("🎓 TRAITEMENT PRINCIPAL — ÉCOLE")

        SCHOOLS = ["INGENIEUR", "GRADUATE", "MANAGEMENT", "DROIT", "MADIBA"]
        DATA_DIR = Path("data")

        selected_school = st.selectbox("Choisir l'école", SCHOOLS)
        uploaded_excel = st.file_uploader(
            "Importer le fichier Excel", type=["xls", "xlsx"]
        )

        if st.button("🚀 Lancer le traitement global", type="primary"):
            if not uploaded_excel:
                st.error("Veuillez importer un fichier Excel d'abord.")
            else:
                # Placer ici la logique d'extraction / traitement Pandas
                st.success(f"Traitement terminé avec succès pour {selected_school} !")

    # Sécurité supplémentaire si rôle non reconnu
    if user_role not in ["admin", "manager", "quick_user"]:
        st.warning(
            "Vous n'avez pas de permissions assignées. Contactez l'administrateur."
        )
