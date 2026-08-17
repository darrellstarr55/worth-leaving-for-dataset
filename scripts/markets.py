"""One primary market for every U.S. state plus D.C. and Puerto Rico."""

MARKETS = (
    ("Birmingham", "AL", 33.5186, -86.8104),
    ("Anchorage", "AK", 61.2181, -149.9003),
    ("Phoenix", "AZ", 33.4484, -112.0740),
    ("Little Rock", "AR", 34.7465, -92.2896),
    ("Los Angeles", "CA", 34.0522, -118.2437),
    ("Denver", "CO", 39.7392, -104.9903),
    ("Hartford", "CT", 41.7658, -72.6734),
    ("Wilmington", "DE", 39.7391, -75.5398),
    ("Washington", "DC", 38.9072, -77.0369),
    ("Miami", "FL", 25.7617, -80.1918),
    ("Atlanta", "GA", 33.7490, -84.3880),
    ("Honolulu", "HI", 21.3069, -157.8583),
    ("Boise", "ID", 43.6150, -116.2023),
    ("Chicago", "IL", 41.8781, -87.6298),
    ("Indianapolis", "IN", 39.7684, -86.1581),
    ("Des Moines", "IA", 41.5868, -93.6250),
    ("Wichita", "KS", 37.6872, -97.3301),
    ("Louisville", "KY", 38.2527, -85.7585),
    ("New Orleans", "LA", 29.9511, -90.0715),
    ("Portland", "ME", 43.6591, -70.2568),
    ("Baltimore", "MD", 39.2904, -76.6122),
    ("Boston", "MA", 42.3601, -71.0589),
    ("Detroit", "MI", 42.3314, -83.0458),
    ("Minneapolis", "MN", 44.9778, -93.2650),
    ("Jackson", "MS", 32.2988, -90.1848),
    ("St. Louis", "MO", 38.6270, -90.1994),
    ("Billings", "MT", 45.7833, -108.5007),
    ("Omaha", "NE", 41.2565, -95.9345),
    ("Las Vegas", "NV", 36.1699, -115.1398),
    ("Manchester", "NH", 42.9956, -71.4548),
    ("Newark", "NJ", 40.7357, -74.1724),
    ("Albuquerque", "NM", 35.0844, -106.6504),
    ("New York", "NY", 40.7128, -74.0060),
    ("Charlotte", "NC", 35.2271, -80.8431),
    ("Fargo", "ND", 46.8772, -96.7898),
    ("Columbus", "OH", 39.9612, -82.9988),
    ("Oklahoma City", "OK", 35.4676, -97.5164),
    ("Portland", "OR", 45.5152, -122.6784),
    ("Philadelphia", "PA", 39.9526, -75.1652),
    ("San Juan", "PR", 18.4655, -66.1057),
    ("Providence", "RI", 41.8240, -71.4128),
    ("Charleston", "SC", 32.7765, -79.9311),
    ("Sioux Falls", "SD", 43.5446, -96.7311),
    ("Nashville", "TN", 36.1627, -86.7816),
    ("Austin", "TX", 30.2672, -97.7431),
    ("Salt Lake City", "UT", 40.7608, -111.8910),
    ("Burlington", "VT", 44.4759, -73.2121),
    ("Richmond", "VA", 37.5407, -77.4360),
    ("Seattle", "WA", 47.6062, -122.3321),
    ("Charleston", "WV", 38.3498, -81.6326),
    ("Milwaukee", "WI", 43.0389, -87.9065),
    ("Cheyenne", "WY", 41.1400, -104.8202),
)


def market(city: str, state_code: str, latitude: float, longitude: float) -> dict:
    return {
        "city": city,
        "stateCode": state_code,
        "latitude": latitude,
        "longitude": longitude,
        "radiusMiles": 12 if state_code == "MI" else 10,
    }


def daily_markets(day_ordinal: int) -> list[dict]:
    detroit = next(item for item in MARKETS if item[1] == "MI")
    rotation = tuple(item for item in MARKETS if item[1] != "MI")
    start = (day_ordinal * 3) % len(rotation)
    selected = [rotation[(start + offset) % len(rotation)] for offset in range(3)]
    return [market(*detroit), *(market(*item) for item in selected)]
