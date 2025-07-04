FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "my_app"]