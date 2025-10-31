import pandas as pd
import numpy as np
import seaborn as sns
from pandasql import sqldf
import streamlit as st

# === Configuration ===
st.set_page_config(page_title="Utiliser SQL et pandas ensemble", layout="wide")

# === Données ===
penguins = sns.load_dataset("penguins")
pysqldf = lambda q: sqldf(q, globals())

# === En-tête ===
st.title("Apprendre SQL et pandas ensemble — pandasql sur le jeu de données Penguins")
st.caption("Chaque exercice propose une requête SQL et son équivalent en pandas, inspiré du tutoriel DataCamp.")

# Aperçu du jeu de données
with st.expander("Aperçu du jeu de données"):
    st.dataframe(penguins.head())

with st.expander("Schéma (colonnes et types)"):
    st.write(penguins.dtypes)


# === Fonctions utilitaires ===
def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    cdf = df.copy()
    for c in cdf.columns:
        if np.issubdtype(cdf[c].dtype, np.floating):
            cdf[c] = cdf[c].round(6)
    cdf = cdf.reindex(sorted(cdf.columns), axis=1)
    if len(cdf.columns) > 0:
        cdf = cdf.sort_values(by=list(cdf.columns), kind="mergesort")
    return cdf.reset_index(drop=True)

def result_equals(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    try:
        return _normalize(a).equals(_normalize(b))
    except Exception:
        return False


# === Exercices SQL + pandas ===
EXOS = [
    {
        "titre": "Exercice 1 — Aperçu du jeu de données",
        "enonce": "Afficher les 5 premières lignes de la table penguins.",
        "solution_sql": "SELECT * FROM penguins LIMIT 5",
        "solution_pandas": "penguins.head()",
    },
    {
        "titre": "Exercice 2 — Valeurs uniques d’une colonne",
        "enonce": "Lister les espèces uniques dans la colonne species.",
        "solution_sql": "SELECT DISTINCT species FROM penguins",
        "solution_pandas": "penguins['species'].unique()",
    },
    {
        "titre": "Exercice 3 — Sélection de colonnes",
        "enonce": "Afficher species, island et bill_length_mm pour les 5 premières lignes.",
        "solution_sql": "SELECT species, island, bill_length_mm FROM penguins LIMIT 5",
        "solution_pandas": "penguins[['species','island','bill_length_mm']].head()",
    },
    {
        "titre": "Exercice 4 — Filtrer des lignes",
        "enonce": "Afficher les lignes où sex = 'Male' et flipper_length_mm > 210.",
        "solution_sql": "SELECT * FROM penguins WHERE sex = 'Male' AND flipper_length_mm > 210",
        "solution_pandas": "penguins[(penguins['sex']=='Male') & (penguins['flipper_length_mm']>210)]",
    },
    {
        "titre": "Exercice 5 — Agrégation par groupe",
        "enonce": "Afficher la longueur de bec maximale (bill_length_mm) par espèce.",
        "solution_sql": "SELECT species, MAX(bill_length_mm) AS max_bill FROM penguins GROUP BY species",
        "solution_pandas": "penguins.groupby('species', as_index=False)['bill_length_mm'].max()",
    },
    {
        "titre": "Exercice 6 — Expression arithmétique et tri",
        "enonce": "Calculer le ratio bill_length_mm / bill_depth_mm, trier décroissant et afficher 5 lignes.",
        "solution_sql": "SELECT bill_length_mm / bill_depth_mm AS ratio FROM penguins ORDER BY ratio DESC LIMIT 5",
        "solution_pandas": "penguins.assign(ratio = penguins['bill_length_mm']/penguins['bill_depth_mm']).sort_values('ratio', ascending=False).head()",
    },
]

# === État ===
if "status" not in st.session_state:
    st.session_state.status = ["locked"] * len(EXOS)
    st.session_state.step = 0

step = st.session_state.step
total = len(EXOS)

# === Barre de progression ===
def render_progress_bar():
    html = '<div style="display:flex;gap:4px;margin:10px 0;">'
    for s in st.session_state.status:
        color = "#ccc"
        if s == "solved":
            color = "#2ecc71"  # vert
        elif s == "skipped":
            color = "#e67e22"  # orange
        html += f'<div style="flex:1;height:20px;background-color:{color};border-radius:3px;"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

render_progress_bar()


# === Exercice courant ===
exo = EXOS[step]
st.subheader(exo["titre"])
st.markdown(f"**Consigne :** {exo['enonce']}")

expected_df = pysqldf(exo["solution_sql"])

sql_user = st.text_area(
    "Votre requête SQL :",
    height=160,
    placeholder="Écrivez votre requête SQL ici (utilisez la table 'penguins')",
    key=f"query_{step}"
)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    run = st.button("Exécuter")
with c2:
    show_schema = st.button("Voir colonnes")
with c3:
    give_up = st.button("Je bloque — voir la solution")

if show_schema:
    st.write("Colonnes disponibles :", list(penguins.columns))

if give_up:
    if st.session_state.status[step] != "solved":
        st.session_state.status[step] = "skipped"
    st.info("Solution attendue :")
    st.code(exo["solution_sql"], language="sql")
    st.write("Équivalent pandas :")
    st.code(exo["solution_pandas"], language="python")
    st.write("Résultat attendu :")
    st.dataframe(expected_df)
    render_progress_bar()

if run:
    try:
        if not sql_user.strip().lower().startswith("select"):
            st.error("Seules les requêtes SELECT sont autorisées.")
        else:
            user_df = pysqldf(sql_user)
            if result_equals(user_df, expected_df):
                if st.session_state.status[step] != "skipped":
                    st.session_state.status[step] = "solved"
                st.success("Résultat correct. Exercice validé.")
                st.dataframe(user_df)

                st.markdown("**Équivalent pandas pour comparaison :**")
                st.code(exo["solution_pandas"], language="python")

                if st.session_state.step < total - 1:
                    st.session_state.step += 1
                    st.rerun()
                else:
                    st.write("Tous les exercices sont terminés.")
                    render_progress_bar()
            else:
                st.error("Résultat incorrect. Réessayez.")
                with st.expander("Voir votre résultat"):
                    st.dataframe(user_df)
                with st.expander("Voir le résultat attendu"):
                    st.dataframe(expected_df)
    except Exception as e:
        st.error(f"Erreur d’exécution SQL : {e}")
