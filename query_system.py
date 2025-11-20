import pandas as pd
from llm_converter import LLMConverter
from data_processor import DataProcessor
from visualizer import Visualizer
from graph_decision_agent import GraphDecisionAgent # New import
from exceptions import QueryError

class QuerySystem:
    def __init__(self, excel_file_path):
        self.dfs = pd.read_excel(excel_file_path, sheet_name=None)
        for sheet_name, df in self.dfs.items():
            df.columns = df.columns.str.strip()
        self.llm_converter = LLMConverter(self.dfs)
        self.data_processor = DataProcessor(self.dfs)
        self.visualizer = Visualizer()
        self.graph_decision_agent = GraphDecisionAgent() # Instantiate the new agent

    def process_query(self, user_query):
        try:
            # Step 1: Convert natural language to SQL using Ollama
            sql_query = self.llm_converter.convert_to_sql(user_query)
            
            # Step 2: Execute SQL on DataFrame
            result_df = self.data_processor.execute_query(sql_query)
            if result_df.empty:
                raise QueryError("No data returned from the query.")
            
            # Step 3: Generate visualization
            # Use the GraphDecisionAgent to determine the chart type
            chart_type = self.graph_decision_agent.decide_chart_type(result_df, user_query)
            chart_object = self.visualizer.generate_chart(result_df, chart_type)
            
            return {
                "sql_query": sql_query,
                "result_df": result_df,
                "chart_object": chart_object
            }
        except QueryError as e:
            raise QueryError(f"Query processing error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error: {str(e)}")