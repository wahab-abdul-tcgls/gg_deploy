import streamlit as st
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os
import boto3
from datetime import datetime
import random
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# TEXT_MODEL = os.getenv("TEXT_MODEL")
SERVICE_NAME = os.getenv("AWS_SERVICE_NAME")
REGION_NAME = os.getenv("AWS_REGION_NAME")
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
TEXT_MODEL = os.getenv("TEXT_MODE")
MONGODB_KEY= os.getenv("MONGODB_KEY")


# MongoDB Connection
password = quote_plus(MONGODB_KEY)
uri = f"mongodb+srv://wahababdul:{password}@gistgenie.9o7cr.mongodb.net/?retryWrites=true&w=majority&appName=Gistgenie"
client = MongoClient(uri)
db = client['rss_feed_database']
articles_collection = db['articles']

# AWS Bedrock Configuration
client = boto3.client(service_name=SERVICE_NAME, region_name=REGION_NAME,
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=ACCESS_SECRET_KEY)

# Prompt template for generating responses
prompt_template = """[INST]Use the following pieces of content to answer the question at the end. Strictly follow the following rules:
1. If the answer is not within the context knowledge, kindly state that you do not know, rather than attempting to fabricate a response.
2. If you find the answer, please craft a detailed and concise response to the question at the end. Aim for a summary, ensuring that your explanation is thorough.[/INST]

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
        response = client.invoke_model(
            body=json.dumps(body),
            modelId=TEXT_MODEL
        )
        response_body = json.loads(response["body"].read())
        outputs = response_body.get("outputs")
        generated_text = outputs[0]['text'].replace('"', '')
        generated_text = generated_text.split('\n', 1)[0].strip()
        return generated_text
    except Exception as e:
        return {"error": str(e)}

# Fetch random articles from MongoDB
def fetch_random_articles(limit=3):
    articles = articles_collection.aggregate([{"$sample": {"size": limit}}])
    formatted_articles = []
    for article in articles:
        title = article.get("title", "No Title")
        ai_summary = article.get("ai_summary", "No Summary Available")
        pub_date = article.get("pub_date", "No Publication Date")
        link = article.get("link", "#")
        content = article.get("full_content", "No Content Available")
        # Format date for display
        formatted_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
        formatted_articles.append((title, ai_summary, formatted_date, link, content))
    return formatted_articles

# Streamlit UI
def streamlit_ui():
    st.set_page_config(page_title="Gistgenie", layout="wide")
    st.header("GIST-GENIE: Ziki 1.0")

    # Initialize session state for the selected article, chat history, and articles
    if "selected_content" not in st.session_state:
        st.session_state.selected_content = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "articles" not in st.session_state:
        st.session_state.articles = fetch_random_articles()

    with st.sidebar:
        st.title("Latest Articles")
        
        # Refresh Button to load random articles
        if st.button("Refresh Articles"):
            st.session_state.articles = fetch_random_articles()
            st.session_state.selected_content = None
            st.session_state.chat_history = []

        for title, ai_summary, pub_date, link, content in st.session_state.articles:
            if st.button(title):
                st.session_state.selected_content = content
                st.session_state.chat_history = []  # Reset chat history when a new article is selected

                # Display article preview in the sidebar
                st.markdown(f"""
                    <div style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                        <h2 style="margin: 0; font-size: 1.5em;">{title}</h2>
                        <p style="margin: 0; font-size: 1em; color: grey;">{ai_summary}</p>
                        <p style="margin: 0; font-size: 0.8em; color: grey; text-align: right;">{pub_date}</p>
                    </div>
                """, unsafe_allow_html=True)

    # Main content area for chat interaction
    if st.session_state.selected_content:
        user_question = st.text_input("Ask me anything about the selected article")

        if st.button("Generate Response") or user_question:
            if not user_question:
                st.error("Please enter a question.")
            else:
                with st.spinner("Processing..."):
                    context = st.session_state.selected_content
                    prompt = format_prompt(prompt_template, context, user_question)

                    # Generate response using the AI model
                    response = generate_ai_text(prompt)

                    # Update chat history
                    st.session_state.chat_history.append(("User", user_question))
                    st.session_state.chat_history.append(("GistGenie", response))

        # Display chat history
        st.write("### Chat History")
        for speaker, message in st.session_state.chat_history:
            if speaker == "User":
                st.write(f"**{speaker}:** {message}")
            else:
                st.write(f"*{speaker}:* {message}")

if __name__ == "__main__":
    streamlit_ui()
