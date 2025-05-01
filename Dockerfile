FROM python:3.11

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache --no-dev

# Run the application.
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]


