from flask import Blueprint, request, jsonify

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/api/v1/comments", methods=["POST"])
def create_comment():
    data = request.get_json(force=True) or {}
    body = data.get("body")

    if not isinstance(body, str):
        return jsonify({"error": "body must be a string"}), 400

    if len(body) > 500:
        return jsonify({"error": "body must be at most 500 characters"}), 400

    if body == "":
        return jsonify({"error": "body must not be empty"}), 400

    comment = save_comment(body)
    return jsonify(comment), 201


def save_comment(body):
    # persistence omitted for this mock
    return {"id": 1, "body": body}
