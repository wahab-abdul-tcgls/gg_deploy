import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch MongoDB key from environment variables
MONGODB_KEY = os.getenv("MONGODB_KEY")

# Check if MONGODB_KEY is set and not None
if MONGODB_KEY is None:
    raise ValueError("MONGODB_KEY environment variable is not set.")

# Encode the MongoDB password
password = quote_plus(MONGODB_KEY)

# Print the password if successful
print(f"Encoded MongoDB password: {password}")
