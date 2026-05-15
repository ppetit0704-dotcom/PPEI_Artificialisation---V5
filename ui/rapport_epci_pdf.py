# ============================================================
#  RAPPORT PDF EPCI — SQUELETTE DE BASE
#  (Toutes les sections seront ajoutées dans les messages suivants)
# ============================================================
import streamlit
import pandas as pd

from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Image
from io import BytesIO
import tempfile
import plotly.io as pio
from Datas.constantes import *


# ============================================================
# 1. STYLES
# ============================================================

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TitreSection",
        fontSize=18,
        leading=22,
        spaceAfter=12,
        textColor=colors.HexColor("#333333"),
        alignment=0,
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="SousTitre",
        fontSize=14,
        leading=18,
        spaceAfter=8,
        textColor=colors.HexColor("#555555"),
        fontName="Helvetica-Bold"
    ))

    styles.add(ParagraphStyle(
        name="Texte",
        fontSize=11,
        leading=14,
        spaceAfter=6,
        textColor=colors.HexColor("#222222"),
        fontName="Helvetica"
    ))

    styles.add(ParagraphStyle(
        name="TexteGris",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#666666"),
        fontName="Helvetica-Oblique"
    ))

    return styles

# ============================================================
# 2. OUTILS PDF
# ============================================================

def add_title(story, text, styles):
    story.append(Paragraph(text, styles["TitreSection"]))
    story.append(Spacer(1, 0.4 * cm))

def add_subtitle(story, text, styles):
    story.append(Paragraph(text, styles["SousTitre"]))
    story.append(Spacer(1, 0.2 * cm))

def add_paragraph(story, text, styles):
    story.append(Paragraph(text, styles["Texte"]))
    story.append(Spacer(1, 0.2 * cm))

def add_table(story, df, styles):
    data = [list(df.columns)] + df.values.tolist()
    table = Table(data, repeatRows=1)

    # ---------------------------------------------------------
    # 🔥 Correction anti-débordement : largeur max des colonnes
    # ---------------------------------------------------------
    max_width = 17 * cm   # largeur utile max dans A4 portrait
    col_width = max_width / len(df.columns)
    table._argW = [col_width] * len(df.columns)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EAEAEA")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.4 * cm))


def add_plotly_fig(story, fig):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        pio.write_image(fig, tmp.name, format="png", scale=2)
        story.append(Paragraph("<br/>", getSampleStyleSheet()["BodyText"]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Image(tmp.name, width=16*cm, height=9*cm))
        story.append(Spacer(1, 0.4 * cm))


# ============================================================
# 3. PAGE DE GARDE
# ============================================================

def build_cover_page(story, epci, region, departement, scot, styles):
    add_title(story, "Rapport territorial — Analyse & Trajectoire ZAN", styles)

    add_paragraph(story, f"<b>EPCI :</b> {epci}", styles)
    add_paragraph(story, f"<b>Région :</b> {region}", styles)
    add_paragraph(story, f"<b>Département :</b> {departement}", styles)
    add_paragraph(story, f"<b>SCoT :</b> {scot}", styles)

    story.append(PageBreak())

# ============================================================
# 4. FONCTION PRINCIPALE (VIDE POUR L’INSTANT)
# ============================================================
def generer_rapport_epci_pdf(df, region, departement, scot, epci, reduction):

    buffer = BytesIO()

    doc = BaseDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width - 0.5*cm,
        doc.height,
        id="normal"
    )

    template = PageTemplate(id="template", frames=[frame])
    doc.addPageTemplates([template])

    styles = build_styles()
    story = []

    # ---------------------------------------------------------
    # PAGE DE GARDE
    # ---------------------------------------------------------
    build_cover_page(story, epci, region, departement, scot, styles)

    # ---------------------------------------------------------
    # SECTION 1 : IDENTITÉ
    # ---------------------------------------------------------
    build_section_identite(story, df, styles)

    # ---------------------------------------------------------
    # SECTION 2 : DONNÉES GÉNÉRALES
    # ---------------------------------------------------------
    build_section_general(story, df, styles)

    # ---------------------------------------------------------
    # SECTION 3 : CONSOMMATIONS 2011–2020
    # ---------------------------------------------------------
    build_section_conso(story, df, styles)

    # ---------------------------------------------------------
    # SECTION 4 : RATIOS
    # ---------------------------------------------------------
    build_section_ratios(story, df, styles)

    # ---------------------------------------------------------
    # SECTION 5 : TRAJECTOIRE ZAN
    # ---------------------------------------------------------
    build_section_zan(story, df, reduction, styles)

    # ---------------------------------------------------------
    # SECTION 6 : SYNTHÈSE FINALE
    # ---------------------------------------------------------
    build_section_synthese(story, df, reduction, styles)

    # ---------------------------------------------------------
    # CONSTRUCTION DU PDF
    # ---------------------------------------------------------
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================
# 5. SECTION 1 — IDENTITÉ EPCI
# ============================================================

