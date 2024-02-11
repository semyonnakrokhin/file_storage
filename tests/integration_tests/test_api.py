from fastapi_app.src.config import DatabaseSettings


def test1():
    settings_test = DatabaseSettings()
    print(settings_test.dsn)
    print(settings_test.mode)
    a = 1
    b = 2
    assert a != b
