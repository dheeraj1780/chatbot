# Project: Multi-Company FAQ Chatbot with SLM + RAG (Notebook Version)
# Step 2: Integrated with Ollama for SLM response generation

import os
import uuid
import shutil
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Document loading
import fitz  # PyMuPDF for PDFs

# Ollama client
import requests

# =============== CONFIG =================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "uploaded_docs"
VECTOR_DB_DIR = "vector_stores"
OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama server
OLLAMA_MODEL = "phi3:mini"  # Replace with your chosen SLM model name

# =============== MODELS =================
embedder = SentenceTransformer(EMBEDDING_MODEL)

# Dictionary to hold FAISS indexes per company
company_indexes = {}
company_docs = {}

# =============== HELPERS =================
def ensure_dirs():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)


def load_pdf_text(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping chunks for better retrieval.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


def get_or_create_index(company_id: str, dim: int):
    if company_id in company_indexes:
        return company_indexes[company_id]
    index = faiss.IndexFlatL2(dim)
    print(index)
    company_indexes[company_id] = index
    company_docs[company_id] = []
    return index


def query_ollama(model: str, prompt: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"[Error from Ollama: {response.status_code}]"
    except Exception as e:
        return f"[Ollama request failed: {e}]"


# =============== NOTEBOOK FUNCTIONS =================
def upload_docs(company_id: str, file_paths: List[str]):
    ensure_dirs()
    all_chunks = []

    for file_path in file_paths:
        file_ext = file_path.split(".")[-1].lower()
        file_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{company_id}_{file_id}_{os.path.basename(file_path)}")
        shutil.copy(file_path, save_path)

        if file_ext == "pdf":
            text = load_pdf_text(save_path)
        else:
            # Fallback: read raw text
            text = open(save_path, "r", encoding="utf-8", errors="ignore").read()

        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    # Embed & add to FAISS
    embeddings = embedder.encode(all_chunks)
    index = get_or_create_index(company_id, embeddings.shape[1])
    index.add(np.array(embeddings, dtype="float32"))
    company_docs[company_id].extend(all_chunks)

    return {"status": "success", "chunks_added": len(all_chunks)}


def chat(company_id: str, query: str, top_k: int = 3):
    if company_id not in company_indexes:
        return {"error": "No documents found for this company."}

    query_emb = embedder.encode([query])
    D, I = company_indexes[company_id].search(np.array(query_emb, dtype="float32"), top_k)

    retrieved_chunks = [company_docs[company_id][idx] for idx in I[0] if idx < len(company_docs[company_id])]

    context = "\n".join(retrieved_chunks)
    prompt = f"You are a company FAQ assistant. Answer based only on the context below.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"

    answer = query_ollama(OLLAMA_MODEL, prompt)

    return {"query": query, "answer": answer, "sources": retrieved_chunks}


# =============== DEMO CELLS =================
# Create fake docs for multiple companies
with open("TechCorp.txt", "w") as f:
    f.write("""
1. Employees at TechCorp get 20 days of paid leave per year.
2. Remote work is allowed up to 3 days a week.
3. TechCorp reimburses up to $500 per year for learning and development courses.
""")

with open("HealthPlus.txt", "w") as f:
    f.write("""
1. HealthPlus provides 15 days of paid sick leave annually.
2. Employees get free annual health checkups.
3. Health insurance covers dependents including spouse and children.
""")
    
with open("EduWorld.txt", "w") as f:
    f.write("""
1. EduWorld offers 25 days of vacation leave per year.
2. Tuition reimbursement is provided for relevant higher education programs.
3. Employees can access free online learning platforms like Coursera and Udemy.
""")

# Upload docs for both companies
print(upload_docs("TechCorp", ["TechCorp.txt"]))
print(upload_docs("HealthPlus", ["HealthPlus.txt"]))
print(upload_docs("EduWorld", ["EduWorld.txt"]))

# Query company A
print("\n--- Chat with TechCorp ---")
print(chat("TechCorp", "is it a good company to work for?"))

# Query company B
print("\n--- Chat with HealthPlus ---")
print(chat("HealthPlus", "do they offer health insurance for dependents?"))

# Query company C
print("\n--- Chat with EduWorld ---")
print(chat("EduWorld", "what learning benefits do employees have?"))