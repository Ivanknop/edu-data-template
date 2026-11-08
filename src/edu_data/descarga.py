"""Descarga de insumos a data/raw/: nunca pisa un archivo existente y reintenta errores 5xx."""

import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

AGENTE = "Mozilla/5.0 (edu-data-script)"


def abrir(url: str, abridor: urllib.request.OpenerDirector | None = None, timeout=60) -> bytes:
    """Contenido de `url` con User-Agent de navegador (algunos portales rechazan el de Python)."""
    abridor = abridor or urllib.request.build_opener()
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with abridor.open(pedido, timeout=timeout) as respuesta:
        return respuesta.read()


def _es_html(contenido: bytes) -> bool:
    return contenido.lstrip()[:15].lower().startswith((b"<!doctype", b"<html"))


def descargar(
    url: str,
    destino: str | Path,
    reintentos: int = 3,
    obtener: Callable[[str], bytes] = abrir,
    espera: float = 2.0,
    rechazar_html: bool = False,
) -> bool:
    """Baja `url` a `destino` si no existe. False si ya estaba (no se toca).

    Reintenta errores del servidor (5xx) y de conexión, con espera creciente. `obtener` permite
    otro mecanismo (p. ej. con cookie). `rechazar_html`: error si llega una página en lugar del
    archivo. Se escribe a un temporal y se renombra: un corte no deja un archivo a medias.
    """
    if reintentos < 1:
        raise ValueError(f"reintentos debe ser al menos 1 (es {reintentos})")
    destino = Path(destino)
    if destino.exists():
        return False
    for intento in range(1, reintentos + 1):
        try:
            contenido = obtener(url)
            break
        except urllib.error.HTTPError as error:
            if error.code < 500 or intento == reintentos:
                raise
        except (urllib.error.URLError, TimeoutError):
            if intento == reintentos:
                raise
        time.sleep(espera * intento)
    if rechazar_html and _es_html(contenido):
        raise RuntimeError(f"Se recibió una página HTML en lugar del archivo: {url}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".parcial")
    parcial.write_bytes(contenido)
    parcial.replace(destino)
    return True
