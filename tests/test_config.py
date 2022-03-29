import pytest

from debiai.config import DebiaiConfig


@pytest.fixture
def default_config():
    config = DebiaiConfig()

    yield config
