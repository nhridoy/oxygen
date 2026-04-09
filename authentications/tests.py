from django.conf import settings


def test_settings_module_loads() -> None:
    assert settings.SECRET_KEY
