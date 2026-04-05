

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentModel:
    """
    Represents a single document in the corpus.

    Fields:
        filename  : The .txt filename  e.g. "finance_ai.txt"
        raw_text  : Full content of the file
        tokens    : List of cleaned words after tokenization
        tfidf_vec : The TF-IDF vector { word: score }
    """
    filename: str
    raw_text: str
    tokens: list = field(default_factory=list)
    tfidf_vec: dict = field(default_factory=dict)

    def get_snippet(self, length: int = 200) -> str:
        """
        Returns the first `length` characters of the document
        as a clean single-line string (no extra spaces/newlines).
        """
        cleaned = " ".join(self.raw_text.split())
        return cleaned[:length]


@dataclass
class SearchResultModel:
    """
    Represents one result returned to the user.

    Fields:
        document : Filename of the matched document
        score    : Cosine similarity score (0.0 to 1.0)
        snippet  : Short preview of the document content
        rank     : Position in results (1 = best match)
    """
    document: str
    score: float
    snippet: str
    rank: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to a plain dictionary for JSON serialization."""
        return {
            "rank": self.rank,
            "document": self.document,
            "score": round(self.score, 6),
            "snippet": self.snippet,
        }


@dataclass
class IndexModel:
   
    doc_vectors: dict = field(default_factory=dict)
    idf: dict = field(default_factory=dict)
    raw_texts: dict = field(default_factory=dict)

    @property
    def total_docs(self) -> int:
        return len(self.doc_vectors)

    @property
    def unique_terms(self) -> int:
        return len(self.idf)

    def is_empty(self) -> bool:
        return self.total_docs == 0
