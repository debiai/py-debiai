from debiai.debiai import Debiai
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)


def test_count_words():
    assert 1 == 1, "Einstein quote counted incorrectly!"


def test_count_words2():
    assert 1 == 2, "Einstein quote counted incorrectly!"
