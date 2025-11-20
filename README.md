# Streamlit NL2SQL Data Visualization Application

This project implements a Natural Language to SQL (NL2SQL) application using Streamlit, designed to generate interactive Plotly data visualizations from natural language queries. The application leverages an Ollama-powered Large Language Model (LLM) to convert user questions into SQLite-compatible SQL queries, and a rule-based `GraphDecisionAgent` to intelligently determine the most appropriate chart type for the query results.

## Features

*   **Natural Language to SQL:** Translate plain English questions into executable SQL queries using a local LLM (Ollama).
*   **Intelligent Chart Type Determination:** A rule-based agent analyzes the SQL query results and the original user query to select the best Plotly chart type (e.g., bar, line, pie, scatter, grouped bar, multi-series).
*   **Interactive Plotly Visualizations:** Generate rich, interactive data visualizations using the Plotly library, displayed directly within the Streamlit interface.
*   **Dynamic Data Exploration:** Users can ask questions about their data and immediately see the corresponding visualizations.
*   **SQLite Compatibility:** SQL queries are specifically tailored for SQLite databases.

## Project Structure

*   `app.py`: The main Streamlit application file.
*   `llm_converter.py`: Handles the conversion of natural language queries to SQL using Ollama.
*   `graph_decision_agent.py`: Contains the logic for determining the appropriate chart type based on query results and user intent.
*   `visualizer.py`: Responsible for generating Plotly visualizations based on the determined chart type and data.
*   `data_processor.py`: Utility for loading and processing data, including the database schema.
*   `exceptions.py`: Custom exception definitions for the application.
*   `Telecom_Filled_Data_Model.xlsx`: The Excel file containing the data model used by the application.
*   `test_queries.txt`: A file containing example natural language queries for testing.

## How to Run

To set up and run this project, follow these steps:

### 1. Prerequisites

*   **Python 3.8+:** Ensure you have a compatible Python version installed.
*   **Ollama:** This application relies on Ollama for its LLM capabilities.
    *   Download and install Ollama from [ollama.com](https://ollama.com/).
    *   Pull a suitable model, for example, `llama2` or `mistral`. You can do this by running `ollama run llama2` or `ollama run mistral` in your terminal. The `llm_converter.py` is configured to use `gpt-oss:latest`, so ensure you have a model named `gpt-oss:latest` or change the model name in `llm_converter.py` to the one you have pulled.

### 2. Clone the Repository

If you haven't already, clone this repository to your local machine:

```bash
git clone <repository_url>
cd <repository_name>
```
(Replace `<repository_url>` and `<repository_name>` with the actual details of your repository.)

### 3. Install Dependencies

Navigate to the project's root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```
If `requirements.txt` is not present, you will need to create one. Based on the imports in the Python files, the key dependencies are:
*   `streamlit`
*   `pandas`
*   `plotly`
*   `ollama`
*   `openpyxl` (for reading `.xlsx` files)
*   `sqlalchemy` (for SQL execution)

You can create a `requirements.txt` with the following content:

```
streamlit
pandas
plotly
ollama
openpyxl
sqlalchemy
```
Then run:
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application

Once all dependencies are installed and Ollama is running with the correct model, you can launch the Streamlit application:

```bash
streamlit run app.py
```

This command will open the application in your web browser, usually at `http://localhost:8501`.

### 5. Interact with the Application

In the Streamlit interface, you can:

1.  Enter natural language queries into the input box.
2.  The application will convert your query to SQL, execute it, and display the results as an appropriate Plotly chart or a table.
3.  Experiment with different queries to explore the data and test the chart determination logic.

## Example Queries

You can try some of the queries from `test_queries.txt` or create your own:

*   "What are the average sales per each month?"
*   "Show me the count of customers by gender."
*   "What is the distribution of customers by region?"
*   "Show me the relationship between age and income."
*   "Compare sales by month for different product categories."
*   "Show me a line chart of sales over time."
*   "Show me a table of all customers."
*   "What are the total charges for each service type?"
*   "What is the trend of total charges over time?"
*   "Show me the average monthly revenue and average monthly expenses."
