from lib.db import GeocodeResult


def test_geocode_result():
    r = GeocodeResult()
    obj = {"key": "value"}
    key = "a random address"
    output = r.get(key)
    assert output is None
    r.set(key, obj)
    assert str(r.get(key)) == str(obj)
