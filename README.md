# 🚀 LinkedIn + X Scraping RAG Multi-Turn Agent

An AI-powered full-stack application that scrapes LinkedIn and X (Twitter) profiles, processes the data, and enables intelligent multi-turn conversations using a Retrieval-Augmented Generation (RAG) pipeline.

---

## 🧠 What is this?

This project is a **Profile Intelligence Agent** that:

- Scrapes professional data from **LinkedIn**
- Optionally scrapes **X (Twitter)** profile + tweets
- Converts raw data into structured knowledge
- Uses **RAG (Retrieval-Augmented Generation)** to answer questions about a person
- Provides a **chat interface** to interact with that profile

Think of it like:
> ChatGPT, but trained on a specific person's digital footprint

---

## ⚙️ What does it do?

### 🔍 Data Extraction
- Extracts:
  - Profile info (name, bio, company, etc.)
  - Experience, education, projects
  - Posts & activity
  - Tweets (if X URL provided)

- Uses Bright Data APIs for scraping

---

### 🧠 RAG-Based Intelligence
- Converts profile data into documents
- Generates embeddings using:
  - sentence-transformers (multilingual-e5-large)
- Stores embeddings in:
  - ChromaDB (Vector Database)
- Retrieves relevant chunks for queries
- Uses:
  - Google Gemini (via LangChain) to generate answers

---

### 💬 Chat Interface
- Ask things like:
  - "What are their core skills?"
  - "Summarize their career"
  - "What projects have they worked on?"

- Supports **multi-turn conversations**

---

## 🏗️ Tech Stack

### Backend
- Flask
- LangChain
- Google Gemini API
- ChromaDB
- Sentence Transformers
- Bright Data APIs

### Frontend
- React (Vite)
- Modern chat UI

---

## 🧩 How it Works (Architecture)

User Input (LinkedIn URL)
        ↓
Scraper (LinkedIn + X)
        ↓
JSON Storage
        ↓
Document Processing
        ↓
Embeddings (Sentence Transformers)
        ↓
Vector DB (Chroma)
        ↓
Retriever + LLM (Gemini)
        ↓
Chat Response

---

## 📂 Project Structure

.
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   │   ├── linkedin_scrap.py
│   │   ├── x_scrap.py
│   │   ├── rag_service.py
│   ├── data/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js

---

## 🔑 Environment Variables

Create a `.env` file inside `backend/`:

GOOGLE_API_KEY=your_gemini_api_key  
BRIGHT_DATA_KEY=your_brightdata_api_key  
CUDA_VISIBLE_DEVICES=0   # optional (for GPU)

---

## 🖥️ How to Run Locally

### 1️⃣ Clone the repo
```sh
git clone https://github.com/your-username/your-repo-name.git  
cd your-repo-name  
```

### 2️⃣ Setup Backend
```sh
cd backend  
```
create virtual env
```sh
python -m venv venv
``` 

activate 
```sh
source venv/bin/activate   # Mac/Linux  
venv\Scripts\activate      # Windows
```

install dependencies  
```sh
pip install -r requirements.txt
```

---

### 3️⃣ Add Environment Variables

```sh
Create `.env` file:

GOOGLE_API_KEY=your_key  
BRIGHT_DATA_KEY=your_key  
```
---

### 4️⃣ Run Backend
```python
python app.py  
```
Backend runs at:  
http://localhost:5000  

---

### 5️⃣ Setup Frontend
```sh
cd ../frontend  
npm install  
```
---

### 6️⃣ Run Frontend
```sh
npm run dev  
```
Frontend runs at:  
http://localhost:5173  

---

## 🚀 How to Use

1. Open frontend  
2. Paste a LinkedIn profile URL  
3. (Optional) Add X profile  
4. Click "Analyze Profile"  
5. Start chatting  

---

## 🧠 Key Features

- Multi-source scraping (LinkedIn + X)
- RAG-based contextual Q&A
- Vector search with embeddings
- Multi-turn chat
- Clean UI
- Cache invalidation for fresh data

---

## ⚠️ Notes

- Bright Data API key is required
- LinkedIn scraping depends on API limits
- GPU is optional but improves speed

---

## 🔮 Future Improvements

- GitHub scraping integration  
- Resume upload support  
- Persistent memory  
- Docker deployment  
- Fine-tuned LLM  

---

## 🤝 Contributing

Fork it, improve it, send PRs.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Built with caffeine and questionable sleep cycles ☕
