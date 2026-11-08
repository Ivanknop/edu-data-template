import urllib.error

import pytest

from edu_data.descarga import descargar


def _error(codigo):
    return urllib.error.HTTPError("http://x", codigo, "error", {}, None)


def test_descarga_y_no_pisa(tmp_path):
    destino = tmp_path / "sub" / "a.csv"
    assert descargar("http://x", destino, obtener=lambda url: b"uno")
    assert destino.read_bytes() == b"uno"
    assert not descargar("http://x", destino, obtener=lambda url: b"dos")
    assert destino.read_bytes() == b"uno"
    assert not list(destino.parent.glob("*.parcial"))


def test_reintenta_errores_del_servidor(tmp_path):
    respuestas = [_error(503), _error(502), b"ok"]

    def obtener(url):
        r = respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    assert descargar("http://x", tmp_path / "a", obtener=obtener, espera=0)
    assert (tmp_path / "a").read_bytes() == b"ok"


def test_no_reintenta_errores_del_cliente(tmp_path):
    llamadas = []

    def obtener(url):
        llamadas.append(url)
        raise _error(404)

    with pytest.raises(urllib.error.HTTPError):
        descargar("http://x", tmp_path / "a", obtener=obtener, espera=0)
    assert len(llamadas) == 1
    assert not (tmp_path / "a").exists()


def test_se_agotan_los_reintentos(tmp_path):
    def obtener(url):
        raise _error(500)

    with pytest.raises(urllib.error.HTTPError):
        descargar("http://x", tmp_path / "a", reintentos=2, obtener=obtener, espera=0)


def test_reintentos_invalidos(tmp_path):
    with pytest.raises(ValueError, match="reintentos"):
        descargar("http://x", tmp_path / "a", reintentos=0, obtener=lambda url: b"x")
    assert not (tmp_path / "a").exists()


def test_rechaza_html(tmp_path):
    with pytest.raises(RuntimeError):
        descargar(
            "http://x",
            tmp_path / "a.xlsx",
            obtener=lambda url: b"  <!DOCTYPE html><html>",
            rechazar_html=True,
        )
    assert not (tmp_path / "a.xlsx").exists()
