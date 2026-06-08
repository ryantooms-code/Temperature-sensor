"""
flask_app.py - Flask REST API
Exposes endpoints to query stored sensor readings from SQLite.
"""

from flask import Flask, jsonify
from database import get_latest_reading, get_all_readings


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return jsonify({
            "service": "SenseHat Monitor API",
            "endpoints": {
                "/api/latest": "Most recent sensor reading",
                "/api/readings": "All stored sensor readings",
                "/health": "Health check"
            }
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/latest")
    def latest():
        row = get_latest_reading()
        if row:
            return jsonify({
                "timestamp":    row["timestamp"],
                "temperature":  row["temperature"],
                "humidity":     row["humidity"],
                "pressure":     row["pressure"],
                "status":       row["status"]
            })
        return jsonify({"error": "No data available"}), 404

    @app.route("/api/readings")
    def readings():
        rows = get_all_readings()
        data = [
            {
                "id":          r["id"],
                "timestamp":   r["timestamp"],
                "temperature": r["temperature"],
                "humidity":    r["humidity"],
                "pressure":    r["pressure"],
                "status":      r["status"]
            }
            for r in rows
        ]
        return jsonify(data)

    return app