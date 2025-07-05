FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

# Presuming there is a `my_app` command provided by the project
RUN uv lock
RUN uv sync --locked

EXPOSE 80 8080 8000

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]