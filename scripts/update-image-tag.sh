#!/usr/bin/env bash
# =============================================================
# update-image-tag.sh
# Atualiza a tag da imagem no kustomization.yaml (base)
# Uso: ./scripts/update-image-tag.sh <nova-tag>
# =============================================================

set -euo pipefail

NEW_TAG="${1:?Erro: informe a nova tag como argumento}"

KUSTOMIZATION_FILE="k8s/base/kustomization.yaml"

if [ ! -f "$KUSTOMIZATION_FILE" ]; then
    echo "Erro: $KUSTOMIZATION_FILE nao encontrado"
    exit 1
fi

echo "Atualizando image tag para: $NEW_TAG"

sed -i "s/newTag: .*/newTag: ${NEW_TAG}/" "$KUSTOMIZATION_FILE"

echo "Tag atualizada com sucesso em $KUSTOMIZATION_FILE"
grep "newTag" "$KUSTOMIZATION_FILE"
