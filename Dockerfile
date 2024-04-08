FROM python:3.12-slim

RUN apt update && apt install -y texlive-pictures texlive-science texlive-latex-extra latexmk procps

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY app/ .

ENTRYPOINT ["python3", "main.py"]
