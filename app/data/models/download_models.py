from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os

# Define paths
MODEL_DIR = "app/data/models"
os.makedirs(MODEL_DIR, exist_ok=True)

# 1. Download SentenceTransformer model
print("Downloading SentenceTransformer model...")
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
sbert_model.save(os.path.join(MODEL_DIR, "all-MiniLM-L6-v2"))

# 2. Download T5 model
print("Downloading T5 model...")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")

t5_tokenizer.save_pretrained(os.path.join(MODEL_DIR, "t5-small"))
t5_model.save_pretrained(os.path.join(MODEL_DIR, "t5-small"))

print("Models downloaded successfully!")