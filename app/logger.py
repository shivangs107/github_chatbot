import os
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env vars
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]

# Initialize all collections
logs_collection = db["logs"]
conversations_collection = db["conversations"]
users_collection = db["users"]
analytics_collection = db["analytics"]


def log_query(user_input, results, user_id=None):
    print(f"🔹 [DEBUG] Logger received user_id: {user_id}")
    print(f"DEBUG - Results structure: {results}")  # Verify results structure
    top_result = results[0] if results else {}

    # 1. Log basic query info
    logs_collection.insert_one(
        {
            "timestamp": datetime.datetime.utcnow(),
            "user_question": user_input,
            "matched_question": top_result.get("question"),
            "tags": top_result.get("tags", []),
            "related": top_result.get("related", []),
        }
    )

    # 2. Store full conversation
    if user_id and str(user_id).strip():
        conversations_collection.insert_one(
            {
                "user_id": user_id,
                "question": user_input,
                "answer": top_result.get("answer", ""),
                "timestamp": datetime.datetime.utcnow(),
            }
        )

    # 3. Update user analytics
    if user_id and str(user_id).strip():
        users_collection.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"query_count": 1},
                "$set": {"last_active": datetime.datetime.utcnow()},
            },
            upsert=True,
        )

    # 4. General analytics
    analytics_collection.update_one(
        {"date": datetime.datetime.utcnow().strftime("%Y-%m-%d")},
        {"$inc": {"daily_queries": 1}},
        upsert=True,
    )