def build_section_identite(story, df, styles):
    """
    Clone PDF de Afficher_identite_commune(), mais version EPCI.
    df = dataframe déjà filtré par région / département / scot / epci
    """

    add_title(story, "1 · Identité de l’EPCI", styles)

    # Extraction des éléments
    epci_nom = df[M_EPCI_NOM].iloc[0]
    deps = sorted(df[M_DEP_NOM].dropna().unique())
    regs = sorted(df[M_REG_NOM].dropna().unique())
    communes = sorted(df[M_COM_NOM].dropna().unique())

    # Tableau identité
    data = {
        "Élément": [
            "EPCI",
            "Départements",
            "Régions",
            "Nombre de communes",
            "Communes"
        ],
        "Valeur": [
            epci_nom,
            ", ".join(deps),
            ", ".join(regs),
            len(communes),
            ", ".join(communes)
        ]
    }

    df_identite = pd.DataFrame(data)

    add_table(story, df_identite, styles)

    add_paragraph(
        story,
        "Cette section présente les éléments d'identité de l’EPCI, "
        "tels qu’affichés dans le module Streamlit.",
        styles
    )

    story.append(PageBreak())

# ============================================================
# 6. SECTION 2 — DONNÉES GÉNÉRALES (clone PDF de Afficher_general_communes)
# ============================================================

def build_section_general(story, df, styles):
    add_title(story, "2 · Données générales", styles)

    # Colonnes utilisées dans ton module
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

    colonnes_existantes = [c for c in colonnes if c in df.columns]
    df_gen = df[colonnes_existantes].copy().sort_values(M_COM_INSEE)

    # Conversion m² → ha
    if M_SURF_COM in df_gen.columns:
        df_gen[M_SURF_COM] = df_gen[M_SURF_COM] / 10000

    # Ligne TOTAL
    total_row = {col: "" for col in df_gen.columns}
    total_row[M_COM_NOM] = "TOTAL"

    for col in [M_POP_MAX, M_MEN_MAX, M_EMP_MAX, M_SURF_COM, M_ART_TOTALE]:
        if col in df_gen.columns:
            total_row[col] = df_gen[col].sum()

    df_tot = pd.concat([df_gen, pd.DataFrame([total_row])], ignore_index=True)

    # --- BADGES (version PDF = tableau synthétique) ---
    pop_totale = total_row.get(M_POP_MAX, 0)
    men_totale = total_row.get(M_MEN_MAX, 0)
    emp_totale = total_row.get(M_EMP_MAX, 0)
    surf_totale = total_row.get(M_SURF_COM, 0)
    art_totale = total_row.get(M_ART_TOTALE, 0)

    data_badges = {
        "Indicateur": [
            "Population totale",
            "Nombre de ménages",
            "Nombre d’emplois",
            "Surface totale (ha)",
            f"% Artificialisation 20{millesime_debut}-20{millesime}"
        ],
        "Valeur": [
            f"{pop_totale:,.0f}".replace(",", " "),
            f"{men_totale:,.0f}".replace(",", " "),
            f"{emp_totale:,.0f}".replace(",", " "),
            f"{surf_totale:,.2f}".replace(",", " "),
            f"{art_totale:,.2f}".replace(",", " ")
        ]
    }

    df_badges = pd.DataFrame(data_badges)
    add_subtitle(story, "Synthèse générale", styles)
    add_table(story, df_badges, styles)

    # --- TABLEAU FINAL (renommé comme dans Streamlit) ---
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

    df_final = df_tot.rename(columns=nouveaux_noms)

    add_subtitle(story, "Tableau détaillé", styles)
    add_table(story, df_final, styles)

    story.append(PageBreak())

# ============================================================
# 7. SECTION 3 — CONSOMMATIONS 2011–2020 (clone PDF)
# ============================================================

