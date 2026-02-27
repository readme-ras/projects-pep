# 🚀 RAG App (Flask + FAISS + Groq Llama 3)

A production-style Retrieval-Augmented Generation (RAG) application built with:

- 🔎 FAISS for vector search
- 🧠 SentenceTransformers for embeddings
- 🚀 Groq API (Llama 3 70B) for generation
- 🌐 Flask backend
- 📄 TXT document upload support

---

## 🧠 Architecture Overview

User Question
↓
Embedding (MiniLM)
↓
FAISS Similarity Search
↓
Top-K Relevant Chunks
↓
Groq Llama 3 (70B)
↓
Final Answer

---

## ⚙️ Tech Stack

- Python
- Flask
- FAISS (CPU)
- Sentence-Transformers
- Groq API (Llama 3.3 70B Versatile)
- NumPy

---
