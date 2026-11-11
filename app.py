"""City Events Finder: Flask app.

Routes:
  /                       the search page (templates/index.html)
  /api/events?city=...    merged, de-duplicated, date-sorted events as JSON
  /health                 returns OK
"""
import logging
import os

from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, render_template, request

load_dotenv()  # reads .env locally; on Cloud Run the keys come from Secret Manager

from merge import merge  # noqa: E402
from sources import seatgeek, ticketmaster, weather  # noqa: E402

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

EVENT_SOURCES = {
    "Ticketmaster": ticketmaster.get_events,
    "SeatGeek": seatgeek.get_events,
}


def safe_error(exc):
    """Describe an error without the request URL, which contains the API key."""
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return f"HTTP {exc.response.status_code} {exc.response.reason}"
    if isinstance(exc, KeyError):
        return f"missing setting {exc} in .env"
    return type(exc).__name__


def parse_city(text):
    """'Richmond, VA' -> ('Richmond', 'VA'); 'Richmond' -> ('Richmond', None)."""
    parts = [p.strip() for p in text.split(",")]
    city = parts[0]
    state = parts[1].upper() if len(parts) > 1 and parts[1] else None
    return city, state


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return "OK", 200


@app.route("/api/events")
def events():
    text = request.args.get("city") or os.environ.get("DEFAULT_CITY", "Richmond")
    city, state = parse_city(text)

    results, errors = [], []
    for name, fetch in EVENT_SOURCES.items():
        try:
            results.append(fetch(city, state))
        except Exception as exc:  # one source failing shouldn't break the page
            logging.error("%s failed: %s", name, safe_error(exc))
            errors.append(name)

    try:
        forecast = weather.get_forecast(city, state)
    except Exception as exc:
        logging.error("Open-Meteo failed: %s", safe_error(exc))
        forecast = {}
        errors.append("Open-Meteo")

    merged = merge(results, forecast)
    return jsonify({
        "city": city,
        "state": state,
        "count": len(merged),
        "failed_sources": errors,
        "events": merged,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
