"""
DebiAI python module configuration
"""

import os
from typing import Optional


class DebiaiConfig:
    """Global configuration object for Debiai"""

    def __init__(
        self,
        debiai_app_url: str = "http://localhost:3000/",
    ):

        self.debiai_app_url = debiai_app_url

    def __repr__(self):
        return (
            f"DebiaiConfig ( "
            f"debiai_app_url: {self.debiai_app_url} "
            f")"
        )


_DEBIAI_CONFIG: Optional[DebiaiConfig] = None


def configure_config(provided_config: Optional[DebiaiConfig] = None):
    global _DEBIAI_CONFIG

    if provided_config is not None:
        _DEBIAI_CONFIG = provided_config
    else:
        _DEBIAI_CONFIG = DebiaiConfig(
            debiai_app_url=os.environ.get("DEBIAI_APP_URL", "http://localhost:3000/")
        )


def get_config() -> DebiaiConfig:
    global _DEBIAI_CONFIG

    if _DEBIAI_CONFIG is None:
        configure_config()

    assert _DEBIAI_CONFIG is not None
    return _DEBIAI_CONFIG
