from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB connection parameters
MONGODB_USERNAME = "appadmin"         # Replace with your MongoDB username
MONGODB_PASSWORD = "gIstdEvtcgeNie2024" # Replace with your MongoDB password
MONGODB_CLUSTER = "gistgenie.afh0z.mongodb.net"  # Replace with your cluster address

# Construct the connection URI
uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority"

try:
    # Create a MongoDB client
    client = MongoClient(uri)

    # Attempt to connect and ping the server
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")

except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
