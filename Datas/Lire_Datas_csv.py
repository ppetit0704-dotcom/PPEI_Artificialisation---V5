import streamlit as st
import pandas as pd
import chardet
import io, os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent
from .constantes import M_REG_NOM, M_DEP_NOM, M_SCOT_NOM, M_EPCI_NOM, M_COM_NOM, M_COM_INSEE, M_EPCI_SIRET


# --- Détection de l'encodage ---
def detect_encoding(file_bytes):
    result = chardet.detect(file_bytes)
    return result["encoding"]


# --- Détection du séparateur ---
def detect_separator(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8", errors="ignore")
    first_line = text.split("\n")[0]

    count_comma = first_line.count(",")
    count_semicolon = first_line.count(";")

    if count_semicolon > count_comma:
        return ";"
    elif count_comma > 0:
        return ","
    else:
        return ";"

# --- Conversion UTF-8 ---
def convert_to_utf8(uploaded_file):
    file_bytes = uploaded_file.read()
    enc = detect_encoding(file_bytes)

    st.write(f"Encodage détecté : **{enc}**")

    if enc is None:
        st.warning("Impossible de détecter l'encodage, tentative en UTF-8.")
        return io.StringIO(file_bytes.decode("utf-8", errors="ignore")), file_bytes

    if enc.lower() != "utf-8":
        st.info("Conversion en UTF-8…")
        text = file_bytes.decode(enc, errors="ignore")
        return io.StringIO(text), text.encode("utf-8")

    st.success("Fichier déjà en UTF-8.")
    return io.StringIO(file_bytes.decode("utf-8")), file_bytes


# --- Fonction utilitaire ---
def get_unique(df, col, **filters):
    sub = df.copy()
    for k, v in filters.items():
        sub = sub[sub[k] == v]
    return sorted(sub[col].dropna().unique())


# --- Lecture du CSV ---
@st.cache_data
def lire_datas(fichier_utf8,sep):
    df = pd.read_csv(fichier_utf8, sep=sep, engine="python")
    st.success("Lecture réussie.")
    return df  # FIX 3 : df toujours retourné dans le bon scope

def lire_csv():
    """Retourne un DataFrame ou None si aucun fichier n'est chargé."""
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

    if uploaded_file is None:
        return None  # FIX 1 : retour explicite si pas de fichier

    fichier_utf8, raw_bytes = convert_to_utf8(uploaded_file)

    sep = detect_separator(raw_bytes)  # FIX 2 : raw_bytes est toujours bytes
    st.write(f"Séparateur détecté : **{sep}**")

    df=lire_datas(fichier_utf8,sep)
    
    return df  # FIX 3 : df toujours retourné dans le bon scope


# --- Sélecteurs hiérarchiques ---# --- Sélecteurs hiérarchiques ---
def affiche_selecteur(df: pd.DataFrame):
    

    # Vérification des colonnes essentielles
    required_cols = [M_REG_NOM, M_DEP_NOM, M_SCOT_NOM, M_EPCI_NOM, M_COM_NOM]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Colonne manquante : {col}")
            return None

    # --- SELECTEUR REGION ---
    region = st.selectbox(
        "Région",
        options=[None] + get_unique(df, M_REG_NOM),
        format_func=lambda x: "— Choisir une région —" if x is None else x,
        key="region"
    )

    if "region_last" not in st.session_state:
        st.session_state["region_last"] = region

    if region != st.session_state["region_last"]:
        st.session_state["departement"] = None
        st.session_state["scot"] = None
        st.session_state["epci"] = None
        st.session_state["commune"] = None
        st.session_state["region_last"] = region
        st.rerun()

    if region is None:
        return None

    # --- SELECTEUR DEPARTEMENT ---
    departement = st.selectbox(
        "Département",
        options=[None] + get_unique(df, M_DEP_NOM, **{M_REG_NOM: region}),
        format_func=lambda x: "— Choisir un département —" if x is None else x,
        key="departement"
    )

    if "departement_last" not in st.session_state:
        st.session_state["departement_last"] = departement

    if departement != st.session_state["departement_last"]:
        st.session_state["scot"] = None
        st.session_state["epci"] = None
        st.session_state["commune"] = None
        st.session_state["departement_last"] = departement
        st.rerun()

    if departement is None:
        return None

    # --- SELECTEUR SCOT ---
    scot = st.selectbox(
        "SCoT",
        options=[None] + get_unique(df, M_SCOT_NOM,
                                    **{M_REG_NOM: region, M_DEP_NOM: departement}),
        format_func=lambda x: "— Choisir un SCoT —" if x is None else x,
        key="scot"
    )

    if "scot_last" not in st.session_state:
        st.session_state["scot_last"] = scot

    if scot != st.session_state["scot_last"]:
        st.session_state["epci"] = None
        st.session_state["commune"] = None
        st.session_state["scot_last"] = scot
        st.rerun()

    if scot is None:
        return None

    # --- SELECTEUR EPCI ---
    epci = st.selectbox(
        "EPCI",
        options=[None] + get_unique(df, M_EPCI_NOM,
                                    **{M_REG_NOM: region, M_DEP_NOM: departement, M_SCOT_NOM: scot}),
        format_func=lambda x: "— Choisir un EPCI —" if x is None else x,
        key="epci"
    )

    if "epci_last" not in st.session_state:
        st.session_state["epci_last"] = epci

    if epci != st.session_state["epci_last"]:
        st.session_state["commune"] = None
        st.session_state["epci_last"] = epci
        st.rerun()

    if epci is None:
        return None

    # --- SELECTEUR COMMUNE ---
    commune = st.selectbox(
        "Commune",
        options=[None] + get_unique(df, M_COM_NOM,
                                    **{M_REG_NOM: region, M_DEP_NOM: departement,
                                       M_SCOT_NOM: scot, M_EPCI_NOM: epci}),
        format_func=lambda x: "— Choisir une commune —" if x is None else x,
        key="commune"
    )

    if commune is None:
        return None
    
    # Lecture du code INSEE
    selection = (
    (df[M_REG_NOM] == region) &
    (df[M_DEP_NOM] == departement) &
    (df[M_SCOT_NOM] == scot) &
    (df[M_EPCI_NOM] == epci) &
    (df[M_COM_NOM] == commune)
    )

    code_insee = df.loc[selection, M_COM_INSEE].iloc[0]  
    code_siret = df.loc[selection, M_EPCI_SIRET].iloc[0]  

    # Stockage en session
    if st.session_state.get("code_insee") != code_insee:
        st.session_state["code_insee"] = code_insee
    if st.session_state.get("code_siret") != code_siret:
        st.session_state["code_siret"] = code_siret

    st.caption(f"✅ {region} › {departement} › {scot} › {epci} › {code_insee}-{commune}")

    return region, departement, scot, epci, commune


