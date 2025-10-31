import pandas as pd
import numpy as np
import seaborn as sns
from pandasql import sqldf
import streamlit as st

# --- Config ---
st.set_page_config(page_title="SQL sur pandas (pandasql) — Exercices", layout="wide")

# --- Données (comme dans le tuto DataCamp) ---
penguins = sns.load_dataset("penguins")  # table logique : 'penguins'
pysqldf = lambda q: sqldf(q, globals())

# --- UI d’en-tête ---
st.title("SQL sur pandas avec pandasql — Parcours d’exercices (Penguins)")
st.caption("Tapez vos requêtes SQL. Si le résultat est correct, l’exercice suivant se débloque.")

with st.expander("Aperçu du jeu de données"):
    st.dataframe(penguins.head())
with st.expander("Schéma (colonnes et types)"):
    st.write(penguins.dtypes)

# --- Outil de comparaison robuste (ordre, index, flottants) ---
def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    cdf = df.copy()
    # normaliser types numériques (arrondir pour éviter bruits flottants)
    for c in cdf.columns:
        if np.issubdtype(cdf[c].dtype, np.floating):
            cdf[c] = cdf[c].round(6)
    # trier colonnes par nom et lignes par toutes colonnes disponibles
    cdf = cdf.reindex(sorted(cdf.columns), axis=1)
    sort_cols = list(cdf.columns)
    # si aucune colonne (SELECT sans colonnes), garder tel quel
    if len(sort_cols) > 0:
        cdf = cdf.sort_values(by=sort_cols, kind="mergesort")
    return cdf.reset_index(drop=True)

def result_equals(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    try:
        na, nb = _normalize(a), _normalize(b)
        # gérer NaN==NaN
        return na.equals(nb)
    except Exception:
        return False

# --- Banque d’exercices (proches de ceux du tutoriel DataCamp) ---
# Remarque : les solutions sont en SQLite SQL (pandasql).
EXOS = [
    {
        "titre": "Exercice 1 — Afficher toutes les colonnes et les lignes (avec une limite).",
        "enonce": "Afficher 5 premières lignes de la table penguins.",
        "solution": "SELECT * FROM penguins LIMIT 5"
    },
    {
        "titre": "Exercice 2 — Extraire les valeurs uniques d’une colonne.",
        "enonce": "Lister les espèces uniques.",
        "solution": "SELECT DISTINCT species FROM penguins"
    },
    {
        "titre": "Exercice 3 — Sélectionner des colonnes spécifiques.",
        "enonce": "Afficher species, island, bill_length_mm (limiter à 5 lignes).",
        "solution": "SELECT species, island, bill_length_mm FROM penguins LIMIT 5"
    },
    {
        "titre": "Exercice 4 — Filtrer avec WHERE (conditions multiples).",
        "enonce": "Afficher les lignes où sex = 'Male' ET flipper_length_mm > 210.",
        "solution": "SELECT * FROM penguins WHERE sex = 'Male' AND flipper_length_mm > 210"
    },
    {
        "titre": "Exercice 5 — Agrégation et GROUP BY.",
        "enonce": "Calculer, par espèce, la longueur de bec maximale (bill_length_mm).",
        "solution": "SELECT species, MAX(bill_length_mm) AS max_bill FROM penguins GROUP BY species"
    },
    {
        "titre": "Exercice 6 — Expression arithmétique + alias + tri + limite.",
        "enonce": "Calculer le ratio bill_length_mm / bill_depth_mm, l’appeler ratio, trier décroissant et afficher 5 premières lignes.",
        "solution": "SELECT bill_length_mm / bill_depth_mm AS ratio FROM penguins ORDER BY ratio DESC LIMIT 5"
    },
    {
        "titre": "Exercice 7 — Moyenne par île.",
        "enonce": "Calculer la longueur moyenne des nageoires (flipper_length_mm) par île.",
        "solution": "SELECT island, AVG(flipper_length_mm) AS avg_flipper FROM penguins GROUP BY island"
    },
    {
        "titre": "Exercice 8 — Comptage par espèce et sexe (exclure les NULL).",
        "enonce": "Compter le nombre de lignes par species et sex, en excluant sex NULL. Ordonner par species, sex.",
        "solution": "SELECT species, sex, COUNT(*) AS n FROM penguins WHERE sex IS NOT NULL GROUP BY species, sex ORDER BY species, sex"
    },
    {
        "titre": "Exercice 9 — Filtre intervalle (BETWEEN).",
        "enonce": "Afficher les lignes où bill_length_mm est entre 40 et 50 (inclus).",
        "solution": "SELECT * FROM penguins WHERE bill_length_mm BETWEEN 40 AND 50"
    },
    {
        "titre": "Exercice 10 — Tri décroissant et limite.",
        "enonce": "Afficher les 10 lignes avec les bill_length_mm les plus élevés.",
        "solution": "SELECT * FROM penguins ORDER BY bill_length_mm DESC LIMIT 10"
    },
]

# --- État de progression ---
if "step" not in st.session_state:
    st.session_state.step = 0  # index de l'exercice à afficher

total = len(EXOS)
step = st.session_state.step

# --- Boucle d'affichage : un seul exercice visible à la fois ---
exo = EXOS[step]
st.subheader(exo["titre"])
st.markdown(f"**Consigne :** {exo['enonce']}")

# Résultat attendu (pré-calcul)
expected_df = pysqldf(exo["solution"])

# Zone de saisie en SQL
default_placeholder = "Écrivez votre requête SQL ici. Utilisez le nom de table: penguins"
# Proposer un squelette utile pour guider sans dévoiler la solution
if step == 1:  # l'exercice DISTINCT du screenshot
    default_placeholder = "SELECT DISTINCT species FROM penguins"

sql_user = st.text_area("Votre requête SQL :", height=160, placeholder=default_placeholder, key=f"q_{step}")

# Boutons d'action
c1, c2, c3 = st.columns([1,1,1])
with c1:
    run = st.button("Exécuter")
with c2:
    show_schema = st.button("Voir colonnes")
with c3:
    give_up = st.button("Je bloque — voir la solution")

if show_schema:
    st.write("Colonnes disponibles :", list(penguins.columns))

if give_up:
    st.info("Solution attendue :")
    st.code(exo["solution"], language="sql")
    st.write("Résultat attendu :")
    st.dataframe(expected_df)

if run:
    try:
        # Exiger une requête SELECT uniquement
        if not sql_user.strip().lower().startswith("select"):
            st.error("Seules les requêtes SELECT sont autorisées.")
        else:
            user_df = pysqldf(sql_user)
            if result_equals(user_df, expected_df):
                st.success("✅ Correct. Exercice validé.")
                st.dataframe(user_df)
                # Débloquer l'exercice suivant si disponible
                if st.session_state.step < total - 1:
                    st.session_state.step += 1
                    st.rerun()
                else:
                    st.balloons()
                    st.success("Parcours terminé. Bravo.")
            else:
                st.error("❌ Résultat incorrect. Réessayez.")
                with st.expander("Voir votre résultat"):
                    st.dataframe(user_df)
                with st.expander("Voir le résultat attendu"):
                    st.dataframe(expected_df)
    except Exception as e:
        st.error(f"Erreur d’exécution SQL : {e}")
