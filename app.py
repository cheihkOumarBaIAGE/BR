# app.py
from io import BytesIO
import re
import pandas as pd
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Générateur Manuel Rapide", page_icon="🛠️", layout="centered"
)

# Initialisation des variables dans le session_state
if "manual_code_input" not in st.session_state:
    st.session_state["manual_code_input"] = ""
if "manual_emails_input" not in st.session_state:
    st.session_state["manual_emails_input"] = ""
if "invalid_corrections" not in st.session_state:
    st.session_state["invalid_corrections"] = {}


def reset_form():
    """Efface le contenu des champs de saisie et les réinitialisations."""
    st.session_state["manual_code_input"] = ""
    st.session_state["manual_emails_input"] = ""
    st.session_state["invalid_corrections"] = {}


st.title("🛠️ GÉNÉRATEUR MANUEL RAPIDE")
st.write("Attribuez facilement un code de cours à une liste d'adresses email.")

st.markdown("---")

# Expression régulière pour valider le format standard d'un email
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def is_valid_email(email: str) -> bool:
    """Vérifie le format d'un email."""
    return re.match(EMAIL_REGEX, email) is not None


# 2. Formulaire de saisie principal
col1, col2 = st.columns([1, 2])

with col1:
    manual_code = st.text_input(
        "Code du cours",
        placeholder="ex: INF101",
        key="manual_code_input",
    )

with col2:
    manual_emails_input = st.text_area(
        "Emails (un par ligne)",
        placeholder="etudiant1@exemple.com\netudiant2@exemple.com",
        height=150,
        key="manual_emails_input",
    )

# Boutons d'action
btn_col1, btn_col2 = st.columns([3, 1])

with btn_col1:
    generate_btn = st.button("🚀 Analyser & Générer le CSV", type="primary")

with btn_col2:
    st.button("🗑️ Vider", on_click=reset_form, help="Réinitialiser le formulaire")

# 3. Traitement, Détection & Correction
if generate_btn or "invalid_emails_list" in st.session_state:
    if manual_code and manual_emails_input:
        # Traitement initial lors du clic sur le bouton principal
        if generate_btn:
            raw_emails = [
                e.strip().lower()
                for e in manual_emails_input.splitlines()
                if e.strip()
            ]

            valid_emails = [e for e in raw_emails if is_valid_email(e)]
            invalid_emails = [e for e in raw_emails if not is_valid_email(e)]

            st.session_state["valid_emails_list"] = valid_emails
            st.session_state["invalid_emails_list"] = invalid_emails
            st.session_state["invalid_corrections"] = {
                e: e for e in invalid_emails
            }

        valid_emails = st.session_state.get("valid_emails_list", [])
        invalid_emails = st.session_state.get("invalid_emails_list", [])

        # --- SECTION DE CORRECTION DES EMAILS INVALIDES ---
        if invalid_emails:
            st.warning(
                f"⚠️ **{len(invalid_emails)} email(s) au format invalide détecté(s).** "
                "Vous pouvez les corriger directement ci-dessous :"
            )

            # Formulaire d'édition pour les adresses erronées
            with st.expander(
                "✏️ Modifier les adresses incorrectes", expanded=True
            ):
                corrected_from_form = []
                for idx, bad_email in enumerate(invalid_emails):
                    new_email = st.text_input(
                        f"Corriger l'adresse #{idx+1}",
                        value=st.session_state["invalid_corrections"].get(
                            bad_email, bad_email
                        ),
                        key=f"corr_{idx}",
                    )
                    st.session_state["invalid_corrections"][bad_email] = (
                        new_email.strip().lower()
                    )

                if st.button("🔄 Appliquer les corrections"):
                    st.rerun()

            # Récupération des emails corrigés qui sont maintenant valides
            fixed_emails = []
            still_invalid = []
            for original, corrected in st.session_state[
                "invalid_corrections"
            ].items():
                if corrected and is_valid_email(corrected):
                    fixed_emails.append(corrected)
                elif corrected:
                    still_invalid.append(corrected)

            if still_invalid:
                st.error(
                    f"Certaines adresses sont toujours invalides : {', '.join(still_invalid)}"
                )

            # Fusion des emails valides initiaux + les emails corrigés
            all_valid_emails = valid_emails + fixed_emails
        else:
            all_valid_emails = valid_emails

        # Dédoublonnage des emails valides (conservant l'ordre)
        unique_emails = list(dict.fromkeys(all_valid_emails))
        duplicates_count = len(all_valid_emails) - len(unique_emails)

        if duplicates_count > 0:
            st.info(
                f"ℹ️ {duplicates_count} doublon(s) supprimé(s) automatiquement."
            )

        # Génération du CSV si au moins une adresse valide existe
        if unique_emails:
            manual_df = pd.DataFrame(
                {
                    "code": [manual_code] * len(unique_emails),
                    "email": unique_emails,
                }
            )

            csv_buffer = BytesIO()
            manual_df.to_csv(
                csv_buffer, index=False, header=False, encoding="utf-8-sig"
            )
            csv_buffer.seek(0)

            st.success(
                f"✅ CSV prêt avec **{len(unique_emails)} email(s) valide(s)** !"
            )

            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv_buffer,
                file_name=f"manuel_{manual_code}.csv",
                mime="text/csv",
            )
        else:
            st.error("Aucun email valide n'est disponible pour la génération.")
    else:
        st.error("Veuillez remplir le code de cours et la liste d'emails.")
