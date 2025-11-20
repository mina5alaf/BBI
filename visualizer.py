import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from exceptions import QueryError

class Visualizer:
    def determine_chart_type(self, df: pd.DataFrame, user_query: str):
        if df.empty:
            return 'table'

        num_cols = len(df.columns)
        if num_cols == 0:
            return 'table'
        
        # Identify column types based on the input DataFrame
        nominal_cols = [col for col in df.columns if 'object' in str(df[col].dtype) or 'category' in str(df[col].dtype)]
        quantitative_cols = [col for col in df.columns if 'int' in str(df[col].dtype) or 'float' in str(df[col].dtype)]
        temporal_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]

        if num_cols == 1:
            return 'bar' # Single column, value counts bar chart
        elif num_cols == 2:
            # Heuristic for 2 columns
            # Time-series
            if temporal_cols or 'time' in user_query.lower() or any(col.lower().find('date') >= 0 for col in df.columns):
                return 'line'
            # Categorical vs Quantitative
            elif (nominal_cols and quantitative_cols) and (len(nominal_cols) == 1 and len(quantitative_cols) == 1):
                if 'distribution' in user_query.lower() or 'percentage' in user_query.lower():
                    return 'pie'
                return 'bar'
            # Two quantitative
            elif len(quantitative_cols) == 2:
                return 'scatter'
            return 'bar' # Default for 2 columns
        elif num_cols >= 3:
            # Smarter detection for more than 2 columns
            if len(nominal_cols) == 1 and len(quantitative_cols) >= 1:
                # One nominal, multiple quantitative -> multi-series bar/line
                return 'multi_series_chart'
            elif len(nominal_cols) >= 2 and len(quantitative_cols) == 1:
                # Two nominal, one quantitative -> grouped bar (already handled for 3 cols)
                return 'grouped_bar'
            elif len(temporal_cols) == 1 and len(quantitative_cols) >= 1:
                # One temporal, multiple quantitative -> multi-series line chart
                return 'multi_series_chart'
            
            # Fallback to multi_charts if no single clear chart type
            return 'multi_charts'

        return 'table' # Default if no specific chart type matched

    def generate_chart(self, df: pd.DataFrame, chart_type: str):
        if df.empty:
            return "No data to visualize."
        
        if chart_type == 'table':
            return df # Return DataFrame for st.dataframe to handle

        num_cols = len(df.columns)
        if num_cols == 0:
            return df # No columns, return empty df

        # Ensure columns are strings for Plotly
        df.columns = df.columns.astype(str)

        # Helper function to create descriptive titles
        def create_title(base_title, x_col=None, y_col=None, color_col=None):
            title_parts = [base_title]
            if y_col and y_col != 'count()':
                title_parts.append(f"of {y_col.replace('_', ' ').title()}")
            if x_col and x_col != 'index':
                title_parts.append(f"by {x_col.replace('_', ' ').title()}")
            if color_col:
                title_parts.append(f"grouped by {color_col.replace('_', ' ').title()}")
            return " ".join(title_parts)

        if chart_type == 'bar':
            if num_cols >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                title = create_title("Bar Chart", x_col, y_col)
                fig = px.bar(df, x=x_col, y=y_col, title=title,
                             labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()})
            else: # Single column bar chart (e.g., value counts)
                x_col = df.columns[0]
                value_counts_df = df[x_col].value_counts().reset_index()
                value_counts_df.columns = [x_col, 'Count']
                title = create_title("Count", x_col, 'Count')
                fig = px.bar(value_counts_df, x=x_col, y='Count', title=title,
                             labels={x_col: x_col.replace('_', ' ').title(), 'Count': 'Count'})
            return fig
        
        elif chart_type == 'line':
            if num_cols >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                title = create_title("Line Chart", x_col, y_col)
                fig = px.line(df, x=x_col, y=y_col, title=title,
                              labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()})
            else: # Single column line chart (e.g., index vs value)
                x_col = df.columns[0]
                df_indexed = df.reset_index()
                title = create_title("Line Chart", 'index', x_col)
                fig = px.line(df_indexed, x='index', y=x_col, title=title,
                              labels={'index': 'Index', x_col: x_col.replace('_', ' ').title()})
            return fig

        elif chart_type == 'scatter':
            if num_cols >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                title = create_title("Scatter Plot", x_col, y_col)
                fig = px.scatter(df, x=x_col, y=y_col, title=title,
                                 labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()})
            else:
                return df # Not suitable for scatter, return table
            return fig

        elif chart_type == 'pie':
            if num_cols >= 2:
                category_col = df.columns[0]
                value_col = df.columns[1]
                title = create_title("Distribution", category_col)
                fig = px.pie(df, names=category_col, values=value_col, title=title)
            else:
                return df # Not suitable for pie, return table
            return fig
        
        elif chart_type == 'grouped_bar':
            if num_cols >= 3:
                x_col = df.columns[0]
                color_col = df.columns[1]
                y_col = df.columns[2]
                title = create_title("Grouped Bar Chart", x_col, y_col, color_col)
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, barmode='group', title=title,
                             labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title(), color_col: color_col.replace('_', ' ').title()})
            else:
                return df # Not suitable for grouped bar, return table
            return fig
        
        elif chart_type == 'multi_series_chart':
            nominal_temporal_cols = [col for col in df.columns if 'object' in str(df[col].dtype) or 'category' in str(df[col].dtype) or pd.api.types.is_datetime64_any_dtype(df[col])]
            quantitative_cols = [col for col in df.columns if 'int' in str(df[col].dtype) or 'float' in str(df[col].dtype)]

            if len(nominal_temporal_cols) >= 1 and len(quantitative_cols) >= 1:
                x_col = nominal_temporal_cols[0]
                y_cols = quantitative_cols
                
                df_melted = df.melt(id_vars=[x_col], value_vars=y_cols, var_name='Metric', value_name='Value')
                title = create_title("Multi-Series Chart", x_col, 'Value', 'Metric')
                fig = px.line(df_melted, x=x_col, y='Value', color='Metric', title=title,
                              labels={x_col: x_col.replace('_', ' ').title(), 'Value': 'Value', 'Metric': 'Metric'})
            else:
                return df # Not suitable, return table
            return fig

        elif chart_type == 'multi_charts':
            # For multi_charts, we will return a list of Plotly figures
            figures = []
            nominal_cols = [col for col in df.columns if 'object' in str(df[col].dtype) or 'category' in str(df[col].dtype)]
            quantitative_cols = [col for col in df.columns if 'int' in str(df[col].dtype) or 'float' in str(df[col].dtype)]

            # Generate bar charts for each quantitative column against each nominal column
            for q_col in quantitative_cols:
                for n_col in nominal_cols:
                    if q_col != n_col:
                        title = create_title("Bar Chart", n_col, q_col)
                        fig = px.bar(df, x=n_col, y=q_col, title=title,
                                     labels={n_col: n_col.replace('_', ' ').title(), q_col: q_col.replace('_', ' ').title()})
                        figures.append(fig)
            
            # Generate scatter plots for pairs of quantitative columns
            for i in range(len(quantitative_cols)):
                for j in range(i + 1, len(quantitative_cols)):
                    x_col = quantitative_cols[i]
                    y_col = quantitative_cols[j]
                    title = create_title("Scatter Plot", x_col, y_col)
                    fig = px.scatter(df, x=x_col, y=y_col, title=title,
                                     labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()})
                    figures.append(fig)
            
            if not figures:
                return df
            return figures # Return list of figures

        return df # Default to table if no specific chart type matched or insufficient columns