import os
import threading
import requests

from flask import Flask, render_template, request, jsonify
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ================= CONFIG =================

UPLOAD_FOLDER = "uploads"
TOP_K = 3
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_TOKENS = 300

# 🔥 PUT YOUR GROQ KEY HERE (must start with gsk_)
GROQ_API_KEY = "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"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================= GLOBAL =================

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

chunks = []
index = None
lock = threading.Lock()


# ================= CHUNK TEXT =================

def chunk_text(text):
    parts = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for i in range(0, len(text), step):
        chunk = text[i:i + CHUNK_SIZE].strip()
        if len(chunk) > 80:
            parts.append(chunk)

    return parts


# ================= BUILD VECTOR DB =================

def rebuild_db():
    global chunks, index

    with lock:
        all_text = ""

        for file in os.listdir(UPLOAD_FOLDER):
            if file.endswith(".txt"):
                path = os.path.join(UPLOAD_FOLDER, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    all_text += f.read() + "\n"

        if not all_text.strip():
            chunks = []
            index = None
            return

        chunks = chunk_text(all_text)

        vectors = embedder.encode(chunks)
        vectors = np.array(vectors).astype("float32")

        faiss.normalize_L2(vectors)

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        print("Vector DB Ready ✅")


# ================= RETRIEVE =================

def retrieve(query):
    if index is None:
        return []

    q_vec = embedder.encode([query])
    q_vec = np.array(q_vec).astype("float32")

    faiss.normalize_L2(q_vec)

    _, ids = index.search(q_vec, TOP_K)

    return [chunks[i] for i in ids[0] if i < len(chunks)]


# ================= GENERATE ANSWER (GROQ) =================

def generate_answer(context, question):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Use ONLY the context below to answer the question.
If the answer is not present, say: Not found in document.

Context:
{context}

Question:
{question}
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a strict RAG assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": MAX_TOKENS
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("Groq ERROR STATUS:", response.status_code)
        print("Groq ERROR BODY:", response.text)
        return f"Groq API Error: {response.status_code}"

    result = response.json()

    return result["choices"][0]["message"]["content"].strip()


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")

    if not files:
        return jsonify({"status": "no_files"})

    for file in files:
        if file and file.filename.endswith(".txt"):
            name = file.filename.replace(" ", "_")
            path = os.path.join(UPLOAD_FOLDER, name)
            file.save(path)

    rebuild_db()

    return jsonify({"status": "success"})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json

    if not data or "question" not in data:
        return jsonify({"answer": "Invalid request."})

    question = data["question"].strip()

    if not question:
        return jsonify({"answer": "Type a question."})

    if index is None:
        return jsonify({"answer": "Upload TXT files first."})

    docs = retrieve(question)

    if not docs:
        return jsonify({"answer": "Not found in document."})

    context = "\n".join(docs)

    answer = generate_answer(context, question)

    return jsonify({"answer": answer})


@app.route("/status")
def status():
    return jsonify({
        "files": len(os.listdir(UPLOAD_FOLDER)),
        "chunks": len(chunks),
        "indexed": index is not None
    })


# ================= RUN =================

if __name__ == "__main__":
    print("Starting RAG App 🚀")
    rebuild_db()
    app.run(port=8000, debug=True)