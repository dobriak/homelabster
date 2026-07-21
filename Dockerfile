FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HOMELABSTER_DATA_DIR=/data

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

COPY config/services.yaml.example config/categories.yaml.example config/ipam.yaml.example /defaults/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint"]
CMD ["uv", "run", "--no-sync", "fastapi", "run", "src/homelabster/main.py", "--host", "0.0.0.0", "--port", "8000"]
