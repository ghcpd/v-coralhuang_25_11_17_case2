FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m translate
WORKDIR /workspace

COPY . /workspace

RUN python3 -m venv /workspace/fixes/.venv && \
    . /workspace/fixes/.venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /workspace/fixes/requirements.txt && \
    mkdir -p /workspace/fixes/artifacts && \
    chown -R translate /workspace

USER translate
ENV PATH="/workspace/fixes/.venv/bin:$PATH"
ENV PYTHONPATH="/workspace/fixes/src"

CMD ["bash", "fixes/run_test.sh"]
