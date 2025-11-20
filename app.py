import streamlit as st
from query_system import QuerySystem
from exceptions import QueryError
import pandas as pd

st.title("LLM-Powered Query and Visualization System")

excel_file = "Telecom_Filled_Data_Model.xlsx"  # Assume in same directory
system = QuerySystem(excel_file)

st.write("### Telecom Data Preview")
sheet_names = list(system.dfs.keys())
tabs = st.tabs(sheet_names)

for i, tab in enumerate(tabs):
    with tab:
        st.dataframe(system.dfs[sheet_names[i]])


user_query = st.text_input("Enter your natural language query:", "What are the average sales from 2022 till now?")

if st.button("Process Query"):
    try:
        result = system.process_query(user_query)
        st.write("Generated SQL:", result["sql_query"])
        st.write("Result Data:")
        st.dataframe(result["result_df"])
        st.write("Visualization:")
        if isinstance(result["chart_object"], list):
            if result["chart_object"]: # Check if the list is not empty
                chart_tabs = st.tabs([f"Chart {i+1}" for i in range(len(result["chart_object"]))])
                for i, chart in enumerate(result["chart_object"]):
                    with chart_tabs[i]:
                        st.plotly_chart(chart, use_container_width=True)
            else:
                st.write("No charts could be generated for this query.")
        elif isinstance(result["chart_object"], pd.DataFrame):
            st.dataframe(result["chart_object"])
        else:
            st.plotly_chart(result["chart_object"], use_container_width=True)
    except QueryError as e:
        st.error(str(e))