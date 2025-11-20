import pandas as pd
from pandasql import sqldf
from exceptions import QueryError

class DataProcessor:
    def __init__(self, dfs):
        self.dfs = dfs

    def execute_query(self, sql_query):
        try:
            # Execute SQL using pandasql
            result = sqldf(sql_query, self.dfs)
            return result
        except Exception as e:
            raise QueryError(f"SQL execution error: {str(e)}")