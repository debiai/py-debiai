import pytest
from debiai.debiai import Debiai
from debiai.config import DebiaiConfig


# The initial debiai_url = "http://localhost:3000"


config = DebiaiConfig()
debiai_url = config.debiai_app_url


def test_debiai_init_empty_url():
    with pytest.raises(ValueError):
        Debiai("")


def test_debiai_init_valid_url():
    test_url = debiai_url
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_init_sharp_url():
    test_url = debiai_url + "#"
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_add_slash():
    test_url = debiai_url + "/"
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_add_slash_and_sharp():
    test_url = debiai_url + "/" + "#"
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_empty_space():
    test_url = debiai_url + " "
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_space_then_slash():
    test_url = debiai_url + " " + "/"
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_slash_then_space():
    test_url = debiai_url + "/" + " "
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_slash_sharp_slash():
    test_url = debiai_url + "/" + "#" + "/"
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url


def test_debiai_uppercase():
    test_url = debiai_url.upper()
    debiai_instance = Debiai(test_url)
    assert debiai_instance.debiai_url == debiai_url
