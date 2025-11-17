FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        locales && \
    rm -rf /var/lib/apt/lists/*

RUN sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m microblog
USER microblog

ENV FLASK_APP=microblog.py

CMD ["flask", "run", "--host=0.0.0.0"]
