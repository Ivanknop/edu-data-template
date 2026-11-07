#!/usr/bin/env bash
# Crea un proyecto de análisis nuevo a partir de esta plantilla.
# Uso: scripts/nuevo_proyecto.sh -name <nombre-o-ruta> -so <linux|windows>
set -euo pipefail

SISTEMAS=(linux windows)

uso() {
  echo "Uso: $0 -name <nombre-o-ruta> -so <$(IFS="|"; echo "${SISTEMAS[*]}")>" >&2
  exit 1
}

DESTINO=""
SO=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -name) DESTINO="${2:-}"; shift 2 ;;
    -so)   SO="${2:-}"; shift 2 ;;
    -h|-help|--help) uso ;;
    *) echo "Parámetro desconocido: $1" >&2; uso ;;
  esac
done

[[ -z "$DESTINO" || -z "$SO" ]] && uso
[[ " ${SISTEMAS[*]} " == *" $SO "* ]] || { echo "Sistema operativo no soportado: $SO" >&2; uso; }

PLANTILLA="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOMBRE="$(basename "$DESTINO")"

if [[ -e "$DESTINO" ]]; then
  echo "Error: '$DESTINO' ya existe." >&2
  exit 1
fi

mkdir -p "$DESTINO"
DESTINO="$(cd "$DESTINO" && pwd)"

# Solo archivos versionados: deja afuera data todo lo ignorado
git -C "$PLANTILLA" ls-files -z | (cd "$PLANTILLA" && xargs -0 cp --parents -t "$DESTINO")

cd "$DESTINO"

# Lo exclusivo de la plantilla no pasa al proyecto
rm -f scripts/nuevo_proyecto.sh
rmdir --ignore-fail-on-non-empty scripts 2>/dev/null || true
sed -i '/<!-- plantilla:inicio -->/,/<!-- plantilla:fin -->/d' README.md

# Secciones por sistema operativo: queda solo la del elegido, sin las marcas
for s in "${SISTEMAS[@]}"; do
  if [[ "$s" == "$SO" ]]; then
    sed -i "/<!-- so:$s:\(inicio\|fin\) -->/d" README.md
  else
    sed -i "/<!-- so:$s:inicio -->/,/<!-- so:$s:fin -->/d" README.md
  fi
done

# Sin líneas en blanco dobles donde había bloques
cat -s README.md > README.md.tmp && mv README.md.tmp README.md

# En el proyecto derivado el lock se versiona
sed -i '/^uv\.lock$/d' .gitignore

# Nombre del proyecto en título del README y en el devcontainer
sed -i "1s/.*/# $NOMBRE/" README.md
sed -i "s/\"name\": \"edu-data-template\"/\"name\": \"$NOMBRE\"/" .devcontainer/devcontainer.json

chmod +x .devcontainer/post-create.sh

echo "Proyecto '$NOMBRE' ($SO) creado en $DESTINO"
echo "Siguiente: abrir la carpeta en VS Code → Dev Containers: Reopen in Container"