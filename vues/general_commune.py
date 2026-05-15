#Module EPCI : Général commune
import streamlit as st
import pandas as pd

from Datas.constantes import *
from ui.cards import badge, badgeBlue, badgeGreen, badgeRed

def Afficher_identite_commune():
    """
    Affiche la liste des communes filtrées selon les sélections
    (région, département, scot, epci, commune) + formatage.
    """

    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return None

    df = st.session_state["df"].copy()

    # --- Récupération des filtres ---
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")
    commune     = st.session_state.get("commune")   # <-- AJOUT

    # --- Affichage des filtres sélectionnés ---
    if region:
        st.markdown(f"<span style='color:orange; font-weight:bold'>Région :</span> {region}", unsafe_allow_html=True)
    if departement:
        st.markdown(f"<span style='color:orange; font-weight:bold'>Département :</span> {departement}", unsafe_allow_html=True)
    if scot:
        st.markdown(f"<span style='color:orange; font-weight:bold'>SCoT :</span> {scot}", unsafe_allow_html=True)
    if epci:
        st.markdown(f"<span style='color:orange; font-weight:bold'>EPCI :</span> {epci}", unsafe_allow_html=True)
    if commune:
        st.markdown(f"<span style='color:orange; font-weight:bold'>Commune :</span> {commune}", unsafe_allow_html=True)  # <-- AJOUT

    st.divider()

    # --- Application des filtres ---
    if region:
        df = df[df[M_REG_NOM] == region]

    if departement:
        df = df[df[M_DEP_NOM] == departement]

    if scot:
        df = df[df[M_SCOT_NOM] == scot]

    if epci:
        df = df[df[M_EPCI_NOM] == epci]

    if commune:  # <-- AJOUT
        df = df[df[M_COM_NOM] == commune]
    # --- Colonnes à afficher ---
    colonnes = [
        M_COM_INSEE,
        M_COM_NOM,
        M_REG_NOM,
        M_DEP_NOM,
        M_SCOT_NOM,
        M_EPCI_NOM
    ]

    colonnes_existantes = [c for c in colonnes if c in df.columns]
    if not colonnes_existantes:
        st.error("Aucune des colonnes demandées n'existe dans le fichier CSV.")
        return None

    # --- Table filtrée ---
    table = df[colonnes_existantes].sort_values(M_COM_INSEE).copy()

    # --- Renommage ---
    nouveaux_noms = {
        M_COM_INSEE: "Code INSEE",
        M_COM_NOM: "Commune",
        M_REG_NOM: "Région",
        M_DEP_NOM: "Département",
        M_SCOT_NOM: "SCoT",
        M_EPCI_NOM: "EPCI"
    }
    table = table.rename(columns=nouveaux_noms)

    # --- Affichage ---
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )

