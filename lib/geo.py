from geopy.geocoders import Nominatim
from geopy.distance import distance as get_distance
from geopy.extra.rate_limiter import RateLimiter
from geopy.point import Point

from lib.db import GeocodeResult

geolocator = Nominatim(user_agent="people-matcher-demo")
rate_limited_geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)


class Location(object):
    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return dict(
            address=self.address, latitude=self.latitude, longitude=self.longitude
        )

    def __eq__(self, other):
        return (
            self.address == other.address
            and self.latitude == other.latitude
            and self.longitude == other.longitude
        )

    @property
    def point(self):
        return Point(self.latitude, self.longitude)


def geocode(address):
    cache = GeocodeResult()
    output_dict = cache.get(address)
    if output_dict is None:
        loc = rate_limited_geocode(address)
        output = Location(
            address=loc.address, latitude=loc.latitude, longitude=loc.longitude
        )
        cache.set(address, output.to_dict())
    else:
        output = Location(**output_dict)
    return output
