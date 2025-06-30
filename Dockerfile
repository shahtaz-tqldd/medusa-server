FROM python:3.12-slim 

ENV PYTHONUNBUFFERED=1 

WORKDIR /app 

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install system dependencies and Python packages in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        binutils \
        libproj-dev \
        gdal-bin \
        curl \
        netcat-openbsd && \
    pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000
CMD ["/usr/local/bin/entrypoint.sh"]