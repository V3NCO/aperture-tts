FROM intel/intel-extension-for-pytorch:2.8.10-xpu
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV XDG_CACHE_HOME=/tmp/.cache
ENV TMPDIR=/tmp

RUN apt-get update && apt-get install -y git-lfs

ADD . /app
WORKDIR /app

# RUN git lfs pull
# RUN uv python install
RUN python -c "import torch; print(f'torch=={torch.__version__.split(\"+\")[0]}')" > constraints.txt
RUN uv pip install --system -c constraints.txt .
RUN rm -rf /root/.cache /tmp/.cache || true


COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 7272

# ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["python", "main.py"]
