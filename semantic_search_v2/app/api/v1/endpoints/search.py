

from flask import Blueprint, request, jsonify

from app.schemas.search import (
    SearchQuerySchema,
    SearchResponseSchema,
)
from app.services.search_service import search_service
from app.core.config import settings

search_bp = Blueprint("search", __name__)



@search_bp.route("/search", methods=["GET"])
def search_documents():
    """
    Search the document corpus.

    Query Parameters:
        q      (str, required) : The search query
        top_n  (int, optional) : Number of results (default 3, max 10)

    Returns:
        200 OK with results (even if 0 results — "no word found" message)
        400 Bad Request if query is empty or invalid
        503 Service Unavailable if index not loaded
    """
   
    if not search_service.is_ready():
        return jsonify(
            SearchResponseSchema.error(settings.MSG_INDEX_NOT_LOADED)
        ), 503

  
    query_schema = SearchQuerySchema(
        q=request.args.get("q", ""),
        top_n=request.args.get("top_n"),
    )

    if not query_schema.is_valid():
        return jsonify(query_schema.error_response()), 400

    
    results = search_service.search(
        query=query_schema.q,
        top_n=query_schema.top_n,
    )

    
    response = SearchResponseSchema.success(
        query=query_schema.q,
        results=results,
        total_docs=search_service.get_stats()["documents_indexed"],
    )

    return jsonify(response), 200
