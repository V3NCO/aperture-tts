FROM intel/intel-optimized-pytorch:xpu-latest
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y git-lfs

ADD . /app
WORKDIR /app

RUN git lfs pull
RUN uv python install
RUN uv sync --frozen

EXPOSE 7272

ENV PATH="/app/.venv/bin:$PATH"

CMD [ "uv", "run", "main.py" ]
