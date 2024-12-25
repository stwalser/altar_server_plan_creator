FROM python:3.13-slim

RUN apt update && \
    apt install -y latexmk texlive-latex-extra texlive-science git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip3 install -r requirements.txt && \
    rm -rf /root/.cache/pip

ADD app /app

ENTRYPOINT ["python3", "app/main.py"]
