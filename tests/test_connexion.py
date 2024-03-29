import pytest
from debiai.debiai import Debiai
from tests.config import get_config

config = get_config()

PROJECT_NAME = "test_project"


def test_no_url():
    with pytest.raises(ValueError) as execution_info:
        Debiai(None)
    assert "URL cannot be empty" in str(execution_info.value)

    with pytest.raises(ValueError) as execution_info:
        Debiai("")
    assert "URL cannot be empty" in str(execution_info.value)

    with pytest.raises(ValueError) as execution_info:
        Debiai({})
    assert "URL is not valid" in str(execution_info.value)


def test_unreachable_url():
    with pytest.raises(ConnectionError) as execution_info:
        Debiai("http://IDONTEXIST.com")
    assert "Unable to connect" in str(execution_info.value)

    with pytest.raises(ConnectionError) as execution_info:
        Debiai("NOT_AN_URL")
    assert "Unable to connect" in str(execution_info.value)
