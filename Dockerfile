FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

ENV TZ=Asia/Dhaka
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN pip install setuptools
RUN apt-get update && apt-get install build-essential binutils libproj-dev gdal-bin curl -y

# for weasyprint library
RUN apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libharfbuzz-subset0 -y

RUN pip3 install -U pip

RUN pip install -r requirements.txt
RUN apt-get --purge autoremove build-essential -y

COPY . /app
COPY entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entrypoint.sh
CMD ["entrypoint.sh"]

EXPOSE 5000 5001

