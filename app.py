"""
@author : Philippe PETIT
@version : 5.1.00
@description : Tableau de bord artificialisation Détection automatique des champs ajoutés ou de changement de millésime
"""
import sys, os

# Fix PyInstaller : plusieurs stratégies pour trouver _internal/
_candidates = [
    getattr(sys, '_MEIPASS', None),
    os.path.dirname(os.path.abspath(__file__)),
    os.path.dirname(sys.executable),
    os.path.join(os.path.dirname(sys.executable), '_internal'),
]
for _p in _candidates:
    if _p and os.path.isdir(os.path.join(_p, 'ui')) and _p not in sys.path:
        sys.path.insert(0, _p)
        break

import streamlit as st
import webbrowser
import pandas as pd
import urllib.parse
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent

from ui.cards import badge, badgeBlue, badgeGreen, badgeRed
from Datas.constantes import *
from Datas.Lire_Datas_csv import lire_csv, affiche_selecteur
from vues.general_commune import Afficher_identite_commune, Afficher_general_communes, afficher_general_commune_graph, afficher_general_commune_ratio, afficher_trajectoire_zan
#from ui.rapport_epci_pdf import generer_rapport_epci_pdf
from rapport.graph_export_pdf import *
from ui.utilitaires import get_coords_from_insee





def fermer_page_web():
    st.markdown("""
        <script>
            window.location.href = "about:blank";
        </script>
    """, unsafe_allow_html=True)


# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(
    layout="wide",
    page_title="Tableau de bord artificialisation communale (V5.1)",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# =====================================================
# HEADER
# =====================================================

