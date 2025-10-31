import pandas as pd
import seaborn as sns
from pandasql import sqldf
import streamlit as st

# SQL helper
pysqldf = lambda q: sqldf(q, globals())

# Load built-in penguins dataset
penguins = sns.load_dataset("penguins")

# Streamlit UI
st.title("SQL on pandas — Penguins Example")

st.write("### Dataset preview")
st.dataframe(penguins.head())

st.write("### Columns and types")
st.write(penguins.dtypes)

query = st.text_area("Write your SQL query below (use table name: penguins):", 
                     "SELECT species, island, bill_length_mm FROM penguins LIMIT 5", 
                     height=150)

if st.button("Run query"):
    try:
        result = pysqldf(query)
        st.write("### Query result")
        st.dataframe(result)
        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("Download result as CSV", data=csv, file_name="result.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error executing query: {e}")
