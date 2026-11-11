"""Merge events from all sources: dedupe, sort by date, attach weather.

Duplicate rule: two events are the same if
  1. they are on the same calendar day,
  2. their main titles have the same words (any order), and
  3. their venues match (or one venue name contains the other).

"Main title" = the title with these removed, because the two sources word them differently:
  - anything in parentheses:        "The Notebook (Touring)"           -> "The Notebook"
  - anything after " - ":           "King of Drag - The Royal Tour"    -> "King of Drag"
  - opening acts after w/ or with:  "The Sword w/ Hippie Death Cult"   -> "The Sword"
  - filler words like the, live, tour, vs, at
Comparing words in any order matches sports listings such as
"Richmond Spiders Football vs. Lehigh" and "Lehigh at Richmond Spiders Football".
"""
import re

FILLER = {"live", "tour", "touring", "tickets", "ticket", "the", "presents",
          "concert", "in", "at", "vs", "v", "a", "an", "and", "of"}

SUPPORT_ACT = re.compile(r"\s+(?:w/|with|feat\.?|featuring|ft\.?)\s+.*$", re.IGNORECASE)


def main_part(text):
    text = (text or "").lower()
    text = re.sub(r"\(.*?\)", " ", text)  # drop "(Touring)", "(21 and Over)"
    text = text.split(" - ")[0]           # drop " - The Musical - Richmond"
    text = SUPPORT_ACT.sub("", text)      # drop " w/ Opening Act"
    return re.sub(r"[^a-z0-9 ]", " ", text)


def title_words(title):
    return frozenset(w for w in main_part(title).split() if w not in FILLER)


def venue_name(venue):
    return " ".join(w for w in main_part(venue).split() if w not in FILLER)


def day_of(start):
    return (start or "")[:10]  # "2026-11-14T19:30:00" -> "2026-11-14"


def same_event(a, b):
    if day_of(a["start"]) != day_of(b["start"]):
        return False
    ta, tb = title_words(a["title"]), title_words(b["title"])
    if not ta or ta != tb:
        return False
    va, vb = venue_name(a["venue"]), venue_name(b["venue"])
    return va == vb or bool(va and vb and (va in vb or vb in va))


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
        sources = match["sources"]
        if e["source"] not in sources:
            sources = sources + [e["source"]]
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
