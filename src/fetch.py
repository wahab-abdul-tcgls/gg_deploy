import os
import requests
import xml.etree.ElementTree as ET
import json
from urllib.parse import quote_plus
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import boto3
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SERVICE_NAME = os.getenv("AWS_SERVICE_NAME")
REGION_NAME = os.getenv("AWS_REGION_NAME")
ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
ACCESS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
TEXT_MODEL = os.getenv("TEXT_MODE")
MONGODB_KEY = os.getenv("MONGODB_KEY")

# MongoDB Connection
password = quote_plus(MONGODB_KEY)
uri = f"mongodb+srv://wahababdul:{password}@gistgenie.9o7cr.mongodb.net/?retryWrites=true&w=majority&appName=Gistgenie"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['rss_feed_database']
collection = db['articles']

# Confirm connection to MongoDB
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

client = boto3.client(service_name=SERVICE_NAME, region_name=REGION_NAME,
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=ACCESS_SECRET_KEY)

# List of RSS feed URLs and corresponding website names
rss_feed_urls = {
    "https://www.aluxurytravelblog.com/feed/":"aluxurytravelblog",
    "https://www.healthifyme.com/blog/feed/": "healthify"

}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to scrape article content
def scrape_article_content(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li'])
    content = " ".join(tag.text for tag in tags)
    return content.strip()

# Function to clean and extract relevant part of the description
def clean_description(description):
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        paragraphs = soup.find_all('p')
        if paragraphs:
            return paragraphs[0].text.strip()
    return "No Description"

# Function to handle retries for RSS feed requests
def fetch_rss_feed(rss_feed_url, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(rss_feed_url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {rss_feed_url}: {e}")
            time.sleep(delay)
    return None


def generate_ai_summary(content, title):
    model_id = "mistral.mixtral-8x7b-instruct-v0:1"
    system_prompt = f"""You are an intelligent content summarizer. Strictly provide response in JSON format. Your task is to analyze the content titled '{title}' and generate the following:

    1. 'summary': A concise summary of the content without personal commentary or opinion in no more than 100 words.
    2. 'title': A creative title for the content.

    Generate a valid JSON with the keys 'summary' and 'title'."""
    formatted_prompt = f"<s>[INST] {system_prompt}\n content : {content}[/INST]"
    
    native_request = {
        "prompt": formatted_prompt,
        "max_tokens": 4096,
        "temperature": 0.8,
    }

    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)
        model_response = json.loads(response["body"].read())
        response_text = model_response["outputs"][0]["text"]

        # Parse the JSON response
        response_data = json.loads(response_text)

        # Extract summary and title, handling missing keys
        summary = response_data.get("summary", "Summary not found.")
        title = response_data.get("title", "Title not found.")
        
        return summary, title

    except (ClientError, Exception, json.JSONDecodeError) as e:
        print(f"ERROR: Can't invoke '{model_id}' or parse response. Reason: {e}")
        return "Summary generation failed.", "Title generation failed."


# Step 1: Store Raw Article Data First
for rss_feed_url, website_name in rss_feed_urls.items():
    try:
        rss_feed_content = fetch_rss_feed(rss_feed_url, headers)
        if not rss_feed_content:
            print(f"Skipping feed {rss_feed_url} after multiple failed attempts.")
            continue

        root = ET.fromstring(rss_feed_content)

        for item in root.findall('.//item'):
            title = item.find('title').text or 'No Title'
            description = item.find('description').text or 'No Description'
            link = item.find('link').text or 'No Link'
            pub_date = item.find('pubDate').text or 'No Publication Date'
            creator = item.find('{http://purl.org/dc/elements/1.1/}creator').text or 'No Creator'
            cleaned_description = clean_description(description)
            article_full_content = scrape_article_content(link) if link != 'No Link' else "No Content Available"

            # Store raw data in MongoDB
            article_data = {
                "title": title,
                "description": cleaned_description,
                "link": link,
                "pub_date": pub_date,
                "creator": creator,
                "website": website_name,
                "full_content": article_full_content,
                "ai_summary": None 
            }

            collection.update_one(
                {"link": link},
                {"$set": article_data},
                upsert=True
            )
            print(f"Raw data saved for article '{title}'")

    except ET.ParseError as e:
        print(f"XML parsing error for {rss_feed_url}: {e}")
    except Exception as e:
        print(f"Failed to process feed {rss_feed_url}: {e}")

print("Raw article data saved. Starting summary generation...")

def generate_content(content): 
    model_id = "mistral.mixtral-8x7b-instruct-v0:1"
    system_prompt = f"""You are an intelligent content assistant. Strictly provide the response in JSON format. Your task is to analyze the content and generate the following:
    1. 'question1' and 'question2': Two engaging short questions about the content. The questions should be short and no more than 10 words.
    2. 'image': A descriptive prompt for an image that captures the general theme content, focusing strictly on location. Strictly avoid people.  

    Generate a valid JSON with the keys 'question1', 'question2', and 'image'."""
    formatted_prompt = f"<s>[INST] {system_prompt}\n content : {content}[/INST]"
    
    native_request = {
        "prompt": formatted_prompt,
        "max_tokens": 4096,
        "temperature": 0.8,
    }

    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)
        model_response = json.loads(response["body"].read())
        response_text = model_response["outputs"][0]["text"]

        # Parse the JSON response
        response_data = json.loads(response_text)

        # Extract question1, question2, and image, handling missing keys
        question1 = response_data.get("question1", "question1 not found.")
        question2 = response_data.get("question2", "question2 not found.")
        image = response_data.get("image", "image prompt not found.")
        
        return question1, question2, image

    except (ClientError, Exception, json.JSONDecodeError) as e:
        print(f"ERROR: Can't invoke '{model_id}' or parse response. Reason: {e}")
        return "question1 generation failed.", "question2 generation failed.", "image prompt generation failed."


# Step 2: Generate AI Summaries, Titles, Questions, and Image Prompts, then Update MongoDB
articles = collection.find({"ai_summary": None})
for article in articles:
    try:
        # Step 2.1: Generate summary and title
        summary, title = generate_ai_summary(article['full_content'], article['title'])

        # Update MongoDB with summary and title
        collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"ai_summary": summary, "title": title}}
        )
        print(f"Summary and title generated and saved for article '{article['title']}'")

        # Step 2.2: Generate questions and image prompt after summary and title are updated
        question1, question2, image = generate_content(article['full_content'])

        # Prepare the data to update MongoDB with questions and image prompt
        update_data = {
            "question1": question1,
            "question2": question2,
            "image_prompt": image
        }

        # Update MongoDB with the questions and image prompt
        collection.update_one(
            {"_id": article["_id"]},
            {"$set": update_data}
        )
        print(f"Questions and image prompt generated and saved for article '{article['title']}'")

    except Exception as e:
        print(f"Failed to generate AI fields for article '{article['title']}': {e}")

print("AI generation and update completed for all articles.")



    