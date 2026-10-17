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
                f"⚠️ **{len(invalid_emails)} email(s) au
