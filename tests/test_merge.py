import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from merge import merge

def test_merge_near_identical_titles():
    """Near-identical titles on the same date should merge into one event."""
    source1 = [{"title": "Richmond Tech Meetup", "start": "2026-11-15", "city": "Richmond", "state": "VA", "source": "Ticketmaster", "venue": "Convention Center"}]
    source2 = [{"title": "Richmond Tech Meetup!", "start": "2026-11-15", "city": "Richmond", "state": "VA", "source": "SeatGeek", "venue": "Convention Center"}]
    
    result = merge([source1, source2], {})
    
    assert len(result) == 1
    assert result[0]["title"] in ["Richmond Tech Meetup", "Richmond Tech Meetup!"]

def test_no_merge_different_dates():
    """Exact same titles on different dates should NOT merge."""
    source1 = [{"title": "Richmond Tech Meetup", "start": "2026-11-15", "city": "Richmond", "state": "VA", "source": "Ticketmaster", "venue": "Convention Center"}]
    source2 = [{"title": "Richmond Tech Meetup", "start": "2026-12-15", "city": "Richmond", "state": "VA", "source": "SeatGeek", "venue": "Convention Center"}]
    
    result = merge([source1, source2], {})
    
    assert len(result) == 2

def test_no_merge_completely_different_events():
    """Different events on the same date should NOT merge."""
    source1 = [{"title": "Richmond Tech Meetup", "start": "2026-11-15", "city": "Richmond", "state": "VA", "source": "Ticketmaster", "venue": "Convention Center"}]
    source2 = [{"title": "Downtown Farmers Market", "start": "2026-11-15", "city": "Richmond", "state": "VA", "source": "SeatGeek", "venue": "City Plaza"}]
    
    result = merge([source1, source2], {})
    
    assert len(result) == 2