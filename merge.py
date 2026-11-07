"""Merge events from all sources: dedupe, sort by date, attach weather.

Duplicate rule: two events are the same if, after cleaning,
  1. the titles match,
  2. they are on the same calendar day, and
  3. the venues match (or one venue name contains the other).
"""
import re

# Filler words that one source adds and the other doesn't.
FILLER = {"live", "tour", "touring", "tickets", "ticket", "the", "presents", "concert", "in", "at"}


def clean(text):
    text = (text or "").lower()
    text = re.sub(r"\(.*?\)", " ", text)  # drop "(Touring)", "(18+)" etc.
    text = re.sub(r"[^a-z0-9 ]", " ", text)  # drop punctuation
    words = [w for w in text.split() if w not in FILLER]
    return " ".join(words)


def day_of(start):
    return (start or "")[:10]  # "2026-11-14T19:30:00" -> "2026-11-14"


def same_event(a, b):
    if day_of(a["start"]) != day_of(b["start"]):
        return False
    if clean(a["title"]) != clean(b["title"]):
        return False
    va, vb = clean(a["venue"]), clean(b["venue"])
    return va == vb or (va and vb and (va in vb or vb in va))


def info_score(e):
    """How much useful info an event has, so we keep the better copy."""
    return sum(1 for k in ("title", "start", "venue", "url") if e.get(k)) + (1 if "T" in e.get("start", "") else 0)


def dedupe(events):
    kept = []
    for e in events:
        match = next((k for k in kept if same_event(k, e)), None)
        if match is None:
            kept.append({**e, "sources": [e["source"]]})
            continue
        sources = match["sources"] + [e["source"]]
        if info_score(e) > info_score(match):
            match.clear()
            match.update(e)
        match["sources"] = sources
    return kept


def merge(event_lists, forecast=None):
    forecast = forecast or {}
    all_events = [e for lst in event_lists for e in lst]
    merged = dedupe(all_events)
    merged.sort(key=lambda e: e["start"])
    for e in merged:
        e["weather"] = forecast.get(day_of(e["start"]))
    return merged
