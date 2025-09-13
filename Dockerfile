FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim
LABEL authors="Stefan Walser"

RUN apt-get update && \
    apt-get install -y latexmk texlive-latex-extra texlive-science && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /
RUN uv sync

COPY app /app

ENTRYPOINT ["uv", "run", "app/main.py"]
