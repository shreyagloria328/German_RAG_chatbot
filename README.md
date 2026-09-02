# German Study Assistant — RAG Chatbot

An AI-powered German language study chatbot built 
using Retrieval Augmented Generation (RAG).

## What it does
Ask questions about German grammar and vocabulary 
in English or German — the chatbot answers using 
your own A1/A2/B1 study materials.

## Tech stack
- PDF extraction — pdfplumber
- Vector embeddings — sentence-transformers
- Vector database — ChromaDB
- LLM — Groq (Llama)
- Web interface — Streamlit
- Containerised — Docker

## Project structure

├── pdf_extractor.py  — extracts text from PDFs
├── embeddings.py     — creates and stores vectors
├── retriever.py      — searches ChromaDB
├── generator.py      — generates answers via Groq
├── app.py            — Streamlit web interface
└── Dockerfile        — container configuration
