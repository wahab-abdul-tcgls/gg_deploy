import streamlit as st

# Set page configuration
st.set_page_config(page_title="Gist-Genie", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .card {
            border: 2px solid #d3d3d3;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .card h3 {
            margin: 0;
            color: #0073e6;
            font-size: 1.3em;
        }
        .card p {
            color: #555555;
            font-size: 1em;
            margin: 10px 0;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        .button-container button {
            background-color: #007acc;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# Example function to display each article card
def display_article_card(column, title, image_url, ai_summary, question1, question2):
    with column:
        st.markdown(f"""
        <div class="card">
            <h3>{title}</h3>
            <img src="{image_url}" style="width:100%; border-radius: 10px; margin-bottom: 15px;">
            <p>{ai_summary}</p>
            <div class="button-container">
                <button onclick="window.location.href='#'">{question1}</button>
                <button onclick="window.location.href='#'">{question2}</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Sample data for 3 articles
articles = [
    {
        "title": "Air Jordan 1 - Now available in India",
        "image_url": "https://link-to-image.com/image1.jpg",  # Replace with actual image URL
        "ai_summary": "The iconic Air Jordan 1 has finally arrived in India. Known for its high-top silhouette and bold colorways, it is a staple in streetwear fashion.",
        "question1": "What is the price?",
        "question2": "Where can I buy them?"
    },
    {
        "title": "New Balance 550 - A Retro Comeback",
        "image_url": "https://link-to-image.com/image2.jpg",  # Replace with actual image URL
        "ai_summary": "The New Balance 550 returns with retro aesthetics that are making waves in the sneaker community.",
        "question1": "What colors are available?",
        "question2": "Is it suitable for running?"
    },
    {
        "title": "Adidas Yeezy Boost - Limited Edition Drop",
        "image_url": "https://link-to-image.com/image3.jpg",  # Replace with actual image URL
        "ai_summary": "Adidas Yeezy Boost continues to redefine footwear with its limited-edition drops and futuristic designs.",
        "question1": "Where can I find the latest drop?",
        "question2": "What sizes are available?"
    }
]

# Displaying the 3 articles side-by-side
st.markdown("<h2 style='text-align: center; color: #663399;'>GIST-GENIE ✨</h2>", unsafe_allow_html=True)
columns = st.columns(3)

for i, article in enumerate(articles):
    display_article_card(
        columns[i],
        article["title"],
        article["image_url"],
        article["ai_summary"],
        article["question1"],
        article["question2"]
    )

# Bottom input box for user queries
st.text_input("Ask me anything...", key="user_input", placeholder="Ask me anything...")
st.button("Send", key="send_button")
