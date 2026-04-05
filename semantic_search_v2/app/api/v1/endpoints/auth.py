

from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """
    Placeholder endpoint showing auth is not required for this API.
    In production, replace this with real JWT/OAuth2 logic.
    """
    return jsonify({
        "auth_required": False,
        "message": (
            "This API is publicly accessible. "
            "Authentication endpoints would live here in a "
            "protected production deployment."
        ),
    }), 200
