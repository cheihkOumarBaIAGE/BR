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
    """Efface le contenu des champs de saisie."""
    st.session_state["manual_code_input"] = ""
    st.session_state["manual_emails_input"] = ""
    st.session_state["invalid_corrections"] = {}


def get_special_characters(text: str) -> list[str]:
    """Extrait et retourne la liste unique des caractères spéciaux / symboles non alphanumériques."""
    # Trouve tout ce qui N'EST PAS une lettre ou un chiffre (y compris espaces, accents, symboles)
    bad_chars = re.findall(r"[^a-zA-Z0-9]", text)
    # Dédoublonnage en conservant la visibilité (remplace les espaces par 'Espace')
    display_chars = []
    for c in set(bad_chars):
        if c == " ":
            display_chars.append("Espace")
        else:
            display_chars.append(f"'{c}'")
    return display_chars


def clean_course_code(code: str) -> str:
    """Conserve uniquement les lettres et les chiffres en majuscules (supprime ', ², /, ., etc.)."""
    return re.sub(r"[^a-zA-Z0-9]", "", code).upper()


st.title("🛠️ GÉNÉRATEUR MANUEL RAPIDE")
st.write("Attribuez facilement un code de cours à une liste d'adresses email.")

st.markdown("---")

# Expression régulière restreinte au domaine @ism.edu.sn
EMAIL_ISM_REGEX = r"^[a-zA-Z0-9_.+-]+@ism\.edu\.sn$"


def is_valid_ism_email(email: str) -> bool:
    """Vérifie le format d'un email et s'assure qu'il appartient au domaine @ism.edu.sn."""
    return re.match(EMAIL_ISM_REGEX, email) is not None


# 2. Formulaire de saisie
col1, col2 = st.columns([1, 2])

with col1:
    manual_code_raw = st.text_input(
        "Code du cours",
        placeholder="ex: INF101",
        key="manual_code_input",
    )

with col2:
    manual_emails_input = st.text_area(
        "Emails (@ism.edu.sn)",
        placeholder="etudiant1@ism.edu.sn\netudiant2@ism.edu.sn",
        height=150,
        key="manual_emails_input",
    )

# Boutons d'action
btn_col1, btn_col2 = st.columns([3, 1])

with btn_col1:
    generate_btn = st.button("🚀 Analyser & Générer le CSV", type="primary")

with btn_col2:
    st.button("🗑️ Vider", on_click=reset_form, help="Réinitialiser le formulaire")

# 3. Traitement, Détection des Caractères Spéciaux & Correction
if generate_btn or "invalid_emails_list" in st.session_state:
    if manual_code_raw and manual_emails_input:
        
        # Détection des caractères spéciaux dans le code du cours
        detected_bad_chars = get_special_characters(manual_code_raw)
        
        if detected_bad_chars:
            cleaned_code_proposal = clean_course_code(manual_code_raw)
            st.warning(
                f"⚠️ **Caractère(s) non autorisé(s) détecté(s) dans le code du cours :** "
                f"{', '.join(detected_bad_chars)}"
            )
            
            if cleaned_code_proposal:
                st.info(f"💡 **Proposition de nettoyage :** `{manual_code_raw}` ➡️ **`{cleaned_code_proposal}`**")
                if st.button("🧹 Supprimer ces caractères et continuer"):
                    st.session_state["manual_code_input"] = cleaned_code_proposal
                    st.rerun()
            else:
                st.error("Le code saisi ne contient aucun caractère alphanumérique valide.")
            
            # Bloque le traitement tant que le code n'est pas nettoyé
            st.stop()
        
        manual_code = manual_code_raw.upper()

        if generate_btn:
            # Nettoyage des emails (suppression des espaces)
            raw_emails = [
                e.replace(" ", "").lower()
                for e in manual_emails_input.splitlines()
                if e.replace(" ", "") != ""
            ]

            valid_emails = [e for e in raw_emails if is_valid_ism_email(e)]
            invalid_emails = [
                e for e in raw_emails if not is_valid_ism_email(e)
            ]

            st.session_state["valid_emails_list"] = valid_emails
            st.session_state["invalid_emails_list"] = invalid_emails
            st.session_state["invalid_corrections"] = {
                e: e for e in invalid_emails
            }

        valid_emails = st.session_state.get("valid_emails_list", [])
        invalid_emails = st.session_state.get("invalid_emails_list", [])

        # Interface de correction pour les emails non conformes
        if invalid_emails:
            st.warning(
                f"⚠️ **{len(invalid_emails)} email(s) invalide(s) ou hors domaine `@ism.edu.sn` détecté(s).**"
            )

            with st.expander(
                "✏️ Modifier les adresses incorrectes", expanded=True
            ):
                for idx, bad_email in enumerate(invalid_emails):
                    new_email = st.text_input(
                        f"Corriger l'adresse #{idx+1}",
                        value=st.session_state["invalid_corrections"].get(
                            bad_email, bad_email
                        ),
                        key=f"corr_{idx}",
                    )
                    st.session_state["invalid_corrections"][bad_email] = (
                        new_email.replace(" ", "").lower()
                    )

                if st.button("🔄 Appliquer les corrections"):
                    st.rerun()

            fixed_emails = []
            still_invalid = []
            for original, corrected in st.session_state[
                "invalid_corrections"
            ].items():
                if corrected and is_valid_ism_email(corrected):
                    fixed_emails.append(corrected)
                elif corrected:
                    still_invalid.append(corrected)

            if still_invalid:
                st.error(
                    f"Certaines adresses ne respectent toujours pas la forme `@ism.edu.sn` : {', '.join(still_invalid)}"
                )

            all_valid_emails = valid_emails + fixed_emails
        else:
            all_valid_emails = valid_emails

        # Dédoublonnage des emails
        unique_emails = list(dict.fromkeys(all_valid_emails))
        duplicates_count = len(all_valid_emails) - len(unique_emails)

        if duplicates_count > 0:
            st.info(
                f"ℹ️ {duplicates_count} doublon(s) supprimé(s) automatiquement."
            )

        # Génération du DataFrame & Aperçu
        if unique_emails:
            manual_df = pd.DataFrame(
                {
                    "Code Cours": [manual_code] * len(unique_emails),
                    "Email Etudiant": unique_emails,
                }
            )

            st.success(
                f"✅ **{len(unique_emails)} email(s) valide(s)** prêt(s) pour l'exportation avec le code **{manual_code}** !"
            )

            # Aperçu du tableau
            st.subheader("👁️ Aperçu des données du CSV")
            st.dataframe(
                manual_df,
                use_container_width=True,
                hide_index=True,
            )

            # Conversion du DataFrame en buffer CSV
            csv_buffer = BytesIO()
            manual_df.to_csv(
                csv_buffer, index=False, header=False, encoding="utf-8-sig"
            )
            csv_buffer.seek(0)

            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le fichier CSV",
                data=csv_buffer,
                file_name=f"manuel_{manual_code}.csv",
                mime="text/csv",
                type="primary",
            )
        else:
            st.error(
                "Aucun email valide `@ism.edu.sn` disponible pour la génération."
            )
    else:
        st.error("Veuillez remplir le code de cours et la liste d'emails.")
