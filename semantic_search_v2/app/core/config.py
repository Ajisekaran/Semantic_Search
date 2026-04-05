"""
app/core/config.py
------------------
Central configuration for the entire application.
All settings live here — change one place, affects everything.

Think of this like the "settings panel" of your app.
"""

import os

class Settings:
    """
    All app-wide settings in one place.
    If you want to change the port, documents folder,
    or app name — you only touch THIS file.
    """

    # ── App Info ──────────────────────────────────────────
    APP_NAME: str = "Semantic Document Search Engine"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = (
        "Custom TF-IDF search engine built from scratch. "
        "No sklearn, gensim, or external NLP libraries used."
    )

    # ── Server ────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = False

    # ── Documents ─────────────────────────────────────────
    # Build the path relative to the project root
    BASE_DIR: str = os.path.dirname(                  # /app/core → /app
                        os.path.dirname(              # /app
                            os.path.dirname(          # project root
                                os.path.abspath(__file__)
                            )
                        )
                    )

    DOCUMENTS_DIR: str = os.path.join(BASE_DIR, "documents")

    # ── Search ────────────────────────────────────────────
    DEFAULT_TOP_N: int = 3          # Return top 3 results by default
    MAX_TOP_N: int = 10             # Never return more than 10
    MIN_QUERY_LENGTH: int = 1       # Query must be at least 1 character
    SNIPPET_LENGTH: int = 200       # Characters to show in snippet

    # ── Messages ──────────────────────────────────────────
    # Centralised messages — no hardcoded strings in other files
    MSG_NO_RESULTS = (
        "No matching documents found for your query. "
        "Try different or broader keywords."
    )
    MSG_INDEX_NOT_LOADED = "Search index is not loaded yet. Please try again shortly."
    MSG_EMPTY_QUERY     = "Query parameter 'q' cannot be empty."
    MSG_INDEX_SUCCESS   = "Index rebuilt successfully."


# Create a single instance — import this everywhere
settings = Settings()
