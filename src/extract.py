import streamlit as st
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os
import boto3
from datetime import datetime
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
SERVICE_NAME = os.getenv("AWS_SERVICE_NAME")
REGION_NAME = os.getenv("AWS_REGION_NAME")
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
TEXT_MODEL = os.getenv("TEXT_MODEL")
MONGODB_KEY = os.getenv("MONGODB_KEY")

# MongoDB Connection
if MONGODB_KEY is None:
    raise ValueError("MONGODB_KEY environment variable is not set.")
password = quote_plus(MONGODB_KEY)
uri = f"mongodb+srv://wahababdul:{password}@gistgenie.9o7cr.mongodb.net/?retryWrites=true&w=majority&appName=Gistgenie"
client = MongoClient(uri)
db = client['rss_feed_database']
articles_collection = db['articles']

# AWS Bedrock Configuration
bedrock_client = boto3.client(
    service_name=SERVICE_NAME,
    region_name=REGION_NAME,
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY
)

# Prompt template for generating responses
prompt_template = """[INST]Use the following pieces of content to answer the question at the end. Strictly follow these rules:
1. If the answer is not within the context knowledge, kindly state that you do not know, rather than attempting to fabricate a response.
2. If you find the answer, craft a detailed and concise response to the question at the end. Aim for a summary, ensuring that your explanation is thorough.[/INST]

{context}

Question: {question}
Helpful Answer:"""

# Function to format the prompt
def format_prompt(template, context, question):
    return template.format(context=context, question=question)

# Function to interact with AWS Bedrock to generate AI text
def generate_ai_text(prompt, max_tokens=4096, temperature=1, top_p=0.8, top_k=50):
    try:
        body = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k
        }
        response = bedrock_client.invoke_model(
            body=json.dumps(body),
            modelId=TEXT_MODEL
        )
        response_body = json.loads(response["body"].read())
        outputs = response_body.get("outputs")
        generated_text = outputs[0]['text'].replace('"', '').split('\n', 1)[0].strip()
        return generated_text
    except Exception as e:
        return {"error": str(e)}

# Function to fetch random articles with required fields from MongoDB
def fetch_random_articles(limit=3):
    articles = articles_collection.aggregate([
        {"$match": {"image_links": {"$exists": True, "$ne": ""}, "ai_summary": {"$exists": True, "$ne": ""}}},
        {"$sample": {"size": limit}}
    ])
    
    formatted_articles = []
    for article in articles:
        title = article.get("title", "No Title")
        ai_summary = article.get("ai_summary", "No Summary Available")
        image_link = article.get("image_links", "No Image Available")
        question1 = article.get("question1", "No Question 1")
        question2 = article.get("question2", "No Question 2")
        formatted_articles.append({
            "title": title,
            "ai_summary": ai_summary,
            "image_link": image_link,
            "question1": question1,
            "question2": question2
        })
    return formatted_articles

# Streamlit UI
def streamlit_ui():
    st.set_page_config(page_title="Gistgenie", layout="wide")
    st.markdown("<h2 style='text-align: center; color: #663399;'>GIST-GENIE: Ziki 1.0</h2>", unsafe_allow_html=True)

    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "articles" not in st.session_state:
        st.session_state.articles = fetch_random_articles()

    # Sidebar for chat history
    with st.sidebar:
        st.title("Chat History")
        if st.button("Refresh Articles"):
            st.session_state.articles = fetch_random_articles()
            st.session_state.chat_history = []  # Reset chat history

        # Display chat history
        for speaker, message in st.session_state.chat_history:
            st.write(f"**{speaker}:** {message}" if speaker == "User" else f"*{speaker}:* {message}")

    # Custom CSS for card styling
    st.markdown("""
        <style>
            .card {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                background-color: #f9f9f9;
                text-align: center;
            }
            .card h3 {
                color: #0073e6;
                font-size: 1.2em;
                margin-bottom: 15px;
            }
            .card p {
                color: #555555;
                font-size: 0.95em;
                margin: 10px 0;
            }
            .button-container {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 15px;
            }
            .button-container button {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    # Main content area for displaying articles
    st.subheader("Explore Articles")
    columns = st.columns(3)  # Create 3 columns for displaying articles side by side

    # Display each article in its respective column
    for i, article in enumerate(st.session_state.articles):
        title = article["title"]
        ai_summary = article["ai_summary"]
        image_link = article["image_link"]
        question1 = article["question1"]
        question2 = article["question2"]

        with columns[i]:  # Use column[i] to place each article in its own column
            st.markdown(f"""
                <div class="card">
                    <h3>{title}</h3>
                    <img src="{image_link}" alt="Article Image" style="width:100%; border-radius: 8px; margin-bottom: 15px;">
                    <p>{ai_summary}</p>
                    <div class="button-container">
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Trigger chat if question1 or question2 button is clicked
            if st.button(f"{question1}", key=f"q1_{title}"):
                st.session_state.chat_history.append(("User", question1))
                response = generate_ai_text(format_prompt(prompt_template, ai_summary, question1))
                st.session_state.chat_history.append(("GistGenie", response))

            if st.button(f"{question2}", key=f"q2_{title}"):
                st.session_state.chat_history.append(("User", question2))
                response = generate_ai_text(format_prompt(prompt_template, ai_summary, question2))
                st.session_state.chat_history.append(("GistGenie", response))

    # Custom question input at the bottom
    user_question = st.text_input("Ask me anything about the articles")
    if st.button("Send"):
        if user_question:
            st.session_state.chat_history.append(("User", user_question))
            response = generate_ai_text(format_prompt(prompt_template, ai_summary, user_question))
            st.session_state.chat_history.append(("GistGenie", response))

if __name__ == "__main__":
    streamlit_ui()

