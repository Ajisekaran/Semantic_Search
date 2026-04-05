# Semantic Document Search Engine v2.0

A production-style semantic search engine built **from scratch** — no sklearn, no gensim, no HuggingFace. Custom TF-IDF vectorization and Cosine Similarity using only Python's built-in `math` and `re` modules.

---

## Project Structure

```
semantic_search/
│
├── app/                        ← Main application package
│   ├── main.py                 ← Flask app factory (create_app)
│   │
│   ├── core/                   ← Configuration & security
│   │   ├── config.py           ← All app settings in one place
│   │   └── security.py         ← CORS headers, security headers
│   │
│   ├── api/                    ← All route-related files
│   │   └── v1/                 ← Versioned API (v1)
│   │       └── endpoints/
│   │           ├── search.py   ← GET /api/v1/search
│   │           ├── system.py   ← GET /api/v1/health, /api/v1/index
│   │           └── auth.py     ← Auth placeholder
│   │
│   ├── models/                 ← Data models (shapes of data)
│   │   └── search.py           ← DocumentModel, SearchResultModel, IndexModel
│   │
│   ├── schemas/                ← Request/response validation
│   │   └── search.py           ← SearchQuerySchema, SearchResponseSchema
│   │
│   ├── services/               ← Business logic
│   │   └── search_service.py   ← build_index(), search() — the core logic
│   │
│   ├── db/                     ← Database layer
│   │   ├── session.py          ← In-memory DB (placeholder for SQLAlchemy)
│   │   └── base.py             ← Base model class placeholder
│   │
│   ├── utils/                  ← Utility functions
│   │   └── text_processor.py   ← tokenize, TF, IDF, TF-IDF, cosine_similarity
│   │
│   └── tests/                  ← Test suite
│       └── test_search.py      ← 40+ tests covering all components
│
├── documents/                  ← 55 sample .txt files (the corpus)
├── run.py                      ← Start the server: python run.py
└── requirements.txt            ← Only Flask needed
```

---

## Quick Start

### 1. Install the only dependency
```bash
pip install flask
```

### 2. Run the server
```bash
python run.py
```

### 3. Open your browser
```
http://127.0.0.1:5000
```

### 4. Run the tests
```bash
python app/tests/test_search.py
```

---

## API Reference

### `GET /api/v1/search`
Search documents using TF-IDF + Cosine Similarity.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `q` | string | ✅ Yes | — | Search query |
| `top_n` | int | No | 3 | Results to return (max 10) |

**Success response (results found):**
```json
{
  "success": true,
  "query": "artificial intelligence in finance",
  "results_found": 3,
  "total_documents_searched": 55,
  "results": [
    {
      "rank": 1,
      "document": "artificial_intelligence_overview.txt",
      "score": 0.150166,
      "snippet": "Artificial intelligence is one of the most transformative..."
    }
  ],
  "message": null
}
```

**No results found response:**
```json
{
  "success": true,
  "query": "xyzunknownword",
  "results_found": 0,
  "total_documents_searched": 55,
  "results": [],
  "message": "No matching documents found for your query. Try different or broader keywords."
}
```

**Error response (empty query):**
```json
{
  "success": false,
  "errors": ["Query parameter 'q' cannot be empty."],
  "data": null
}
```

---

### `GET /api/v1/index`
Rebuild the TF-IDF index (bonus endpoint).

```json
{
  "success": true,
  "message": "Index rebuilt successfully.",
  "stats": {
    "documents_indexed": 55,
    "unique_terms": 3369,
    "build_time_seconds": 0.018,
    "last_built": "2024-01-15 10:30:00"
  }
}
```

---

### `GET /api/v1/health`
Server health check.

```json
{
  "status": "healthy",
  "index_loaded": true,
  "stats": {
    "documents_indexed": 55,
    "unique_terms": 3369,
    "build_time_seconds": 0.018,
    "last_built": "2024-01-15 10:30:00"
  }
}
```

---

## Sample API Calls

```bash
# Basic search
curl "http://127.0.0.1:5000/api/v1/search?q=machine+learning"

# Search with custom result count
curl "http://127.0.0.1:5000/api/v1/search?q=deep+learning+neural+networks&top_n=5"

# Unknown word (returns no-results message)
curl "http://127.0.0.1:5000/api/v1/search?q=xyzunknownword"

# Empty query (returns 400 error)
curl "http://127.0.0.1:5000/api/v1/search?q="

# Rebuild index after adding new documents
curl "http://127.0.0.1:5000/api/v1/index"

# Health check
curl "http://127.0.0.1:5000/api/v1/health"
```

---

## How It Works

```
55 .txt documents
      │
      ▼  tokenize()      → clean words, remove stop words
      ▼  compute_tf()    → word frequency per document
      ▼  compute_idf()   → word rarity across corpus
      ▼  compute_tfidf() → TF × IDF = importance score
      │
      ├── doc1_vector: { "investment": 0.10, "risk": 0.08, ... }
      ├── doc2_vector: { "neural": 0.15, "learning": 0.12, ... }
      └── ... (55 vectors stored in memory)

User query: "machine learning"
      │
      ▼  Same tokenize + tfidf pipeline
      │
      query_vector: { "machine": 0.45, "learning": 0.38 }
      │
      ▼  cosine_similarity(query_vector, each doc_vector)
      │
      Scores → sorted → top 3 → JSON response ✅
```

---

## Constraints Compliance

| Requirement | Status |
|---|---|
| No sklearn / gensim / HuggingFace / Spacy | ✅ |
| TF-IDF manually implemented | ✅ `app/utils/text_processor.py` |
| Cosine Similarity manually implemented | ✅ `app/utils/text_processor.py` |
| `GET /search?q=` endpoint | ✅ `GET /api/v1/search?q=` |
| Returns top 3 docs + scores + snippets | ✅ |
| "No results found" message for unknown words | ✅ |
| Bonus: `/index` reindex endpoint | ✅ |
| Bonus: HTML Search UI | ✅ at `http://127.0.0.1:5000/` |
| Structured & modular code | ✅ FastAPI-style folder structure |
| Test suite | ✅ `python app/tests/test_search.py` |
