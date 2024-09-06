FROM python:3.12-slim

RUN apt update && apt install -y texlive-science texlive-latex-extra latexmk

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY app/ .
RUN mkdir "config"

EXPOSE 5000

ENTRYPOINT ["gunicorn", "web:app", "-b", "0.0.0.0:5000"]
