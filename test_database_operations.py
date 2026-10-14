
import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

uri = os.getenv("MONGODB_URI")
database_name = os.getenv("MONGODB_DATABASE", "schoolms_db")

if not uri:
    raise ValueError("MONGODB_URI is missing from .env")

client = MongoClient(uri, serverSelectionTimeoutMS=15000)

try:
    client.admin.command("ping")
    db = client[database_name]
    collection = db["connection_tests"]

    test_record = {
        "test": "SchoolMS database read/write",
        "created_at": datetime.now(timezone.utc)
    }

    result = collection.insert_one(test_record)
    print("WRITE SUCCESS:", result.inserted_id)

    saved_record = collection.find_one({"_id": result.inserted_id})
    print("READ SUCCESS:", saved_record is not None)

    collection.delete_one({"_id": result.inserted_id})
    print("CLEANUP SUCCESS: Test record removed.")

except Exception as error:
    print("Database operation failed:", type(error).__name__, error)

finally:
    client.close()
