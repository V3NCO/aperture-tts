#!/bin/bash
set -e

# --- INTEL ONEAPI SETUP ---
if [ -f /opt/intel/oneapi/setvars.sh ]; then
    source /opt/intel/oneapi/setvars.sh > /dev/null 2>&1
fi
export ZE_ENABLE_PCI_ID_DEVICE_ORDER=1
# --------------------------

echo "--- RUNNING DIAGNOSTIC ---"
# We run this in a subshell so if it segfaults, the entrypoint script doesn't die immediately
# and we can print a message.
(python debug.py) || echo "!!! DIAGNOSTIC CRASHED WITH EXIT CODE $? !!!"
echo "--- DIAGNOSTIC COMPLETE ---"

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

    TEMP_DIR="/tmp/repo"
    rm -rf "$TEMP_DIR"

    git clone --depth 1 "https://github.com/V3NCO/aperture-tts.git" "$TEMP_DIR"
    cd "$TEMP_DIR"
    git submodule update --init --recursive
    if [ -d "glados-model" ]; then
        cd glados-model
        git lfs pull
        cd ..
        cp -r glados-model/* /app/glados-model/
    fi

    if [ -d "deberta-v3-large" ]; then
        cd deberta-v3-large
        git lfs pull
        cd ..
        cp -r deberta-v3-large/* /app/deberta-v3-large/
    fi

    cd /app
    rm -rf "$TEMP_DIR"
    echo "models fetched i think"
}

if lfs_pulled "$GLADOS_FILE" || lfs_pulled "$DEBERTA_FILE"; then
    fetch_models
else
    echo "models present anyways lol"
fi

exec "$@"