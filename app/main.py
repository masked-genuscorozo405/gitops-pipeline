"""
GitOps Pipeline - Flask API
Endpoints: health, version, metrics, readiness
"""

import os
import time
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
START_TIME = time.time()

request_count = 0


@app.before_request
def count_requests():
    global request_count
    request_count += 1


@app.route("/")
def root():
    return jsonify(
        {
            "app": "gitops-pipeline",
            "version": APP_VERSION,
            "docs": "/health, /version, /metrics, /ready",
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.route("/ready")
def readiness():
    return jsonify({"ready": True, "uptime_seconds": round(time.time() - START_TIME, 2)})


@app.route("/version")
def version():
    return jsonify(
        {
            "version": APP_VERSION,
            "commit": os.getenv("GIT_COMMIT", "unknown"),
            "build_date": os.getenv("BUILD_DATE", "unknown"),
        }
    )


@app.route("/metrics")
def metrics():
    uptime = time.time() - START_TIME
    return jsonify(
        {
            "uptime_seconds": round(uptime, 2),
            "request_count": request_count,
            "version": APP_VERSION,
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
