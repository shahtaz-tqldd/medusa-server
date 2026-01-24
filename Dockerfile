FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        binutils \
        libgdal-dev \
        gdal-bin \
        libproj-dev \
        proj-bin \
        curl \
        netcat-openbsd && \
    pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000
CMD ["/usr/local/bin/entrypoint.sh"]
