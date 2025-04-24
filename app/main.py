from fastapi import FastAPI
from pymongo import MongoClient
import time
from pydantic import BaseModel
import numpy as np
import faiss
import json
import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)

try:
    from app.logger import log_query
except ModuleNotFoundError:
    from logger import log_query

app = FastAPI()

# Globals to be initialized on startup
model = None
index = None
faq_data = None
t5_tokenizer = None
t5_model = None


@app.on_event("startup")
async def load_resources():
    global model, index, faq_data, t5_tokenizer, t5_model

    await startup_db_client()

    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    INDEX_PATH = os.path.join(DATA_DIR, "faq_index.index")
    LOOKUP_PATH = os.path.join(DATA_DIR, "faq_lookup.json")

    # Load models from local cache
    model = SentenceTransformer("/app/cache/all-MiniLM-L6-v2")
    t5_tokenizer = T5Tokenizer.from_pretrained("/app/cache/t5-small")
    t5_model = T5ForConditionalGeneration.from_pretrained("/app/cache/t5-small")

    index = faiss.read_index(INDEX_PATH)
    with open(LOOKUP_PATH, "r", encoding="utf-8") as f:
        faq_data = json.load(f)


async def startup_db_client():
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            client.admin.command("ping")
            db = client[os.getenv("MONGO_DB")]
            collection = db[os.getenv("MONGO_COLLECTION")]
            return collection
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)


class Query(BaseModel):
    question: str
    top_k: int = 3


def enhance_answer_with_t5(answer: str) -> str:
    prompt = f"Improve this answer: {answer}"
    input_ids = t5_tokenizer.encode(
        prompt, return_tensors="pt", truncation=True, max_length=512
    )
    output_ids = t5_model.generate(
        input_ids, max_length=200, num_beams=4, early_stopping=True
    )
    enhanced_answer = t5_tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Log the output instead of printing
    logging.info("\n--- T5 Debug Output ---")
    logging.info(f"🔸 Original Answer: {answer}")
    logging.info(f"🔹 T5 Enhanced Answer: {enhanced_answer}")
    logging.info("------------------------\n")

    return enhanced_answer.replace("*", "★").replace("_", "␣")


@app.get("/")
def root():
    return {"status": "GitHub FAQ Chatbot API running"}


@app.post("/query")
def get_answer(query: Query, user_id: str = None):
    print(f"🔹 [DEBUG] Received user_id in /query: {user_id}")
    user_embedding = model.encode([query.question])
    D, I = index.search(np.array(user_embedding), query.top_k)

    results = []
    for idx_num, idx in enumerate(I[0]):
        item = faq_data[idx]
        answer = item["answer"]
        if idx_num == 0:
            answer = enhance_answer_with_t5(answer)
        results.append(
            {
                "question": item["question"],
                "answer": answer,
                "tags": item.get("tags", []),
                "related": item.get("related", []),
            }
        )

    print(f"🔹 [DEBUG] Calling log_query with user_id: {user_id}")
    log_query(query.question, results, user_id)
    return {"input": query.question, "results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
