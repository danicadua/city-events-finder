"""SeatGeek API -> list of normalized events."""
import os

import requests

URL = "https://api.seatgeek.com/2/events"


def get_events(city, state=None, timeout=5):
    params = {
        "client_id": os.environ["SEATGEEK_CLIENT_ID"],
        "venue.city": city,
        "per_page": 50,
        "sort": "datetime_local.asc",
    }
    if state:
        params["venue.state"] = state

    resp = requests.get(URL, params=params, timeout=timeout)
    resp.raise_for_status()
    raw = resp.json().get("events", [])

    events = []
    for e in raw:
        venue = e.get("venue") or {}
        events.append({
            "title": e.get("title", ""),
            "start": e.get("datetime_local", ""),  # e.g. 2026-11-14T19:30:00
            "venue": venue.get("name", ""),
            "city": venue.get("city", city),
            "url": e.get("url", ""),
            "source": "SeatGeek",
        })
    return [ev for ev in events if ev["start"]]
