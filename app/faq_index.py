import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
FAQ_JSON = os.path.join(DATA_PATH, "Full_dataset.json")
LOOKUP_PATH = os.path.join(DATA_PATH, "faq_lookup.json")
INDEX_PATH = os.path.join(DATA_PATH, "faq_index.index")

# Load dataset
with open(FAQ_JSON, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

questions = [item["question"] for item in faq_data]

# Load Sentence-BERT model
print("Loading Sentence-BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
print("Encoding questions...")
embeddings = model.encode(questions, show_progress_bar=True)

# Build FAISS index
dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save index
faiss.write_index(index, INDEX_PATH)
print(f"FAISS index saved to {INDEX_PATH}")

# Save lookup data (FAQ items)
with open(LOOKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(faq_data, f, indent=2)
print(f"Lookup data saved to {LOOKUP_PATH}")
