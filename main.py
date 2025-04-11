import streamlit as st
import json
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv

import json
import gzip




# Set up Google Cloud API key
API_KEY = os.getenv('API_KEY')  # Replace with your actual API key
genai.configure(api_key=API_KEY)


# Load environment variables from the .env file
load_dotenv()


# Load predefined Q&A and dataset
import json
import gzip
import os
import glob

# Paths
questions_parts_folder = r"D:\code of llm\compressed_parts"
data_path = r"data.json"

# Function to load JSON safely
def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

# Load other dataset
json_data = load_json(data_path) or {}

# Function to find answer across all `.json.gz` parts
def find_answer(user_question):
    try:
        # Loop through all .json.gz files in the folder
        for file_path in sorted(glob.glob(os.path.join(questions_parts_folder, "*.json.gz"))):
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                questions_data = json.load(f)

                # Search in current chunk
                if isinstance(questions_data, list):
                    for entry in questions_data:
                        if isinstance(entry, dict) and "q" in entry and "a" in entry:
                            if entry["q"].strip().lower() == user_question.strip().lower():
                                return entry["a"]
    except Exception as e:
        return f"Error loading compressed parts: {e}"

    return None  # Return None if no match found


# Clean Gemini response to remove "Item 1:", "Item 2:", etc.
def clean_response(text):
    return re.sub(r'Item\s*\d+\s*:\s*\n?', '', text)

# Query Gemini AI with `data.json`
def query_llm(prompt, json_data):
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    structured_prompt = (
        "You are an AI assistant analyzing structured JSON data. "
        "Answer queries based on the given JSON structure. "
        "Format responses clearly, using bullet points for multiple items.Show all relevant results "
        "Show complete data without skipping if possible.\n\n"
        "User Query: " + prompt + "\n\n"
        "Relevant Data:\n" + json.dumps(json_data, indent=2)[:800000]  # Limit JSON size
    )

    try:
        response = model.generate_content([structured_prompt])
        return response.text.strip() if response else "No response received."
    except Exception as e:
        st.error(f"Error querying LLM: {e}")
        return None

# Streamlit UI
st.title("Chat with AI AGENT")

if json_data:
    st.success("JSON data loaded successfully! Ask any query.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask a question about the data...")
if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for an answer in `questions.json`
    response = find_answer(prompt)

    # If no predefined answer, query Gemini AI with `data.json`
    if not response:
        response = query_llm(prompt, json_data)

    # Clean and display AI response
    if response:
        cleaned_response = clean_response(response)
        st.session_state.messages.append({"role": "assistant", "content": cleaned_response})
        with st.chat_message("assistant"):
            st.markdown(cleaned_response)
