FROM python:3.12-slim

RUN apt update && \
    apt install -y latexmk texlive-latex-extra texlive-science && \
    apt clean

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "app/main.py"]
