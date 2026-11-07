"""Ticketmaster Discovery API -> list of normalized events."""
import os

import requests

URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def get_events(city, state=None, timeout=5):
    params = {
        "apikey": os.environ["TICKETMASTER_KEY"],
        "city": city,
        "size": 50,
        "sort": "date,asc",
    }
    if state:
        params["stateCode"] = state

    resp = requests.get(URL, params=params, timeout=timeout)
    resp.raise_for_status()
    raw = resp.json().get("_embedded", {}).get("events", [])

    events = []
    for e in raw:
        dates = e.get("dates", {}).get("start", {})
        # dateTime is UTC; localDate + localTime is what the venue shows.
        start = dates.get("localDate")
        if not start:
            continue
        if dates.get("localTime"):
            start = f"{start}T{dates['localTime']}"

        venue = (e.get("_embedded", {}).get("venues") or [{}])[0]
        events.append({
            "title": e.get("name", ""),
            "start": start,
            "venue": venue.get("name", ""),
            "city": venue.get("city", {}).get("name", city),
            "url": e.get("url", ""),
            "source": "Ticketmaster",
        })
    return events
