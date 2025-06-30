FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install build-essential binutils libproj-dev gdal-bin curl -y

# Install Python dependencies
ADD ./requirements.txt /app/requirements.txt
RUN pip install setuptools && pip3 install -U pip && pip install -r requirements.txt

# Clean up build dependencies
RUN apt-get --purge autoremove build-essential -y

# Copy application code
COPY . /app

# Copy and prepare entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000
CMD ["/usr/local/bin/entrypoint.sh"]