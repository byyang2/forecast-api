"""forecast-api: synthetic point-forecast service for the GSL deployment POC (no real data)."""
import datetime
import hashlib
import os

from flask import Flask, jsonify, request

app = Flask(__name__)
RELEASE = os.environ.get("RELEASE", "v1")


def _synthetic(station: str, hour: int) -> dict:
    seed = int(hashlib.sha256(f"{station}:{hour}".encode()).hexdigest(), 16)
    return {
        "hour": hour,
        "temp_c": round(5 + (seed % 2500) / 100, 1),
        "wind_kt": seed % 35,
        "precip_pct": seed % 101,
    }


@app.get("/")
def index():
    return jsonify(service="forecast-api", release=RELEASE,
                   endpoints=["/forecast?station=KBOU&hours=6", "/healthz"])


@app.get("/forecast")
def forecast():
    station = request.args.get("station", "KBOU").upper()[:8]
    hours = max(1, min(int(request.args.get("hours", 6)), 48))
    issued = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    return jsonify(station=station, issued=issued.isoformat(), synthetic=True,
                   periods=[_synthetic(station, h) for h in range(hours)])


@app.get("/healthz")
def healthz():
    return "ok", 200
