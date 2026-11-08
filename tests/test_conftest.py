import pytest


def test_requiere_crudos(requiere_crudos, monkeypatch):
    requiere_crudos(True, "no se usa")
    monkeypatch.delenv("CI", raising=False)
    with pytest.raises(pytest.skip.Exception, match="faltan"):
        requiere_crudos(False, "faltan crudos")
    monkeypatch.setenv("CI", "true")
    with pytest.raises(pytest.fail.Exception, match="faltan"):
        requiere_crudos(False, "faltan crudos")
