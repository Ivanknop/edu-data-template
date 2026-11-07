#!/usr/bin/env bash
# Crea un proyecto de análisis nuevo a partir de esta plantilla.
# Uso: scripts/nuevo-proyecto.sh <directorio-destino>
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: $0 <directorio-destino>" >&2
  exit 1
fi

PLANTILLA="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTINO="$1"
NOMBRE="$(basename "$DESTINO")"

if [[ -e "$DESTINO" ]]; then
  echo "Error: '$DESTINO' ya existe." >&2
  exit 1
fi

mkdir -p "$DESTINO"
DESTINO="$(cd "$DESTINO" && pwd)"

# Solo archivos versionados: deja afuera todo lo ignorado
git -C "$PLANTILLA" ls-files -z | (cd "$PLANTILLA" && xargs -0 cp --parents -t "$DESTINO")

cd "$DESTINO"

# Lo exclusivo de la plantilla no pasa al proyecto
rm -f scripts/nuevo-proyecto.sh
rmdir --ignore-fail-on-non-empty scripts 2>/dev/null || true
sed -i '/<!-- plantilla:inicio -->/,/<!-- plantilla:fin -->/d' README.md

# En el proyecto derivado el lock se versiona
sed -i '/^uv\.lock$/d' .gitignore

# Nombre del proyecto en título del README y en el devcontainer
sed -i "1s/.*/# $NOMBRE/" README.md
sed -i "s/\"name\": \"edu-data-template\"/\"name\": \"$NOMBRE\"/" .devcontainer/devcontainer.json

chmod +x .devcontainer/post-create.sh

echo "Proyecto '$NOMBRE' creado en $DESTINO"
echo "Siguiente: abrir la carpeta en VS Code → Dev Containers: Reopen in Container"