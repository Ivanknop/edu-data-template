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

# Origen y versión de la plantilla, para poder actualizar el proyecto después
URL_PLANTILLA="$(git -C "$PLANTILLA" remote get-url origin 2>/dev/null || echo "$PLANTILLA")"
# Se guarda HTTPS: en un contenedor sin clave SSH, el clon para actualizar fallaría
if [[ "$URL_PLANTILLA" =~ ^git@([^:]+):(.+)$ ]]; then
  URL_PLANTILLA="https://${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
elif [[ "$URL_PLANTILLA" =~ ^ssh://git@([^/]+)/(.+)$ ]]; then
  URL_PLANTILLA="https://${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
fi
VERSION_PLANTILLA="$(git -C "$PLANTILLA" describe --tags --always)"
if [[ -n "$(git -C "$PLANTILLA" status --porcelain)" ]]; then
  echo "Aviso: la plantilla tiene cambios sin commitear; el proyecto los incluye," >&2
  echo "pero .plantilla.json registra la versión $VERSION_PLANTILLA." >&2
fi

mkdir -p "$DESTINO"
DESTINO="$(cd "$DESTINO" && pwd)"

# Solo archivos versionados: deja afuera data todo lo ignorado
git -C "$PLANTILLA" ls-files -z | (cd "$PLANTILLA" && xargs -0 cp --parents -t "$DESTINO")

cd "$DESTINO"

# Lo exclusivo de la plantilla no pasa al proyecto
rm -f scripts/nuevo_proyecto.sh CHANGELOG.md
rm -rf .plantilla
rmdir --ignore-fail-on-non-empty scripts 2>/dev/null || true

cat > .plantilla.json <<JSON
{"plantilla": "$URL_PLANTILLA", "version": "$VERSION_PLANTILLA", "so": "$SO"}
JSON

# README: solo las secciones del proyecto (el entorno está en docs/entorno.md)
sed -i '/<!-- plantilla:inicio -->/,/<!-- plantilla:fin -->/d' README.md
# El bloque de proyecto está comentado en la plantilla: acá se descomenta
sed -i '/^<!-- proyecto:inicio$/d; /^proyecto:fin -->$/d' README.md
sed -i "s|(URL_PLANTILLA)|(${URL_PLANTILLA%.git})|; s|VERSION_PLANTILLA|$VERSION_PLANTILLA|" README.md

# docs/entorno.md: queda solo la sección del sistema operativo elegido, sin las marcas
for s in "${SISTEMAS[@]}"; do
  if [[ "$s" == "$SO" ]]; then
    sed -i "/<!-- so:$s:\(inicio\|fin\) -->/d" docs/entorno.md
  else
    sed -i "/<!-- so:$s:inicio -->/,/<!-- so:$s:fin -->/d" docs/entorno.md
  fi
done

# Sin líneas en blanco dobles donde había bloques
for f in README.md docs/entorno.md; do
  cat -s "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done

# En el proyecto derivado el lock se versiona
sed -i '/^uv\.lock$/d' .gitignore

# Nombre del proyecto en título del README y en el devcontainer
sed -i "1s/.*/# $NOMBRE/" README.md
sed -i "s/\"name\": \"edu-data-template\"/\"name\": \"$NOMBRE\"/" .devcontainer/devcontainer.json

# pyproject: el nombre del paquete importable (edu_data) no cambia, lo fija tool.hatch
SLUG="$(echo "$NOMBRE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
sed -i "s/^name = \"edu-data-template\"$/name = \"$SLUG\"/" pyproject.toml
sed -i 's/^description = .*/description = "Completar: qué analiza este proyecto"/' pyproject.toml

chmod +x .devcontainer/post-create.sh

echo "Proyecto '$NOMBRE' ($SO) creado en $DESTINO"
echo "Siguiente: abrir la carpeta en VS Code → Dev Containers: Reopen in Container"
echo "Antes del primer commit: completar README.md, data/README.md y la description de pyproject.toml"