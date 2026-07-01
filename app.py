from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from detector import analyze_with_groq
from stylometric import analyze_stylometry
from confidence import calculate_confidence
from audit_log import write_audit_log, get_log, update_status
import uuid
from datetime import datetime, timezone



app = Flask(__name__)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[]
)

@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text or not creator_id:
        return jsonify({
            "error": "Both 'text' and 'creator_id' are required."
        }), 400


    # Generate unique submission ID
    content_id = str(uuid.uuid4())


    try:
        # -------------------------
        # Signal 1: Groq LLM
        # -------------------------
        groq_result = analyze_with_groq(text)

        llm_score = groq_result["confidence"]


        # -------------------------
        # Signal 2: Stylometric
        # -------------------------
        stylometric_result = analyze_stylometry(text)

        stylometric_score = stylometric_result["stylometric_score"]


        # -------------------------
        # Combine signals
        # -------------------------
        final_result = calculate_confidence(
            llm_score,
            stylometric_score
        )


        # -------------------------
        # Audit log entry
        # -------------------------
        audit_entry = {
            "content_id": content_id,
            "creator_id": creator_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attribution": final_result["attribution"],
            "confidence": final_result["confidence"],
            "llm_score": llm_score,
            "stylometric_score": stylometric_score,
            "status": "classified"
        }

        write_audit_log(audit_entry)


        # -------------------------
        # API response
        # -------------------------
        return jsonify({
            "content_id": content_id,
            "creator_id": creator_id,

            "signal_1_llm": groq_result,

            "signal_2_stylometric": stylometric_result,

            "confidence_score": final_result["confidence"],

            "attribution": final_result["attribution"],

            "transparency_label": final_result["label"]

        }), 200


    except Exception as e:
        return jsonify({
            "error": "Detection failed.",
            "details": str(e)
        }), 500



@app.route("/log", methods=["GET"])
def log():
    return jsonify({
        "entries": get_log()
    }), 200

@app.route("/appeal", methods=["POST"])
def appeal():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400


    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")


    if not content_id or not creator_reasoning:

        return jsonify({
            "error": "content_id and creator_reasoning are required."
        }), 400



    updated = update_status(
        content_id,
        "under_review",
        creator_reasoning
    )


    if not updated:

        return jsonify({
            "error": "Content ID not found."
        }), 404



    return jsonify({

        "message": "Appeal submitted successfully.",

        "content_id": content_id,

        "status": "under_review"

    }), 200


if __name__ == "__main__":
    app.run(debug=True)