def Afficher_general_communes():
    """
    Affiche la liste des communes filtrées selon les sélections
    (région, département, scot, epci) + formatage + ligne TOTAL.
    """

    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return None

    df = st.session_state["df"].copy()

    # Récupération des filtres
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")
    commune     = st.session_state.get("commune") 

    # Application des filtres
    if region:
        df = df[df[M_REG_NOM] == region]

    if departement:
        df = df[df[M_DEP_NOM] == departement]

    if scot:
        df = df[df[M_SCOT_NOM] == scot]

    if epci:
        df = df[df[M_EPCI_NOM] == epci]
    
    if commune:
        df = df[df[M_COM_NOM] == commune]

    # Colonnes à afficher
    colonnes = [
        M_COM_INSEE,
        M_COM_NOM,
        M_AAV_NOM,
        M_POP_MAX,
        M_MEN_MAX,
        M_EMP_MAX,
        M_SURF_COM,
        M_ART_TOTALE
    ]
    print(colonnes)
    colonnes_existantes = [c for c in colonnes if c in df.columns]

    if not colonnes_existantes:
        st.error("Aucune des colonnes demandées n'existe dans le fichier CSV.")
        return None

    # Table filtrée
    table = df[colonnes_existantes].sort_values(M_COM_INSEE).copy()

    # Conversion m² → hectares
    if M_SURF_COM in table.columns:
        table[M_SURF_COM] = table[M_SURF_COM] / 10000

    if M_ART_TOTALE in table.columns:
        table[M_ART_TOTALE] = table[M_ART_TOTALE]

    # Colonnes numériques à totaliser
    cols_num = [M_POP_MAX, M_MEN_MAX, M_EMP_MAX, M_SURF_COM, M_ART_TOTALE]
    cols_num = [c for c in cols_num if c in table.columns]

    # Création de la ligne TOTAL
    total_row = {col: "" for col in table.columns}
    total_row[M_COM_NOM] = "TOTAL"

    for col in cols_num:
        total_row[col] = table[col].sum()

    # Ajout de la ligne TOTAL
    table_tot = pd.concat([table, pd.DataFrame([total_row])], ignore_index=True)

    st.header("📊 Données générales")
    # Totaux
    pop_totale = table_tot.loc[table_tot[M_COM_NOM] == "TOTAL", M_POP_MAX].values[0]
    men_totale = table_tot.loc[table_tot[M_COM_NOM] == "TOTAL", M_MEN_MAX].values[0]
    emp_totale = table_tot.loc[table_tot[M_COM_NOM] == "TOTAL", M_EMP_MAX].values[0]
    surf_totale = table_tot.loc[table_tot[M_COM_NOM] == "TOTAL", M_SURF_COM].values[0]
    art_totale = table_tot.loc[table_tot[M_COM_NOM] == "TOTAL", M_ART_TOTALE].values[0]

    # Formatage
    for col in cols_num:
        if col in (M_SURF_COM, M_ART_TOTALE):   # ← les deux colonnes en m² → ha
            table_tot[col] = table_tot[col].apply(
                lambda x: f"{x:,.1f}".replace(",", " ").replace(".", ",")
                if pd.notnull(x) and x != "" else x
            )
        else:
            table_tot[col] = table_tot[col].apply(
                lambda x: f"{int(x):,}".replace(",", " ")
                if pd.notnull(x) and x != "" else x
            )

    # Badges
    col1, col2, col3, col4, col5,col6 = st.columns(6)

    with col1:
        badgeGreen("Population totale", f"{pop_totale:,.0f}".replace(",", " ").replace(".", ","))

    with col2:
        badgeBlue("Nombre de ménages", f"{men_totale:,.0f}".replace(",", " ").replace(".", ","))

    with col3:
        badgeRed("Nombre d'emplois", f"{emp_totale:,.0f}".replace(",", " ").replace(".", ","))

    with col4:
        surf_totale_num = float(str(surf_totale).replace(" ", "").replace(",", "."))
        badgeGreen("Surface totale (h)", f"{surf_totale_num:,.2f}".replace(",", " ").replace(".", ","))

    with col5:
        nb_communes = len(table)
        badge("Nombre de comunes",nb_communes,"DarkGray")
    
    with col6:
        art_totale_num = float(str(art_totale).replace(" ", "").replace(",", "."))
        badge(f"% Artificialisation 20{millesime_debut}-20{millesime}",art_totale_num,"DarkGray")

    st.markdown("---")
    # Dictionnaire de renommage
    nouveaux_noms = {
        M_COM_INSEE: "Code INSEE",
        M_COM_NOM: "Commune",
        M_AAV_NOM: "AAV",
        M_POP_MAX: "Population",
        M_MEN_MAX: "Ménages",
        M_EMP_MAX: "Emplois",
        M_SURF_COM: "Surface (ha)",
        M_ART_TOTALE: f"%Conso-{millesime_debut}{millesime} (ha)"
    }
    
    # Renommage
    table_tot = table_tot.rename(columns=nouveaux_noms)
    st.dataframe(
        table_tot,
        use_container_width=True,
        hide_index=True
    )

    return

