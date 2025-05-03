FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
LABEL authors="Stefan Walser"

RUN apt-get update && \
    apt-get install -y latexmk texlive-latex-extra texlive-science git && \
    rm -rf /var/lib/apt/lists/*
