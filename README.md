# City Events Finder

INFO 520 group project (VCU) by Danielle and Arsema. Type a city and see one merged, de-duplicated list of upcoming events, sorted by date.

## APIs used

- **Ticketmaster Discovery API** (events) – largest coverage of concerts, sports and theater; free key with 5,000 calls/day; simple city search.
- **SeatGeek API** (events) – a second events feed with different listings, so we get broader results and real duplicates to test our de-dupe rule.
- **Open-Meteo** (weather enrichment) – free with no API key; adds a forecast for each event's date (e.g., "Saturday looks rainy").

## Duplicate rule

Ticketmaster and SeatGeek often list the same event with slightly different names. Two events count as the same if all three are true:

1. **Same day.** The time can differ; only the date has to match.
2. **Same main title words, in any order.** Before comparing, we remove text in parentheses ("The Notebook (Touring)" → "The Notebook"), anything after " - " ("King of Drag - The Royal Tour - Richmond" → "King of Drag"), opening acts after "w/" or "with" ("The Sword w/ Hippie Death Cult" → "The Sword"), and filler words like *the, live, tour, vs, at*.
3. **Same venue, or one venue name contains the other.** "The National" matches "The National - Richmond".

When we find a duplicate, we keep the copy with more information (exact time, link) and list both sources. Tested on real Richmond, VA results: the first version of the rule missed 10 duplicates; this version merged them (84 events → 74) with no wrong merges. The code is in `merge.py` and the tests are in `tests/test_merge.py`.

## Run locally

1. `python3 -m venv venv` then `source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and add your own keys (never commit `.env`)
4. `python app.py`, then open:
   - `http://localhost:8080/api/events?city=Richmond, VA` (merged events as JSON)
   - `http://localhost:8080/health` (returns `OK`)
5. Run the tests with `pytest`

## Deploy to Google Cloud

Coming in Phase 2. Region: us-east1.

## Teardown

Coming in Phase 4.