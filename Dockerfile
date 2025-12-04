FROM intel/intel-extension-for-pytorch:2.8.10-xpu
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV XDG_CACHE_HOME=/tmp/.cache
ENV TMPDIR=/tmp

RUN apt-get update && apt-get install -y git-lfs espeak-ng build-essential gdb

ADD . /app
WORKDIR /app

# --- DEBUG SCRIPT CREATION ---
RUN echo "import sys" > debug.py && \
    echo "print('DEBUG: Starting Python XPU Check...')" >> debug.py && \
    echo "import torch" >> debug.py && \
    echo "print(f'DEBUG: Torch Version: {torch.__version__}')" >> debug.py && \
    echo "try:" >> debug.py && \
    echo "    import intel_extension_for_pytorch as ipex" >> debug.py && \
    echo "    print(f'DEBUG: IPEX Version: {ipex.__version__}')" >> debug.py && \
    echo "except ImportError as e:" >> debug.py && \
    echo "    print(f'DEBUG: IPEX Import Failed: {e}')" >> debug.py && \
    echo "print('DEBUG: Checking XPU availability...')" >> debug.py && \
    echo "try:" >> debug.py && \
    echo "    if torch.xpu.is_available():" >> debug.py && \
    echo "        print(f'DEBUG: XPU Available! Device Count: {torch.xpu.device_count()}')" >> debug.py && \
    echo "        print(f'DEBUG: Device Name: {torch.xpu.get_device_name(0)}')" >> debug.py && \
    echo "        t = torch.tensor([1.0], device='xpu')" >> debug.py && \
    echo "        print('DEBUG: Tensor created on XPU successfully.')" >> debug.py && \
    echo "    else:" >> debug.py && \
    echo "        print('DEBUG: XPU NOT Available (is_available=False)')" >> debug.py && \
    echo "except Exception as e:" >> debug.py && \
    echo "    print(f'DEBUG: CRASH during XPU check: {e}')" >> debug.py

# --- CONSTRAINT & INSTALL LOGIC (Keep previous fix) ---
RUN echo "import torch" > get_constraints.py && \
    echo "print(f'torch=={torch.__version__}')" >> get_constraints.py && \
    echo "try:" >> get_constraints.py && \
    echo "    import torchaudio" >> get_constraints.py && \
    echo "    print(f'torchaudio=={torchaudio.__version__}')" >> get_constraints.py && \
    echo "except ImportError:" >> get_constraints.py && \
    echo "    pass" >> get_constraints.py && \
    python get_constraints.py > constraints.txt && \
    rm get_constraints.py

RUN python -m pip install --no-cache-dir \
    -c constraints.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    .

RUN rm -rf /root/.cache /tmp/.cache || true

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 7272

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["python", "main.py"]