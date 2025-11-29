FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN uv python install
RUN uv sync --frozen

EXPOSE 7272

ENV PATH="/app/.vexznv/bin:$PATH"

CMD [ "uv", "run", "main.py" ]
