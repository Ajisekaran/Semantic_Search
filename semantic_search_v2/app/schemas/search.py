

from app.core.config import settings


class SearchQuerySchema:
    """
    Schema for validating an incoming search request.

    In FastAPI this would be:
        class SearchQuery(BaseModel):
            q: str
            top_n: int = 3

    We simulate the same validation manually.
    """

    def __init__(self, q: str, top_n: str = None):
        self.errors = []

       
        if not q or not q.strip():
            self.errors.append(settings.MSG_EMPTY_QUERY)
            self.q = ""
        else:
            self.q = q.strip()

       
        if top_n is None:
            self.top_n = settings.DEFAULT_TOP_N
        else:
            try:
                self.top_n = int(top_n)
                if self.top_n < 1:
                    self.top_n = 1
                if self.top_n > settings.MAX_TOP_N:
                    self.top_n = settings.MAX_TOP_N
            except ValueError:
                self.errors.append(f"'top_n' must be a number. Got: '{top_n}'")
                self.top_n = settings.DEFAULT_TOP_N

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def error_response(self) -> dict:
        """Returns a structured error dict when validation fails."""
        return {
            "success": False,
            "errors": self.errors,
            "data": None,
        }


class SearchResponseSchema:
    """
    Schema for structuring the search response.

    Ensures every response from /search has the SAME structure,
    whether results are found or not.
    """

    @staticmethod
    def success(query: str, results: list, total_docs: int) -> dict:
        """Response when search succeeds (even if 0 results)."""
        found = len(results) > 0
        return {
            "success": True,
            "query": query,
            "results_found": len(results),
            "total_documents_searched": total_docs,
        
            "results": [r.to_dict() for r in results] if results else [],
            "message": (
                None if found
                else settings.MSG_NO_RESULTS  
            ),
        }

    @staticmethod
    def error(message: str) -> dict:
        """Response when something goes wrong (index not loaded, etc.)."""
        return {
            "success": False,
            "query": None,
            "results_found": 0,
            "total_documents_searched": 0,
            "results": [],
            "message": message,
        }


class IndexResponseSchema:
    """Schema for the /index endpoint response."""

    @staticmethod
    def success(stats: dict) -> dict:
        return {
            "success": True,
            "message": settings.MSG_INDEX_SUCCESS,
            "stats": stats,
        }

    @staticmethod
    def error(message: str) -> dict:
        return {
            "success": False,
            "message": message,
            "stats": None,
        }


class HealthResponseSchema:
    """Schema for the /health endpoint response."""

    @staticmethod
    def build(index_loaded: bool, stats: dict) -> dict:
        return {
            "status": "healthy" if index_loaded else "degraded",
            "index_loaded": index_loaded,
            "stats": stats,
        }
