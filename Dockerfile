FROM intel/intel-extension-for-pytorch:2.8.10-xpu
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV XDG_CACHE_HOME=/tmp/.cache
ENV TMPDIR=/tmp

RUN apt-get update && apt-get install -y git-lfs espeak-ng build-essential

ADD . /app
WORKDIR /app

# RUN git lfs pull
# RUN uv python install
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

# ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["python", "main.py"]