def afficher_header():
    col_logo, col_texte = st.columns([1, 4])
    with col_logo:
        logo_path = ROOT_DIR / "assets" / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=210)
    with col_texte:
        st.markdown(
            """
            <div style='margin-top:10px;'>
                <h1 style='margin-bottom:0px;'>📊 Tableau de bord artificialisation communale & intercommunale</h1>
                <div style='font-size:1rem; font-weight:600; color:orange; margin-top:6px;'>
                    Version 5.1 Stable, millésime 2026<br>
                    Auteur : Philippe PETIT
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Bouton Quitter ---
    if st.button("🚪 Quitter l'application"):
        st.session_state["confirm_quit"] = True

    if st.session_state.get("confirm_quit", False):
        st.warning("Voulez-vous vraiment quitter l'application ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Oui, quitter maintenant"):
                fermer_page_web()   # ferme l'onglet
                os._exit(0)         # tue le process EXE
        with col2:
            if st.button("Non, annuler"):
                st.session_state["confirm_quit"] = False


    
        




def afficher_export_epci_pdf():
    st.subheader("📄 Export du rapport PDF — EPCI")

    # ---------------------------------------------------------
    # 1. Vérification des données
    # ---------------------------------------------------------
    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return

    df = st.session_state["df"].copy()

    # ---------------------------------------------------------
    # 2. Récupération des filtres session
    # ---------------------------------------------------------
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")

    # ---------------------------------------------------------
    # 3. Application des filtres
    # ---------------------------------------------------------
    if region:
        df = df[df[M_REG_NOM] == region]
    if departement:
        df = df[df[M_DEP_NOM] == departement]
    if scot:
        df = df[df[M_SCOT_NOM] == scot]
    if epci:
        df = df[df[M_EPCI_NOM] == epci]

    if df.empty:
        st.warning("Aucune commune ne correspond aux filtres sélectionnés.")
        return

    # ---------------------------------------------------------
    # 4. Vérification : un seul EPCI
    # ---------------------------------------------------------
    epci_uniques = df[M_EPCI_NOM].dropna().unique()
    if len(epci_uniques) != 1:
        st.warning("Merci de sélectionner un seul EPCI pour générer le rapport.")
        return

    # ---------------------------------------------------------
    # 5. Sélecteur de réduction ZAN
    # ---------------------------------------------------------
    paliers = [round(x, 1) for x in list(frange(40, 65, 0.5))] + [60.7]
    paliers = sorted(set(paliers))
    index_default = paliers.index(50.0) if 50.0 in paliers else 0

    reduction = st.selectbox(
        "Objectif de réduction ZAN (%)",
        paliers,
        index=index_default
    )

    # ---------------------------------------------------------
    # 6. Bouton de génération
    # ---------------------------------------------------------
    if st.button("🛠️ Générer le rapport PDF"):
        with st.spinner("Veuillez patienter... Construction du rapport en cours..."):

            pdf_bytes = generer_rapport_epci_pdf(
                df=df,
                region=region,
                departement=departement,
                scot=scot,
                epci=epci,
                reduction=reduction
            )

            st.session_state["epci_pdf"] = pdf_bytes

        st.success("✔ Rapport généré avec succès ! Vous pouvez maintenant le télécharger.")

    # ---------------------------------------------------------
    # 7. Bouton de téléchargement
    # ---------------------------------------------------------
    if "epci_pdf" in st.session_state:
        epci_nom = df[M_EPCI_NOM].iloc[0]

        st.download_button(
            label="📥 Télécharger le rapport PDF",
            data=st.session_state["epci_pdf"],
            file_name=f"rapport_epci_{epci_nom}.pdf",
            mime="application/pdf"
        )


# Petit utilitaire pour les paliers ZAN
def frange(start, stop, step):
    x = start
    while x <= stop:
        yield x
        x += step


# =====================================================
# MAIN
# =====================================================
afficher_header()

# --- SIDEBAR ---
with st.sidebar:
    with st.expander("📁 Import des données (cliquer pour afficher/masquer)"):
        st.header("📂 Import des données")
        df = lire_csv()
        if df is not None:
            st.session_state["df"] = df

    if "df" in st.session_state:
        df = st.session_state["df"]
        with st.expander("Sélectionnez votre territoire..."):
            result = affiche_selecteur(df)
            # plus besoin de toucher à st.session_state ici
    else:
        st.info("Veuillez importer un fichier CSV dans la barre latérale.")

# --- ZONE PRINCIPALE ---
if "df" in st.session_state:
    tab_general, tab_synthese, tab_analyse, tab_ratio, tab_export, tab_lien = st.tabs([
        "📊 Général",
        "📐 Synthèse",
        "📈 Analyse & Tendances",
        "📈 Ratios",
        "📄 Export PDF",
        "💾 Liens utiles",
    ])

    with tab_general:
        with st.spinner("Veuillez patienter... calcul en cours"):
            Afficher_identite_commune()
    with tab_synthese:
        with st.spinner("Veuillez patienter... calcul en cours"):
            Afficher_general_communes()
            afficher_general_commune_graph()
    
    with tab_analyse:
        with st.spinner("Veuillez patienter... calcul en cours"):
            afficher_trajectoire_zan()
    with tab_ratio:
        with st.spinner("Veuillez patienter... calcul en cours"):
            afficher_general_commune_ratio()

    with tab_export:
        # --- Génération du PDF ---
        df = st.session_state["df"].copy()
        # --- Récupération des filtres ---
        region      = st.session_state.get("region")
        departement = st.session_state.get("departement")
        scot        = st.session_state.get("scot")
        epci        = st.session_state.get("epci")
        commune     = st.session_state.get("commune")        
        insee       = st.session_state.get("code_insee")
        if commune :
            st.header(f"📊 {commune}")
            if st.button("📄 Générer le rapport PDF pour la commune"):
                with st.spinner("Veuillez patienter... Traitement du rapport en cours..."):
                    selection = (
                        (df[M_REG_NOM] == region) &
                        (df[M_DEP_NOM] == departement) &
                        (df[M_SCOT_NOM] == scot) &
                        (df[M_EPCI_NOM] == epci) &
                        (df[M_COM_NOM] == commune)
                    )
                    ligne_commune = df.loc[selection].iloc[0]
                    pdf_bytes = generer_rapport_pdf(ligne_commune, 0.5)
                st.success("Rapport généré avec succès ! Vous pouvez maintenant le télécharger.")

                st.download_button(
                    "📥 Télécharger le rapport PDF",
                    pdf_bytes,
                    file_name=f"rapport_{insee}.pdf",
                    mime="application/pdf"
                )
        else:
            st.caption("Veuillez sélectionner une commune")


    with tab_lien:
        df = st.session_state["df"].copy()
        # --- Récupération des filtres ---
        region      = st.session_state.get("region")
        departement = st.session_state.get("departement")
        scot        = st.session_state.get("scot")
        epci        = st.session_state.get("epci")
        epci_siret  = st.session_state.get("code_siret")
        commune     = st.session_state.get("commune")
        insee       = st.session_state.get("code_insee")
        if commune:
            
            st.write("Découvrez la commune : ", insee, " - ",commune)
            
            lat, lon = get_coords_from_insee(insee)
            url_maps = f"https://www.geoportail.gouv.fr/carte?c={lon},{lat}&z=15&l0=ORTHOIMAGERY.ORTHOPHOTOS::GEOPORTAIL:OGC:WMTS(1)&v1=PLAN.IGN::GEOPORTAIL:GPP:TMS(1;s:standard)&l2=OCSGE.COUVERTURE::GEOPORTAIL:OGC:WMTS(0.6)&l3=OCSGE.USAGE::GEOPORTAIL:OGC:WMTS(0.6)&permalink=yes"
            st.markdown(f"[🗺️ OCSGE (L'OCS GE est une base de données qui contribue au suivi de l'occupation du sol, et à celui de l'usage des sols)]({url_maps})")
            
            url_maps2 = f"https://www.geoportail-urbanisme.gouv.fr/map/#tile=1&lon={lon}&lat={lat}&zoom=12&mlon={lon}&mlat={lat}"
            st.markdown(f"[🗺️ Document d'urbanisme (Le Géoportail de l'urbanisme a pour mission de rendre accessibles les documents d'urbanisme et les servitudes d'utilité publique à tous les utilisateurs du)]({url_maps2})")

            url_maps3 = f"https://www.geoportail.gouv.fr/carte?c={lon},{lat}&z=14&l0=ORTHOIMAGERY.ORTHOPHOTOS::GEOPORTAIL:OGC:WMTS(1)&l1=LANDUSE.AGRICULTURE2021::GEOPORTAIL:OGC:WMTS(0.8)&permalink=yes"
            st.markdown(f"[🗺️ RPG 2022 (Le Registre parcellaire graphique (RPG) est un système d'information géographique représentant au 1/5000ème les îlots culturaux)]({url_maps3})")

            url_maps4 = f"https://cadastre.data.gouv.fr/map?style=ortho&parcelleId=315160000A0432#16.00/{lat}/{lon}"
            st.markdown(f"[🗺️ CADASTRE (Le cadastre est le registre public qui recense et identifie les propriétés foncières (immeuble, maison, terrain, etc.).)]({url_maps4})")

            st.divider()
            
            url_maps5 = f"https://www.insee.fr/fr/statistiques/2011101?geo=COM-{insee}"
            st.markdown(f"[🗺️ INSEE : Dossier complet commune]({url_maps5})")

            url_maps6 = f"https://www.picto-occitanie.fr/geoclip/#c=report&chapter=demo&report=r01&selgeo1=com16.{insee}&selgeo2=epci.{epci_siret}"
            st.markdown(f"[🗺️ Picto-Stat]({url_maps6})")

            url_maps7 = f"https://observatoire.atd31.fr/#c=report&chapter=demo&report=r01&selgeo1=com.{commune}&selgeo2=dep.{departement}"
            st.markdown(f"[🗺️ HGI-GeObservatoire]({url_maps7})")

            st.divider()

            url_maps8 = f"https://inpn.mnhn.fr/"
            st.markdown(f"[🗺️ Inventaire National du Patrimoine Naturel]({url_maps8})")

            url_maps8 = f"https://remonterletemps.ign.fr/comparer?lon={lon}&lat={lat}&z=13.0&layer1=10&layer2=19&mode=mag"
            st.markdown(f"[🗺️ IGN - Remonter le temps]({url_maps8})")

            st.divider()

            url_maps9 = f"https://macarte.ign.fr/carte/1X3jxe/Carte-EnR-Grand-public"
            st.markdown(f"[🗺️ Portail cartographique des énergies renouvelables (Accès grand public)]({url_maps9})")

            url_maps10 = f"http://arec-occitanie.terristory.fr/?zone=commune&maille=commune&zone_id={commune}&id_tableau=643"
            st.markdown(f"[🗺️ TerriSTORY®]({url_maps10})")

            st.divider()

            url_maps11 = f"https://explore.data.gouv.fr/fr/immobilier?onglet=carte&filtre=tous&lat={lat}&lng={lon}&zoom=12.00&code={commune}&level=commune"
            st.markdown(f"[🗺️ Explorateur de données de valeurs foncières]({url_maps11})")

        else:
            st.info("Veuillez sélectionner une commune dans le sélecteur latéral.")


else:
    st.info("Veuillez sélectionner votre territoire.")