def build_section_conso(story, df, styles):
    import pandas as pd
    import plotly.express as px

    add_title(story, "3 · Consommations d’espace 2011–2020", styles)

    # -----------------------------
    # 1. Colonnes 2011–2020
    # -----------------------------
    annees = [f"{i:02d}" for i in range(11, 21)]

    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    # -----------------------------
    # 2. Calcul des consommations
    # -----------------------------
    results = []

    for _, row in df.iterrows():
        com = row[M_COM_NOM]
        data = {"Commune": com}

        for cat_name, cat_dict in categories.items():
            cols = [cat_dict[a] for a in annees if cat_dict.get(a) in df.columns]
            data[cat_name] = row[cols].sum() if cols else 0

        results.append(data)

    df_res = pd.DataFrame(results)

    # Total m² → ha
    df_res["Total"] = df_res[list(categories.keys())].sum(axis=1)
    for cat in categories.keys():
        df_res[cat] = df_res[cat] / 10000
    df_res["Total"] = df_res["Total"] / 10000

    # -----------------------------
    # 3. Tableau PDF
    # -----------------------------
    add_subtitle(story, "Tableau des consommations (ha)", styles)
    add_table(story, df_res, styles)

    # -----------------------------
    # 4. Graphique barres empilées
    # -----------------------------
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

    add_subtitle(story, "Graphique — Barres empilées", styles)
    add_plotly_fig(story, fig_bar)

    story.append(PageBreak())

# ============================================================
# 8. SECTION 4 — RATIOS (clone PDF de afficher_general_commune_ratio)
# ============================================================

def build_section_ratios(story, df, styles):
    import pandas as pd
    import plotly.express as px

    add_title(story, "4 · Ratios d’artificialisation 2011–2020", styles)

    # -----------------------------
    # 1. Colonnes 2011–2020
    # -----------------------------
    annees = [f"{i:02d}" for i in range(11, 21)]

    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    # -----------------------------
    # 2. Calcul des consommations
    # -----------------------------
    results = []

    for _, row in df.iterrows():
        com = row[M_COM_NOM]
        data = {"Commune": com}

        for cat_name, cat_dict in categories.items():
            cols = [cat_dict[a] for a in annees if cat_dict.get(a) in df.columns]
            data[cat_name] = row[cols].sum() if cols else 0

        results.append(data)

    df_res = pd.DataFrame(results)

    # Total m² → ha
    df_res["Total"] = df_res[list(categories.keys())].sum(axis=1)
    for cat in categories.keys():
        df_res[cat] = df_res[cat] / 10000
    df_res["Total"] = df_res["Total"] / 10000

    # -----------------------------
    # 3. Ratios %
    # -----------------------------
    for cat in categories.keys():
        df_res[f"% {cat}"] = (df_res[cat] / df_res["Total"] * 100).round(1)

    # -----------------------------
    # 4. Ratios démographiques
    # -----------------------------
    df_res["ha / habitant"] = df_res["Total"] / df[M_POP_MAX].values
    df_res["ha / ménage"]   = df_res["Total"] / df[M_MEN_MAX].values
    df_res["ha / emploi"]   = df_res["Total"] / df[M_EMP_MAX].values

    # -----------------------------
    # 5. Tableau PDF
    # -----------------------------
    colonnes_affichees = (
        ["Commune", "Total"]
        + list(categories.keys())
        + [f"% {c}" for c in categories.keys()]
        + ["ha / habitant", "ha / ménage", "ha / emploi"]
    )

    add_subtitle(story, "Tableau des ratios", styles)
    add_table(story, df_res[colonnes_affichees], styles)

    # -----------------------------
    # 6. Graphique radar (≤ 30 communes)
    # -----------------------------
    if len(df_res) <= 30:
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

        add_subtitle(story, "Graphique — Radar des profils communaux", styles)
        add_plotly_fig(story, fig_radar)

    else:
        add_paragraph(
            story,
            f"Graphique radar non affiché : trop de communes ({len(df_res)}). Limite = 30.",
            styles
        )

    story.append(PageBreak())

# ============================================================
# 9. SECTION 5 — TRAJECTOIRE ZAN (clone PDF de afficher_trajectoire_zan)
# ============================================================

