

import os
import time

from app.core.config import settings
from app.models.search import IndexModel, SearchResultModel
from app.utils.text_processor import (
    tokenize,
    compute_tf,
    compute_idf,
    compute_tfidf,
    cosine_similarity,
)


class SearchService:
    """
    Manages the TF-IDF index and handles all search operations.

    This is a class (not just functions) because:
    - It holds state: the index (self._index)
    - We want one shared instance across the whole app
    - Easy to call methods on it: search_service.search(query)
    """

    def __init__(self):
     
        self._index: IndexModel = IndexModel()
        self._build_time: float = 0.0
        self._last_built: str = "Never"

   
    def build_index(self, documents_dir: str = None) -> dict:
        """
        Read all .txt files → tokenize → compute TF-IDF → store in memory.

        This is called ONCE at startup (and again if /index is hit).
        After this, search() is fast because we never read files again.

        Returns:
            dict with stats about the index build
        Raises:
            FileNotFoundError if documents_dir doesn't exist
            ValueError if no .txt files are found
        """
        docs_dir = documents_dir or settings.DOCUMENTS_DIR

    
        if not os.path.isdir(docs_dir):
            raise FileNotFoundError(
                f"Documents directory not found: {docs_dir}\n"
                f"Make sure a 'documents/' folder exists in your project root."
            )

        filenames = sorted([
            f for f in os.listdir(docs_dir)
            if f.endswith(".txt")
        ])

        if not filenames:
            raise ValueError(
                f"No .txt files found in: {docs_dir}\n"
                f"Add some text documents to the documents/ folder."
            )

        start_time = time.time()

        
        raw_texts = {}
        all_token_lists = []

        for fname in filenames:
            path = os.path.join(docs_dir, fname)
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
            raw_texts[fname] = text
            all_token_lists.append(tokenize(text))

      
        idf = compute_idf(all_token_lists)

        
        doc_vectors = {}
        for fname, tokens in zip(filenames, all_token_lists):
            tf = compute_tf(tokens)
            tfidf_vec = compute_tfidf(tf, idf)
            doc_vectors[fname] = tfidf_vec

       
        self._index = IndexModel(
            doc_vectors=doc_vectors,
            idf=idf,
            raw_texts=raw_texts,
        )

        self._build_time = round(time.time() - start_time, 4)
        self._last_built = time.strftime("%Y-%m-%d %H:%M:%S")

        stats = self.get_stats()
        print(
            f"[SearchService] Index built: "
            f"{stats['documents_indexed']} docs | "
            f"{stats['unique_terms']} terms | "
            f"{stats['build_time_seconds']}s"
        )
        return stats

    def search(self, query: str, top_n: int = 3) -> list:
        """
        Search the corpus for documents most relevant to `query`.

        Steps:
          1. Tokenize the query (same pipeline as documents)
          2. Build query TF-IDF vector (using corpus IDF)
          3. Compute cosine similarity with every document
          4. Sort by score descending
          5. Return top_n results as SearchResultModel objects

        Args:
            query: The user's search string
            top_n: How many results to return (default 3)
        Returns:
            List of SearchResultModel — empty list if no matches or
            if all similarity scores are 0 (no word found)
        """
       
        query_tokens = tokenize(query)

    
        if not query_tokens:
            return []

        
        query_tf = compute_tf(query_tokens)
      
        query_vector = compute_tfidf(query_tf, self._index.idf)

      
        if not query_vector:
            return []

     
        scored = []
        for fname, doc_vector in self._index.doc_vectors.items():
            score = cosine_similarity(query_vector, doc_vector)
           
            if score > 0:
                scored.append((fname, score))

       
        if not scored:
            return []

     
        scored.sort(key=lambda x: x[1], reverse=True)
        top_results = scored[:top_n]


        results = []
        for rank, (fname, score) in enumerate(top_results, start=1):
            raw_text = self._index.raw_texts[fname]
            snippet = " ".join(raw_text.split())[:settings.SNIPPET_LENGTH]
            results.append(SearchResultModel(
                document=fname,
                score=score,
                snippet=snippet,
                rank=rank,
            ))

        return results

  
    def is_ready(self) -> bool:
        """Returns True if the index has been built and has documents."""
        return not self._index.is_empty()

    def get_stats(self) -> dict:
        """Returns a summary of the current index state."""
        return {
            "documents_indexed": self._index.total_docs,
            "unique_terms": self._index.unique_terms,
            "build_time_seconds": self._build_time,
            "last_built": self._last_built,
        }


search_service = SearchService()
