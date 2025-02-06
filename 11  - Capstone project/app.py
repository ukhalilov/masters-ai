import streamlit as st
import os
import openai
import requests
import sqlite3
import json

import matplotlib.pyplot as plt
import pandas as pd

from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
from conversation import Conversation  # Your existing 'Conversation' class

# ================================
# 1. Load environment variables
# ================================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"
DATABASE = "data/movie.sqlite"

# ================================
# 2. Database schema
# ================================
database_schema_string = """
Table: movies
Columns: id, original_title, budget, popularity, release_date, revenue, title, vote_average, vote_count, overview, tagline, uid, director_id
Table: directors
Columns: id, name, gender, uid, department
"""

# ================================
# 3. Define the function schemas
# ================================
functions = [
    {
        "name": "ask_database",
        "description": (
            "Use this function to answer user questions about MOVIES. "
            "Output should be a fully formed SQL query. "
            "Max number of rows must be 20, even if user asks for more. "
            "If user asks less, show less. By default limit should be 10."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        SQL query extracting info to answer the user's question.
                        SQL should be written using this database schema:
                        {database_schema_string}
                        The query should be returned in plain text, not in JSON.
                    """,
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "ask_tvmaze",
        "description": (
            "Use this function to answer user questions about TV SHOWS. "
            "You should search the TVMaze API and provide relevant info. "
            "For details, you can call the search endpoint e.g.: "
            "GET https://api.tvmaze.com/search/shows?q=<search_term>"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The user’s query or show name to search on TVMaze"
                }
            },
            "required": ["search_term"]
        },
    }
]

# ================================
# 4. Helpers
# ================================

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, model=MODEL):
    """
    Sends a request to the OpenAI ChatCompletion endpoint using `requests`.
    Logs the conversation to the console for debugging, but hides the system
    prompt to prevent system prompt leakage.
    """
    # --- System Prompt Leakage Prevention ---
    # Create a sanitized copy of messages, replacing system prompt content
    # with a placeholder so it doesn't leak into logs.
    sanitized_messages = []
    for msg in messages:
        if msg["role"] == "system":
            sanitized_messages.append({
                "role": "system",
                "content": "[SYSTEM MESSAGE HIDDEN]"
            })
        else:
            sanitized_messages.append(msg)

    # Print sanitized version for logging
    print("\n=== chat_completion_request called ===")
    for msg in sanitized_messages:
        role = msg["role"].upper()
        content = msg["content"]
        print(f"[{role}] {content}")
    print("======================================\n")
    # ----------------------------------------

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }

    # IMPORTANT: We still send the original (unsanitized) messages to OpenAI
    json_data = {
        "model": model,
        "messages": messages
    }
    if functions is not None:
        json_data.update({"functions": functions})

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=json_data,
    )
    response.raise_for_status()
    return response


def ask_database(conn, query):
    """
    Function to query SQLite database with provided SQL query.
    """
    print(f"[ASK_DATABASE] Executing query:\n{query}\n")
    try:
        results = conn.execute(query).fetchall()
        return results
    except Exception as e:
        raise Exception(f"SQL error: {e}")


def ask_tvmaze(search_term):
    """
    Call TVMaze API to search for TV shows by the given search term.
    Return some relevant data as a string or JSON.
    """
    print(f"[ASK_TVMAZE] Searching TVMaze for term: '{search_term}'\n")
    url = f"https://api.tvmaze.com/search/shows?q={search_term}"
    r = requests.get(url)
    if r.status_code != 200:
        return f"Error calling TVMaze API. Status code: {r.status_code}"
    data = r.json()

    # Format basic info about the first 5 shows
    results_list = []
    for item in data[:5]:
        show = item.get("show", {})
        name = show.get("name", "N/A")
        summary = show.get("summary", "N/A")
        link = show.get("url", "N/A")
        results_list.append(
            f"Title: {name}\nLink: {link}\nSummary: {summary[:200]}..."
        )

    if not results_list:
        return "No TV shows found for that query."
    return "\n\n".join(results_list)


def call_function(messages, full_message, conn):
    """
    Executes function calls using model-generated function arguments.
    """
    function_name = full_message["message"]["function_call"]["name"]
    raw_args = full_message["message"]["function_call"]["arguments"]

    print(f"[CALL_FUNCTION] Name: {function_name}, Raw arguments: {raw_args}\n")

    # Safely parse the function arguments
    try:
        function_args = json.loads(raw_args)
    except json.JSONDecodeError:
        function_args = eval(raw_args)

    if function_name == "ask_database":
        query = function_args["query"]
        try:
            results = ask_database(conn, query)
        except Exception as e:
            # If first query attempt fails, ask the model to fix the query
            messages.append(
                {
                    "role": "system",
                    "content": f"""Query: {query}
The previous query received the error {e}.
Please return a fixed SQL query in plain text.
Your response should consist of ONLY the SQL query with the separator sql_start at the beginning and sql_end at the end""",
                }
            )
            response = chat_completion_request(messages, model=MODEL)

            try:
                assistant_fix = response.json()["choices"][0]["message"]["content"]
                cleaned_query = assistant_fix.split("sql_start")[1]
                cleaned_query = cleaned_query.split("sql_end")[0]
                results = ask_database(conn, cleaned_query)
            except Exception as e2:
                return f"Second query attempt failed with error: {e2}"

        # Put the DB results into the conversation
        messages.append({"role": "function", "name": "ask_database", "content": str(results)})

        # Also store the results in session_state so we can plot them
        st.session_state.last_db_results = results

        # Get the user-facing follow-up from the model
        follow_up = chat_completion_request(messages)
        return follow_up.json()

    elif function_name == "ask_tvmaze":
        search_term = function_args["search_term"]
        api_results = ask_tvmaze(search_term)

        # Put the API results into the conversation
        messages.append({"role": "function", "name": "ask_tvmaze", "content": api_results})

        # Clear any old DB results so we don't display an outdated chart
        if "last_db_results" in st.session_state:
            del st.session_state["last_db_results"]

        follow_up = chat_completion_request(messages)
        return follow_up.json()

    else:
        raise Exception("Function does not exist and cannot be called")


def chat_completion_with_function_execution(messages, functions, conn):
    """
    Makes a ChatCompletion API call and, if a function call is requested,
    executes the function and returns the final response.
    """
    response = chat_completion_request(messages, functions)
    content = response.json()

    full_message = content["choices"][0]
    finish_reason = full_message.get("finish_reason")

    if finish_reason == "function_call":
        return call_function(messages, full_message, conn)
    else:
        return content


# ================================
# 5. Charting Helpers
# ================================
def plot_results_as_bar_chart(data, left_col, right_col, chart_title="Query Results"):
    """
    Given a list of tuples, assume the first column is a label and
    the second column is numeric. Plot a bar chart using matplotlib.
    chart_title allows custom text above the chart.
    """
    if not data:
        right_col.warning("No data to plot.")
        return

    labels = []
    values = []
    for row in data:
        if len(row) >= 2:
            label = str(row[0])
            try:
                val = float(row[1])
            except:
                continue
            labels.append(label)
            values.append(val)

    if not labels or not values:
        right_col.warning("Could not find a second numeric column to plot.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_title(chart_title)
    ax.set_ylabel("Value")

    right_col.pyplot(fig)


def get_default_top10_budgets(conn):
    """
    Return the top 10 highest-budget movies as default data (list of tuples).
    Each tuple => (title, budget).
    """
    query = """
        SELECT title, budget
        FROM movies
        ORDER BY budget DESC
        LIMIT 10;
    """
    return conn.execute(query).fetchall()


# ================================
# 6. Streamlit UI
# ================================
def main():
    # Make the UI full width
    st.set_page_config(layout="wide")

    # Page title
    st.title("Movie & TV Shows Q&A")

    # Top-of-page user input
    user_input = st.text_input("Enter your question:", value="", key="user_input_box")
    submit_clicked = st.button("Submit")

    # Prepare conversation object
    if "conversation" not in st.session_state:
        st.session_state.conversation = Conversation()

    # Ensure system message is in place
    if len(st.session_state.conversation.conversation_history) == 0:
        agent_system_message = """
You are DatabaseGPT, a helpful assistant who can answer user questions about:
1) Movies: by calling the function 'ask_database' to query the database
2) TV shows: by calling the function 'ask_tvmaze' to query the TVMaze API

If the user asks about movies, call ask_database.
If the user asks about TV shows, call ask_tvmaze.
Provide as many details as possible to your users. Begin!
"""
        st.session_state.conversation.add_message("system", agent_system_message)

    # Create bottom layout: 2 columns (left for answer, right for histogram)
    left_col, right_col = st.columns([2, 2])

    if submit_clicked:
        if not user_input.strip():
            st.warning("Please enter a question before submitting.")
            return

        # Add user's question to conversation
        st.session_state.conversation.add_message("user", user_input)

        # Connect to DB
        conn = sqlite3.connect(DATABASE)

        # Send conversation to GPT (with function execution)
        response = chat_completion_with_function_execution(
            st.session_state.conversation.conversation_history, functions, conn
        )

        # Attempt to extract final assistant message
        try:
            assistant_message = response["choices"][0]["message"]["content"]
        except Exception as e:
            assistant_message = f"Error fetching assistant's response: {e}"

        # Add assistant message to conversation
        st.session_state.conversation.add_message("assistant", assistant_message)

        # Display answer in the left column
        with left_col:
            st.markdown("### Assistant Reply")
            st.write(assistant_message)

        # If the user triggered a DB query, we can show a chart
        if "last_db_results" in st.session_state:
            plot_results_as_bar_chart(
                data=st.session_state.last_db_results,
                left_col=left_col,
                right_col=right_col,
                chart_title=f"Results for your query: {user_input}"
            )

        conn.close()

    else:
        # Nothing submitted, show default chart
        conn = sqlite3.connect(DATABASE)
        default_data = get_default_top10_budgets(conn)
        conn.close()

        # Left column: empty reply message
        with left_col:
            st.markdown("### Assistant Reply")
            st.info("Ask a question above...")

        # Right column: default bar chart of top 10 budgets
        plot_results_as_bar_chart(
            data=default_data,
            left_col=left_col,
            right_col=right_col,
            chart_title="Top 10 Highest Budget Movies"
        )


if __name__ == "__main__":
    main()
