from mserv.services.abstract_service import hello_world


def test_service():
    assert hello_world() == "Hello World"
