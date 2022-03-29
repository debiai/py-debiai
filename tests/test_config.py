from debiai.config import DebiaiConfig


def test_config():
    config = DebiaiConfig()
    assert config is not None
    assert config.debiai_app_url is not None
