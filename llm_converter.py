import ollama
from exceptions import QueryError

class LLMConverter:
    def __init__(self, dfs):
        self.dfs = dfs
        self.model = 'gpt-oss:latest'  # Change to your Ollama model if different

    def _get_schema_representation(self):
        schema_parts = []
        for name, df in self.dfs.items():
            columns = ", ".join(df.columns)
            schema_parts.append(f"- Table `{name}` with columns: {columns}")
        return "\n".join(schema_parts)

    def _get_relationships(self):
        relationships = []
        column_map = {}
        for name, df in self.dfs.items():
            for col in df.columns:
                if col not in column_map:
                    column_map[col] = []
                column_map[col].append(name)

        for col, tables in column_map.items():
            if len(tables) > 1:
                for i in range(len(tables)):
                    for j in range(i + 1, len(tables)):
                        relationships.append(f"- `{tables[i]}.{col}` can be joined with `{tables[j]}.{col}`")
        return "\n".join(relationships) if relationships else "No relationships inferred."


    def convert_to_sql(self, user_query):
        schema = self._get_schema_representation()
        relationships = self._get_relationships()
        prompt = f"""
        You are an expert SQL generator. You have access to a database with the following tables:
        {schema}

        The tables are related as follows:
        {relationships}

        **Important Join Information:**
        - To link `fact_billing` to `dim_sales_channel`, you must join `fact_billing` with `dim_subscriber` first using `subscriber_key`, and then `dim_subscriber` with `dim_sales_channel` using `sales_channel_key`.
        - To link `fact_billing` to `dim_product`, you must join `fact_billing` with `dim_subscriber` first using `subscriber_key`, and then `dim_subscriber` with `dim_product` using `product_key`.
        - When date-related columns (like year, month, date) are needed for `fact_billing` or `fact_usage`, always join the fact table with `dim_time` using `time_key`.

        **Important Aggregation Information:**
        - When a query asks for "average monthly" or similar time-based aggregations, ensure the result includes columns for year and month (e.g., using `strftime('%Y', date_column)` and `strftime('%m', date_column)`) and groups by these columns to provide per-month data, not a single overall average.
        - Specifically, for queries like "average monthly revenue and average monthly expenses", ensure the SQL groups by year and month to show the trend over time.
        - For "revenue", consider `fact_billing.total_charges`.
        - For "expenses", consider `fact_billing.taxes` or `fact_billing.total_due`.

        Important context for 'state' columns:
        - The `state` column in `dim_subscriber` refers to the subscriber's address state.
        - The `state` column in `dim_geography` refers to the geographical state.
        - When a query refers to a state in a geographical context (e.g., 'subscribers from California'), assume it refers to `dim_geography.state`.

        Convert the following natural language query to a valid SQL query, compatible with **SQLite**.
        Handle aggregations (e.g., AVG, SUM, COUNT), filtering (e.g., WHERE), time-series (e.g., GROUP BY date), etc.
        For date part extraction, use `strftime` (e.g., `strftime('%Y', date_column)` for year, `strftime('%m', date_column)` for month).
        Avoid functions like `EXTRACT` and `LPAD`.
        Use only the tables and columns provided. When joining tables, use the relationships described above.
        Assume date columns are in 'YYYY-MM-DD' format if applicable.
        Do not add LIMIT unless specified. Return only the SQL query, no explanations.

        Query: {user_query}
        """
        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
            sql_query = response['message']['content'].strip()
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:-3].strip()
            if not sql_query.lower().startswith("select"):
                raise QueryError("Invalid SQL generated.")
            return sql_query
        except Exception as e:
            raise QueryError(f"Ollama error: {str(e)}")