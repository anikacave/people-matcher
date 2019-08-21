import time

from lib import tasks


def test_add():
    res = tasks.add.delay(1, 2)
    success = False
    val = res.get(timeout=5)
    assert val == 3


if __name__ == "__main__":
    test_add()
