FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN pip install setuptools
RUN apt-get update && apt-get install build-essential binutils libproj-dev gdal-bin curl -y

RUN pip3 install -U pip

RUN pip install -r requirements.txt
RUN apt-get --purge autoremove build-essential -y

COPY . /app
COPY entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entrypoint.sh

CMD ["/usr/local/bin/entrypoint.sh"] 

EXPOSE 5000
