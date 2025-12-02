#!/bin/bash
set -e

# omg being able to hardcode because docker is so convinient
GLADOS_FILE="/app/glados-model/Models/GPT-SoVITS/GPT_weights/Portal_GLaDOS_GPT-SoVITS_v1.1-e15.ckpt"
DEBERTA_FILE="/app/deberta-v3-large/pytorch_model.bin"

lfs_pulled() {
    local file="$1"
    if [ ! -f "$file" ]; then
        return 0
    fi
    
    local size
    size=$(stat -c%s "$file" 2>/dev/null || echo 0)
    if [ "$size" -lt 2048 ]; then
        return 0
    else
        return 1
    fi
}

fetch_models() {
    echo "fetching git LFS"
}