import pytest


@pytest.fixture(scope="function", params=["", " "])
def empty_string(request):
    return request.param