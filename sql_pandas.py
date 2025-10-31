import pandas as pd
import numpy as np
import seaborn as sns
import streamlit as st
from pandasql import sqldf

# === Configuration ===
st.set_page_config(page_title="Apprendre SQL via pandasql", layout="wide")

# === Données ===
penguins = sns.load_dataset("penguins")
pysqldf = lambda q: sqldf(q, globals())

# === En-tête ===
st.title("Apprendre SQL à travers pandasql")
st.caption("Rédigez du code Python qui utilise pandasql pour exécuter des requêtes SQL sur un DataFrame pandas.")

with st.expander("Aperçu du jeu de données"):
    st.dataframe(penguins.head())

with st.expander("Colonnes disponibles"):
    st.write(list(penguins.columns))

# === Fonctions utilitaires ===
def normalize(df):
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

def same_result(a, b):
    try:
        return normalize(a).equals(normalize(b))
    except Exception:
        return False

# === Banque d’exercices ===
EXOS = [
    {"titre": "Exercice 1 — Aperçu des données",
     "enonce": "Afficher les 5 premières lignes de la table `penguins`.",
     "solution_code": 'sqldf("SELECT * FROM penguins LIMIT 5")'},
    {"titre": "Exercice 2 — Valeurs uniques",
     "enonce": "Lister les espèces uniques (colonne `species`).",
     "solution_code": 'sqldf("SELECT DISTINCT species FROM penguins")'},
    {"titre": "Exercice 3 — Sélection de colonnes",
     "enonce": "Afficher `species`, `island` et `bill_length_mm` (5 premières lignes).",
     "solution_code": 'sqldf("SELECT species, island, bill_length_mm FROM penguins LIMIT 5")'},
    {"titre": "Exercice 4 — Filtres",
     "enonce": "Afficher les lignes où `sex = \'Male\'` et `flipper_length_mm > 210`.",
     "solution_code": 'sqldf("SELECT * FROM penguins WHERE sex = \'Male\' AND flipper_length_mm > 210")'},
    {"titre": "Exercice 5 — Agrégation",
     "enonce": "Afficher, par espèce, la longueur de bec maximale (`bill_length_mm`).",
     "solution_code": 'sqldf("SELECT species, MAX(bill_length_mm) AS max_bill FROM penguins GROUP BY species")'},
    {"titre": "Exercice 6 — Calcul et tri",
     "enonce": "Calculer le ratio `bill_length_mm / bill_depth_mm`, le nommer `ratio`, trier par ordre décroissant et afficher 5 lignes.",
     "solution_code": 'sqldf("SELECT bill_length_mm / bill_depth_mm AS ratio FROM penguins ORDER BY ratio DESC LIMIT 5")'},
    {"titre": "Exercice 7 — Moyenne par île",
     "enonce": "Afficher la longueur moyenne des nageoires (`flipper_length_mm`) par île.",
     "solution_code": 'sqldf("SELECT island, AVG(flipper_length_mm) AS avg_flipper FROM penguins GROUP BY island")'},
    {"titre": "Exercice 8 — Comptage par espèce et sexe",
     "enonce": "Compter le nombre de lignes par `species` et `sex` en excluant les valeurs NULL.",
     "solution_code": 'sqldf("SELECT species, sex, COUNT(*) AS n FROM penguins WHERE sex IS NOT NULL GROUP BY species, sex ORDER BY species, sex")'},
    {"titre": "Exercice 9 — Filtre avec BETWEEN",
     "enonce": "Afficher les lignes où `bill_length_mm` est entre 40 et 50 inclus.",
     "solution_code": 'sqldf("SELECT * FROM penguins WHERE bill_length_mm BETWEEN 40 AND 50")'},
    {"titre": "Exercice 10 — Tri décroissant et limite",
     "enonce": "Afficher les 10 lignes ayant les plus grandes valeurs de `bill_length_mm`.",
     "solution_code": 'sqldf("SELECT * FROM penguins ORDER BY bill_length_mm DESC LIMIT 10")'}
]

# === État ===
if "status" not in st.session_state:
    st.session_state.status = ["locked"] * len(EXOS)
    st.session_state.step = 0
    st.session_state.inputs = [""] * len(EXOS)

step = st.session_state.step
total = len(EXOS)

# === Barre de progression ===
def render_progress_bar():
    html = '<div style="display:flex;gap:4px;margin:10px 0;">'
    for s in st.session_state.status:
        color = "#ccc"
        if s == "solved":
            color = "#2ecc71"
        elif s == "skipped":
            color = "#e67e22"
        html += f'<div style="flex:1;height:20px;background-color:{color};border-radius:3px;"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

render_progress_bar()

# === Exercice courant ===
exo = EXOS[step]
st.subheader(exo["titre"])
st.markdown(f"**Consigne :** {exo['enonce']}")
expected = eval(exo["solution_code"])

user_code = st.text_area(
    "Écrivez votre code Python ci-dessous (utilisez pandasql) :",
    height=150,
    placeholder="Par exemple : sqldf('SELECT DISTINCT species FROM penguins')",
    key=f"code_{step}",
    value=st.session_state.inputs[step],
)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    run = st.button("Exécuter")
with c2:
    show_hint = st.button("Indice")
with c3:
    give_up = st.button("Je bloque — voir la solution")

if show_hint:
    st.info("Rappel : utilisez `from pandasql import sqldf` puis `sqldf('SELECT ... FROM penguins')`")

if give_up:
    if st.session_state.status[step] != "solved":
        st.session_state.status[step] = "skipped"
    st.warning("Solution attendue :")
    st.code(exo["solution_code"], language="python")
    st.write("Résultat attendu :")
    st.dataframe(expected)
    render_progress_bar()

if run:
    st.session_state.inputs[step] = user_code
    try:
        local_env = {"penguins": penguins, "pd": pd, "sqldf": sqldf}
        result = eval(user_code, {}, local_env)

        if isinstance(result, pd.DataFrame) and same_result(result, expected):
            if st.session_state.status[step] != "skipped":
                st.session_state.status[step] = "solved"
            st.success("Résultat correct.")
            st.dataframe(result)
            if st.session_state.step < total - 1:
                st.session_state.step += 1
                st.rerun()
            else:
                st.info("Tous les exercices sont terminés.")
                render_progress_bar()
        else:
            st.error("Résultat incorrect. Réessayez.")
            if isinstance(result, pd.DataFrame):
                st.write("Votre résultat :")
                st.dataframe(result)
    except Exception as e:
        st.error(f"Erreur dans le code : {e}")
