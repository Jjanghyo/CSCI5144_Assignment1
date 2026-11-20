FROM python:3.9

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

RUN uv sync

EXPOSE 5000 5001 5002 5003
