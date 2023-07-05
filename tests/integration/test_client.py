from mserv.socketlib.client import hello_world


def test_client():
    assert hello_world() == "Hello World"
