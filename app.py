# app.py
from io import BytesIO
import re
import pandas as pd
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="Générateur Manuel Rapide", page_icon="🛠️", layout="centered"
)

# Initialisation du session_state pour permettre la réinitialisation
if "manual_code_input" not in st.session_state:
    st.session_state["manual_code_input"] = ""
if "manual_emails_input" not in st.session_state:
    st.session_state["manual_emails_input"] = ""


def reset_form():
    """Efface le contenu des champs de saisie."""
    st.session_state["manual_code_input"] = ""
    st.session_state["manual_emails_input"] = ""


st.title("🛠️ GÉNÉRATEUR MANUEL RAPIDE")
st.write("Attribuez facilement un code de cours à une liste d'adresses email.")

st.markdown("---")

# Expression régulière pour valider le format standard d'un email
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def is_valid_email(email: str) -> bool:
    """Vérifie le format d'un email."""
    return re.match(EMAIL_REGEX, email) is not None


# 2. Formulaire de saisie
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
    generate_btn = st.button("🚀 Générer le fichier CSV", type="primary")

with btn_col2:
    st.button("🗑️ Vider", on_click=reset_form, help="Réinitialiser le formulaire")

# 3. Traitement, Validation et Dédoublonnage
if generate_btn:
    if manual_code and manual_emails_input:
        # Nettoyage de la saisie utilisateur (passage en minuscules pour détecter les doublons)
        raw_emails = [
            e.strip().lower()
            for e in manual_emails_input.splitlines()
            if e.strip()
        ]

        # Filtrage des formats d'email valides / invalides
        valid_emails = [e for e in raw_emails if is_valid_email(e)]
        invalid_emails = [e for e in raw_emails if not is_valid_email(e)]

        # Dédoublonnage tout en préservant l'ordre d'origine
        unique_valid_emails = list(dict.fromkeys(valid_emails))
        duplicates_count = len(valid_emails) - len(unique_valid_emails)

        # Retours d'information à l'utilisateur
        if invalid_emails:
            st.warning(
                f"⚠️ {len(invalid_emails)} email(s) au format invalide ignoré(s) : "
                + ", ".join(invalid_emails)
            )

        if duplicates_count > 0:
            st.info(
                f"ℹ️ {duplicates_count} doublon(s) détecté(s) et supprimé(s) automatiquement."
            )

        if unique_valid_emails:
            # Création du DataFrame Pandas avec la liste nettoyée et unique
            manual_df = pd.DataFrame(
                {
                    "code": [manual_code] * len(unique_valid_emails),
                    "email": unique_valid_emails,
                }
            )

            # Conversion du DataFrame en buffer CSV
            csv_buffer = BytesIO()
            manual_df.to_csv(
                csv_buffer, index=False, header=False, encoding="utf-8-sig"
            )
            csv_buffer.seek(0)

            st.success(
                f"✅ CSV généré avec succès pour {len(unique_valid_emails)} email(s) unique(s) !"
            )

            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv_buffer,
                file_name=f"manuel_{manual_code}.csv",
                mime="text/csv",
            )
        else:
            st.error("Aucun email valide n'a été trouvé dans votre saisie.")
    else:
        st.error("Veuillez remplir le code de cours et la liste d'emails.")
