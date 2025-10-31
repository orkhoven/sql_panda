import pandas as pd
from pandasql import sqldf
import streamlit as st

pysqldf = lambda q: sqldf(q, globals())

st.title("SQL on pandas with pandasql")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded_file:
    st.info("Please upload one or more CSV files.")
    st.stop()

df = pd.read_csv(uploaded_file)
st.write("Data preview:")
st.dataframe(df.head())

st.write("Schema:")
st.write(df.dtypes)

query = st.text_area("Enter SQL SELECT query here:", height=150)

if st.button("Run query"):
    if not query.strip().lower().startswith("select"):
        st.error("Only SELECT queries are allowed.")
    else:
        try:
            result = pysqldf(query)
            st.write("Result:")
            st.dataframe(result)
            csv = result.to_csv(index=False).encode('utf-8')
            st.download_button("Download result as CSV", data=csv, file_name='result.csv', mime='text/csv')
        except Exception as e:
            st.error(f"Error executing query: {e}")