def afficher_general_commune_graph():
    import plotly.express as px

    # ================================
    # 1. Application des filtres
    # ================================
    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return None

    df = st.session_state["df"].copy()

    # Récupération des filtres
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")
    commune     = st.session_state.get("commune") 

    # Application des filtres
    if region:
        df = df[df[M_REG_NOM] == region]
    if departement:
        df = df[df[M_DEP_NOM] == departement]
    if scot:
        df = df[df[M_SCOT_NOM] == scot]
    if epci:
        df = df[df[M_EPCI_NOM] == epci]
    if commune:
        df = df[df[M_COM_NOM] == commune]

    if df.empty:
        st.warning("Aucune commune ne correspond aux filtres sélectionnés.")
        return

    # ================================
    # 2. Construction automatique des colonnes 2011–2020
    # ================================
    annees = [f"{i:02d}" for i in range(11, 21)]  # 2011 → 2020

    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    # ================================
    # 3. Calcul des consommations par commune et par catégorie
    # ================================
    results = []

    for idx, row in df.iterrows():
        com = row[M_COM_NOM]
        data = {"Commune": com}

        for cat_name, cat_dict in categories.items():
            cols = [cat_dict[a] for a in annees if cat_dict.get(a) in df.columns]
            data[cat_name] = row[cols].sum() if cols else 0

        results.append(data)

    df_res = pd.DataFrame(results)

    # ================================
    # 4. Ajout du total général (en m²)
    # ================================
    df_res["Total"] = df_res[list(categories.keys())].sum(axis=1)

    # ================================
    # 5. Conversion m² → hectares
    # ================================
    for cat in categories.keys():
        df_res[cat] = df_res[cat] / 10000

    df_res["Total"] = df_res["Total"] / 10000

    # ================================
    # 6. Affichage du tableau
    # ================================
    st.subheader("📊 Consommations d’espace 2011–2020 par commune et par catégorie (ha)")
    st.dataframe(df_res, use_container_width=True)

    # ================================
    # 7. Graphique en barres empilées
    # ================================
    df_melt = df_res.melt(
        id_vars="Commune",
        value_vars=list(categories.keys()),
        var_name="Catégorie",
        value_name="Consommation"
    )

    fig_bar = px.bar(
        df_melt,
        x="Commune",
        y="Consommation",
        color="Catégorie",
        title="Consommations d’espace 2011–2020 — Barres empilées (ha)",
        labels={"Consommation": "ha"}
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # ================================
    # 8. Camembert global
    # ================================
    total_global = df_melt.groupby("Catégorie")["Consommation"].sum().reset_index()

    fig_pie = px.pie(
        total_global,
        names="Catégorie",
        values="Consommation",
        title="Répartition totale 2011–2020 par catégorie (ha)"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

def afficher_trajectoire_zan():
    import plotly.express as px
    import pandas as pd

    # ================================
    # 1. Vérification des données
    # ================================
    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return

    df = st.session_state["df"].copy()

    # Récupération des filtres
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")
    commune     = st.session_state.get("commune") 

    # Application des filtres
    if region:
        df = df[df[M_REG_NOM] == region]
    if departement:
        df = df[df[M_DEP_NOM] == departement]
    if scot:
        df = df[df[M_SCOT_NOM] == scot]
    if epci:
        df = df[df[M_EPCI_NOM] == epci]
    if commune:
        df = df[df[M_COM_NOM] == commune]

    if df.empty:
        st.warning("Aucune commune ne correspond aux filtres sélectionnés.")
        return

    # ================================
    # 2. Recalcul de la consommation de référence 2011–2020
    # ================================
    annees_ref = [f"{i:02d}" for i in range(11, 21)]  # 2011 → 2020
    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    df["Conso_2011_2020"] = 0
    for cat_dict in categories.values():
        cols = [cat_dict[a] for a in annees_ref if cat_dict.get(a) in df.columns]
        if cols:
            df["Conso_2011_2020"] += df[cols].sum(axis=1)

    df["Conso_2011_2020"] = df["Conso_2011_2020"] / 10000  # m² → ha
    conso_totale = df["Conso_2011_2020"].sum()

    # ================================
    # 3. Sélecteur de réduction ZAN (pas de 0,5 %)
    # ================================
    def frange(start, stop, step):
        x = start
        while x <= stop:
            yield round(x, 1)
            x += step

    paliers = list(frange(40, 65, 0.5))
    paliers.append(60.7)
    paliers = sorted(set(paliers))
    index_default = paliers.index(50.0) if 50.0 in paliers else 0
    reduction = st.selectbox(
        "Sélectionnez un objectif de réduction ZAN (%)",
        paliers,
        index=index_default
    )
    reduction_ratio = reduction / 100

    # ================================
    # 4. Calculs globaux
    # ================================
    objectif_zan = conso_totale * (1 - reduction_ratio)

    # Déjà consommé (2021–2023)
    annees_obs = [f"{i:02d}" for i in range(21, 24)]
    df["Conso_2021_2023"] = 0
    for cat_dict in categories.values():
        cols = [cat_dict[a] for a in annees_obs if cat_dict.get(a) in df.columns]
        if cols:
            df["Conso_2021_2023"] += df[cols].sum(axis=1)
    df["Conso_2021_2023"] = df["Conso_2021_2023"] / 10000
    conso_obs = df["Conso_2021_2023"].sum()

    reste_dispo = max(objectif_zan - conso_obs, 0)

    # ================================
    # 5. Badges (après calcul)
    # ================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        badgeGreen("📅 Référence 2011–2020", f"{conso_totale:,.2f} ha")

    with col2:
        badgeGreen("🎯 Objectif 2021–2030", f"{objectif_zan:,.2f} ha") # f"Réduction de {reduction:.1f} %"

    with col3:
        pourcentage_atteint = (conso_obs / objectif_zan * 100) if objectif_zan else 0
        badgeRed("📊 Déjà consommé 2021–2023", f"{conso_obs:,.2f} ha") #, f"{pourcentage_atteint:.1f} % atteint"

    with col4:
        badgeGreen("⚠️ Disponible 2024–2030", f"{reste_dispo:,.2f} ha")

    st.markdown("---")

    # ================================
    # 6. TABLE UNIQUE PAR COMMUNE
    # ================================
    df["Objectif_ZAN_2021_2030"] = df["Conso_2011_2020"] * (1 - reduction_ratio)
    df["Solde_2024_2030"] = df["Objectif_ZAN_2021_2030"] - df["Conso_2021_2023"]

    table = df[[M_COM_INSEE, M_COM_NOM,
                "Conso_2011_2020",
                "Objectif_ZAN_2021_2030",
                "Conso_2021_2023",
                "Solde_2024_2030"]].copy()

    table = table.rename(columns={
        M_COM_INSEE: "Idcom",
        M_COM_NOM: "Commune",
        "Conso_2011_2020": "Conso 2011–2020 (ha)",
        "Objectif_ZAN_2021_2030": "Objectif 2021–2030 (ha)",
        "Conso_2021_2023": "Déjà consommé 2021–2023 (ha)",
        "Solde_2024_2030": "Solde 2024–2030 (ha)"
    })

    st.subheader("📋 Synthèse ZAN par commune")
    st.dataframe(table, use_container_width=True)

    # ================================
    # 7. Graphique si nb communes ≤ 30
    # ================================
    if len(df) <= 30:
        df_graph = table.melt(
            id_vars="Commune",
            value_vars=[
                "Conso 2011–2020 (ha)",
                "Objectif 2021–2030 (ha)",
                "Déjà consommé 2021–2023 (ha)",
                "Solde 2024–2030 (ha)"
            ],
            var_name="Indicateur",
            value_name="Consommation (ha)"
        )

        fig = px.bar(
            df_graph,
            x="Commune",
            y="Consommation (ha)",
            color="Indicateur",
            barmode="group",
            title="Comparaison ZAN par commune"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Graphique non affiché : trop de communes (limite = 30).")


def afficher_general_commune_ratio():
    import plotly.express as px

    # ================================
    # 1. Vérification des données
    # ================================
    if "df" not in st.session_state:
        st.warning("Aucune donnée chargée.")
        return None

    df = st.session_state["df"].copy()

    # Récupération des filtres
    region      = st.session_state.get("region")
    departement = st.session_state.get("departement")
    scot        = st.session_state.get("scot")
    epci        = st.session_state.get("epci")
    commune     = st.session_state.get("commune") 

    # Application des filtres
    if region:
        df = df[df[M_REG_NOM] == region]
    if departement:
        df = df[df[M_DEP_NOM] == departement]
    if scot:
        df = df[df[M_SCOT_NOM] == scot]
    if epci:
        df = df[df[M_EPCI_NOM] == epci]
    if commune:
        df = df[df[M_COM_NOM] == commune]

    if df.empty:
        st.warning("Aucune commune ne correspond aux filtres sélectionnés.")
        return

    # ================================
    # 2. Colonnes 2011–2020
    # ================================
    annees = [f"{i:02d}" for i in range(11, 21)]

    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    # ================================
    # 3. Calcul des consommations
    # ================================
    results = []

    for idx, row in df.iterrows():
        com = row[M_COM_NOM]
        data = {"Commune": com}

        for cat_name, cat_dict in categories.items():
            cols = [cat_dict[a] for a in annees if cat_dict.get(a) in df.columns]
            data[cat_name] = row[cols].sum() if cols else 0

        results.append(data)

    df_res = pd.DataFrame(results)

    # Total m²
    df_res["Total"] = df_res[list(categories.keys())].sum(axis=1)

    # Conversion en hectares
    for cat in categories.keys():
        df_res[cat] = df_res[cat] / 10000
    df_res["Total"] = df_res["Total"] / 10000

    # ================================
    # 4. Calcul des ratios
    # ================================
    for cat in categories.keys():
        df_res[f"% {cat}"] = (df_res[cat] / df_res["Total"] * 100).round(1)

    # Ratios démographiques
    df_res["ha / habitant"] = df_res["Total"] / df[M_POP_MAX].values
    df_res["ha / ménage"]   = df_res["Total"] / df[M_MEN_MAX].values
    df_res["ha / emploi"]   = df_res["Total"] / df[M_EMP_MAX].values

    # ================================
    # 5. Affichage tableau
    # ================================
    st.subheader("📊 Ratios d’artificialisation 2011-2020 par commune (ha & %)")

    st.dataframe(
        df_res[
            ["Commune", "Total"]
            + list(categories.keys())
            + [f"% {c}" for c in categories.keys()]
            + ["ha / habitant", "ha / ménage", "ha / emploi"]
        ],
        use_container_width=True
    )
    # ================================
    # 6. Graphique radar (profil communal)
    # ================================
    MAX_COMMUNES_RADAR = 30
    nb_communes = len(df_res)

    if nb_communes > MAX_COMMUNES_RADAR:
        st.warning(
            f"Le graphique radar n'est pas affiché car il y a trop de communes "
            f"({nb_communes}).\n"
            f"Limite : {MAX_COMMUNES_RADAR} communes."
        )
        return

    df_radar = df_res.melt(
        id_vars="Commune",
        value_vars=[f"% {c}" for c in categories.keys()],
        var_name="Catégorie",
        value_name="Pourcentage"
    )

    fig_radar = px.line_polar(
        df_radar,
        r="Pourcentage",
        theta="Catégorie",
        color="Commune",
        line_close=True,
        title="Profil d’artificialisation par catégorie (%)"
    )

    st.plotly_chart(fig_radar, use_container_width=True)


