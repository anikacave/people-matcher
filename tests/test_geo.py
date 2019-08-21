from unittest.mock import patch

from lib.geo import Location, geocode, rate_limited_geocode

address_to_location = {
    "3201 Bee Caves Rd, Austin, TX 78746": Location(
        address="3201 Bee Caves Rd, Austin, TX 78746",
        latitude=30.2730421,
        longitude=-97.8024122,
    ),
    "9617 Anderson Mill Rd, Austin, TX 78750": Location(
        address="9617 Anderson Mill Rd, Austin, TX 78750",
        latitude=30.4481241,
        longitude=-97.7935201,
    ),
    "9422 N Lamar Blvd, Austin, TX 78753": Location(
        address="9422 N Lamar Blvd, Austin, TX 78753",
        latitude=30.3640859,
        longitude=-97.6991223,
    ),
}


def test_geocode():
    addr = "3201 Bee Caves Rd, Austin, TX 78746"
    correct_loc = address_to_location[addr]
    with patch("lib.geo.rate_limited_geocode") as mocked:
        mocked.return_value = correct_loc
        # The following line will still call the un-mocked rate_limited_geocode().
        # assert correct_loc == rate_limited_geocode(addr)
        loc_from_geocode = geocode(addr)
        assert correct_loc == loc_from_geocode

    with patch("lib.geo.rate_limited_geocode") as mocked:
        # Even if rate_limited_geocode does not return anything,
        # the database should have the value stored, so geocode()
        # should return the correct value.
        mocked.return_value = None
        loc_from_geocode = geocode(addr)
        assert correct_loc == loc_from_geocode
