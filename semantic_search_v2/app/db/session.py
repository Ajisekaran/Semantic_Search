


class InMemoryDB:
    """
    Simulates a database session for our in-memory TF-IDF index.
    In production, replace this with a real SQLAlchemy session.
    """

    def __init__(self):
        self._store = {}

    def set(self, key: str, value):
        self._store[key] = value

    def get(self, key: str, default=None):
        return self._store.get(key, default)

    def delete(self, key: str):
        self._store.pop(key, None)

    def all_keys(self):
        return list(self._store.keys())



in_memory_db = InMemoryDB()
