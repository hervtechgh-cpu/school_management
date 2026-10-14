
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env from the project directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "schoolms_db")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is missing from the .env file")

print("Connection string loaded:", MONGODB_URI.startswith("mongodb://"))
print("Database:", DATABASE_NAME)

client = None

try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=15000
    )

    client.admin.command("ping")
    print("SUCCESS: Connected to MongoDB Atlas!")

    db = client[DATABASE_NAME]
    print("Database selected:", db.name)

    print("MongoDB server version:", client.server_info()["version"])

except Exception as e:
    print("MongoDB connection failed:")
    print(type(e).__name__, e)

finally:
    if client is not None:
        client.close()
