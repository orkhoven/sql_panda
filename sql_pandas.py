import pandas as pd
import seaborn as sns
from pandasql import sqldf
import streamlit as st

# load dataset
penguins = sns.load_dataset("penguins")

# helper for SQL
pysqldf = lambda q: sqldf(q, globals())

# Pre-compute correct answer for the question
correct_query = """
SELECT DISTINCT species
FROM penguins
WHERE sex = 'Male'
  AND flipper_length_mm > 210
"""
correct_result = pysqldf(correct_query)

# UI
st.title("Interactive SQL on pandas (penguins)")

st.write("Dataset preview:")
st.dataframe(penguins.head())

st.write("Task: Write an SQL query (using table name `penguins`) to list **distinct** species of male penguins with flipper_length_mm > 210.")

user_query = st.text_area("Enter your SQL query:", height=150,
                          value="SELECT ... FROM penguins WHERE sex = 'Male' AND flipper_length_mm > 210")

if st.button("Submit answer"):
    try:
        user_result = pysqldf(user_query)
        # compare results (simple approach)
        if user_result.equals(correct_result):
            st.success("✅ Correct result!")
        else:
            st.error("❌ Result does not match expected.")
            st.write("Your result:")
            st.dataframe(user_result)
            st.write("Expected result:")
            st.dataframe(correct_result)
    except Exception as e:
        st.error(f"Error executing query: {e}")
