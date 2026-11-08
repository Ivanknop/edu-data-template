#!/usr/bin/env bash
set -euo pipefail

# Por si el volumen ya existía de antes con otro dueño
sudo chown -R vscode:vscode /home/vscode/.claude /home/vscode/.cache/uv /home/vscode/.venv

echo ">> Instalando dependencias Python con uv..."
uv sync

# Opcional (~300 MB): navegador sin interfaz para que Claude verifique visores con capturas.
# Se activa con INSTALAR_NAVEGADOR=1 en el host antes de abrir el contenedor (ver docs/entorno.md).
if [[ "${INSTALAR_NAVEGADOR:-0}" == "1" ]]; then
  echo ">> Instalando Chromium para Playwright..."
  uv run --with playwright playwright install --with-deps chromium
fi

echo ">> Listo."
echo "   Python:      $(uv run python --version)"
echo "   Claude Code: $(claude --version 2>/dev/null || echo 'no encontrado')"
echo "   Primera vez en esta máquina: ejecutá 'claude' y logueate."
