

from flask import Blueprint, jsonify

from app.schemas.search import HealthResponseSchema, IndexResponseSchema
from app.services.search_service import search_service

system_bp = Blueprint("system", __name__)


@system_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    Returns server status and index statistics.

    Use this to verify the server is running and the index is loaded.
    """
    stats = search_service.get_stats()
    is_ready = search_service.is_ready()

    response = HealthResponseSchema.build(
        index_loaded=is_ready,
        stats=stats,
    )
    status_code = 200 if is_ready else 503
    return jsonify(response), status_code



@system_bp.route("/index", methods=["GET"])
def reindex():
    """
    Rebuild the TF-IDF index from the documents folder.

    Call this when:
    - New .txt files have been added to /documents
    - You want to refresh the index without restarting the server

    This is the BONUS endpoint from the task requirements.
    """
    try:
        stats = search_service.build_index()
        return jsonify(IndexResponseSchema.success(stats)), 200

    except FileNotFoundError as e:
        return jsonify(IndexResponseSchema.error(str(e))), 404

    except ValueError as e:
        return jsonify(IndexResponseSchema.error(str(e))), 422

    except Exception as e:
        return jsonify(
            IndexResponseSchema.error(f"Unexpected error: {str(e)}")
        ), 500
