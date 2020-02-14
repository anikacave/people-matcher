import time

from lib import tasks
import tests.test_recommender as rec


def test_add():
    res = tasks.add.delay(1, 2)
    success = False
    val = res.get(timeout=5)
    rec.test_race_filter()
    assert val == 3


if __name__ == "__main__":
    test_add()