def build_section_zan(story, df, reduction, styles):
    import pandas as pd
    import plotly.express as px

    add_title(story, "5 · Trajectoire ZAN", styles)

    # -----------------------------
    # 1. Recalcul conso 2011–2020
    # -----------------------------
    annees_ref = [f"{i:02d}" for i in range(11, 21)]
    categories = {
        "Activité": ACTIVITE,
        "Habitat": HABITAT,
        "Mixte": MIXTE,
        "Route": ROUTE,
        "Ferroviaire": FERROVIAIRE,
        "Inconnu": INCONNU
    }

    df = df.copy()
    df["Conso_2011_2020"] = 0

    for cat_dict in categories.values():
        cols = [cat_dict[a] for a in annees_ref if cat_dict.get(a) in df.columns]
        if cols:
            df["Conso_2011_2020"] += df[cols].sum(axis=1)

    df["Conso_2011_2020"] = df["Conso_2011_2020"] / 10000  # m² → ha
    conso_totale = df["Conso_2011_2020"].sum()

    # -----------------------------
    # 2. Objectif ZAN
    # -----------------------------
    reduction_ratio = reduction / 100
    objectif_zan = conso_totale * (1 - reduction_ratio)

    # -----------------------------
    # 3. Déjà consommé 2021–2023
    # -----------------------------
    annees_obs = [f"{i:02d}" for i in range(21, 24)]
    df["Conso_2021_2023"] = 0

    for cat_dict in categories.values():
        cols = [cat_dict[a] for a in annees_obs if cat_dict.get(a) in df.columns]
        if cols:
            df["Conso_2021_2023"] += df[cols].sum(axis=1)

    df["Conso_2021_2023"] = df["Conso_2021_2023"] / 10000
    conso_obs = df["Conso_2021_2023"].sum()

    reste_dispo = max(objectif_zan - conso_obs, 0)

    # -----------------------------
    # 4. Tableau synthétique (badges PDF)
    # -----------------------------
    data_badges = {
        "Indicateur": [
            "Référence 2011–2020 (ha)",
            f"Objectif 2021–2030 ({reduction:.1f} %)",
            "Déjà consommé 2021–2023 (ha)",
            "Solde disponible 2024–2030 (ha)"
        ],
        "Valeur": [
            f"{conso_totale:,.2f}".replace(",", " "),
            f"{objectif_zan:,.2f}".replace(",", " "),
            f"{conso_obs:,.2f}".replace(",", " "),
            f"{reste_dispo:,.2f}".replace(",", " ")
        ]
    }

    df_badges = pd.DataFrame(data_badges)
    add_subtitle(story, "Synthèse ZAN", styles)
    add_table(story, df_badges, styles)

    # -----------------------------
    # 5. Tableau ZAN par commune
    # -----------------------------
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

    add_subtitle(story, "Tableau ZAN par commune", styles)
    add_table(story, table, styles)

    # -----------------------------
    # 6. Graphique ZAN (≤ 30 communes)
    # -----------------------------
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

        add_subtitle(story, "Graphique — Comparaison ZAN", styles)
        add_plotly_fig(story, fig)

    else:
        add_paragraph(
            story,
            f"Graphique non affiché : trop de communes ({len(df)}). Limite = 30.",
            styles
        )

    story.append(PageBreak())

# ============================================================
# 10. SECTION 6 — SYNTHÈSE FINALE
# ============================================================

def build_section_synthese(story, df, reduction, styles):
    add_title(story, "6 · Synthèse finale", styles)

    # -----------------------------
    # 1. Récapitulatif des points clés
    # -----------------------------
    nb_communes = len(df)
    epci_nom = df[M_EPCI_NOM].iloc[0]

    texte_intro = (
        f"Cette synthèse présente les principaux enseignements du rapport d’artificialisation "
        f"pour l’EPCI <b>{epci_nom}</b>, basé sur les données consolidées des {nb_communes} communes "
        f"du territoire et sur un objectif de réduction ZAN de <b>{reduction:.1f} %</b>."
    )
    add_paragraph(story, texte_intro, styles)

    # -----------------------------
    # 2. Points clés (bullet points)
    # -----------------------------
    points = [
        "• Les consommations d’espace 2011–2020 montrent les dynamiques territoriales par catégorie (habitat, activité, mixte, etc.).",
        "• Les ratios d’artificialisation permettent de comparer les communes entre elles et d’identifier les profils atypiques.",
        "• L’objectif ZAN 2021–2030 est calculé à partir de la consommation de référence 2011–2020.",
        "• Le solde disponible 2024–2030 indique la marge restante avant dépassement de l’objectif.",
        "• Les graphiques essentiels (barres empilées, radar, ZAN) facilitent la lecture des tendances.",
    ]

    for p in points:
        add_paragraph(story, p, styles)

    # -----------------------------
    # 3. Conclusion
    # -----------------------------
    conclusion = (
        "Ce rapport constitue une base d’analyse solide pour accompagner les démarches de planification "
        "territoriale (PLUi, SCoT, stratégies foncières) et pour anticiper les trajectoires d’artificialisation "
        "à horizon 2030. Il peut être enrichi par des analyses complémentaires à l’échelle communale ou par "
        "catégorie d’usage."
    )
    add_paragraph(story, conclusion, styles)

    story.append(PageBreak())





