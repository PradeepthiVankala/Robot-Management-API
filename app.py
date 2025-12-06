from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)


robots_db = {}
logs_db = []


def generate_id():
    return str(uuid.uuid4())


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Robot Management API",
            "endpoints": {
                "POST /api/robots": "Register a new robot",
                "PUT /api/robots/<robot_id>/status": "Update robot status",
                "GET /api/robots": "Get all robots",
                "GET /api/robots/<robot_id>": "Get specific robot details",
                "POST /api/robots/<robot_id>/logs": "Create robot log",
                "GET /api/robots/<robot_id>/logs": "Get robot logs",
            },
        }
    ), 200


# API FOR ROBOT REGISTRATION
@app.route("/api/robots", methods=["POST"])
def register_robot():
    try:
        data = request.get_json()

        if not data or not all(key in data for key in ["name", "type"]):
            return jsonify({"error": "Missing required fields: name, type"}), 400

        robot_id = generate_id()
        robot = {
            "id": robot_id,
            "name": data["name"],
            "type": data["type"],
            "status": data.get("status", "idle"),
            "battery": 100,
            "location": data.get("location", "default"),
            "mode": "idle",
            "error_state": None,
            "created_at": datetime.now().isoformat(),
        }

        robots_db[robot_id] = robot

        # Log the registration
        log_entry = {
            "id": generate_id(),
            "robot_id": robot_id,
            "activity": "Robot registered",
            "timestamp": datetime.now().isoformat(),
            "details": f"Robot {data['name']} registered successfully",
        }
        logs_db.append(log_entry)

        return jsonify(
            {"message": "Robot registered successfully", "robot": robot}
        ), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API FOR UPDATING ROBOT STATUS
@app.route("/api/robots/<robot_id>/status", methods=["PUT"])
def update_robot_status(robot_id):
    try:
        if robot_id not in robots_db:
            return jsonify({"error": "Robot not found"}), 404

        data = request.get_json()
        robot = robots_db[robot_id]

        if "battery" in data:
            robot["battery"] = data["battery"]
        if "location" in data:
            robot["location"] = data["location"]
        if "mode" in data:
            robot["mode"] = data["mode"]
        if "error_state" in data:
            robot["error_state"] = data["error_state"]

        robot["updated_at"] = datetime.now().isoformat()

        log_entry = {
            "id": generate_id(),
            "robot_id": robot_id,
            "activity": "Status updated",
            "timestamp": datetime.now().isoformat(),
            "details": f"Battery: {robot['battery']}%, Location: {robot['location']}, Mode: {robot['mode']}",
        }
        logs_db.append(log_entry)

        return jsonify(
            {"message": "Robot status updated successfully", "robot": robot}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API FOR GETTING/RETRIEVING ROBOTS
@app.route("/api/robots", methods=["GET"])
def get_all_robots():
    try:
        return jsonify(
            {"count": len(robots_db), "robots": list(robots_db.values())}
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/robots/<robot_id>", methods=["GET"])
def get_robot_details(robot_id):
    try:
        if robot_id not in robots_db:
            return jsonify({"error": "Robot not found"}), 404

        return jsonify({"robot": robots_db[robot_id]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API FOR CREATING AND RETRIEVING ROBOT LOGS
@app.route("/api/robots/<robot_id>/logs", methods=["POST"])
def create_robot_log(robot_id):
    try:
        if robot_id not in robots_db:
            return jsonify({"error": "Robot not found"}), 404

        data = request.get_json()

        if not data or "activity" not in data:
            return jsonify({"error": "Missing required field: activity"}), 400

        log_entry = {
            "id": generate_id(),
            "robot_id": robot_id,
            "activity": data["activity"],
            "timestamp": datetime.now().isoformat(),
            "details": data.get("details", ""),
            "is_error": data.get("is_error", False),
        }

        logs_db.append(log_entry)

        return jsonify({"message": "Log created successfully", "log": log_entry}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/robots/<robot_id>/logs", methods=["GET"])
def get_robot_logs(robot_id):
    try:
        if robot_id not in robots_db:
            return jsonify({"error": "Robot not found"}), 404

        robot_logs = [log for log in logs_db if log["robot_id"] == robot_id]

        return jsonify({"count": len(robot_logs), "logs": robot_logs}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
