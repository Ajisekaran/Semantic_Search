

from app.main import create_app, init_index
from app.core.config import settings


if __name__ == "__main__":

    print("=" * 60)
    print("  SEMANTIC DOCUMENT SEARCH ENGINE  v2.0")
    print("  FastAPI-style structure | Flask backend")
    print("  Custom TF-IDF + Cosine Similarity")
    print("=" * 60)


    init_index()


    app = create_app()

    print()
    print(f"  UI:      http://127.0.0.1:{settings.PORT}/")
    print(f"  Search:  http://127.0.0.1:{settings.PORT}/api/v1/search?q=machine+learning")
    print(f"  Health:  http://127.0.0.1:{settings.PORT}/api/v1/health")
    print(f"  Reindex: http://127.0.0.1:{settings.PORT}/api/v1/index")
    print()
    print("  Press CTRL+C to stop.")
    print("=" * 60)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
    )
