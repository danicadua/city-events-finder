"""Open-Meteo (no key) -> {"YYYY-MM-DD": "High 61°F, low 44°F, 20% rain"}.

Open-Meteo needs coordinates, so we geocode the city name first.
The forecast only covers the next 16 days; later events get no weather.
"""
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Two-letter state code -> the name Open-Meteo uses in "admin1".
STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def _find_city(city, state, timeout):
    params = {"name": city, "count": 10, "countryCode": "US"}
    resp = requests.get(GEOCODE_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    if state:
        wanted = STATES.get(state.upper(), state)
        for r in results:
            if r.get("admin1", "").lower() == wanted.lower():
                return r
    return results[0]  # biggest match first, e.g. Richmond, Virginia


def get_forecast(city, state=None, timeout=5):
    place = _find_city(city, state, timeout)
    if not place:
        return {}

    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "temperature_unit": "fahrenheit",
        "timezone": place.get("timezone", "auto"),
        "forecast_days": 16,
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})

    forecast = {}
    for day, hi, lo, rain in zip(
        daily.get("time", []),
        daily.get("temperature_2m_max", []),
        daily.get("temperature_2m_min", []),
        daily.get("precipitation_probability_max", []),
    ):
        text = f"High {round(hi)}°F, low {round(lo)}°F"
        if rain is not None:
            text += f", {rain}% rain"
        forecast[day] = text
    return forecast
