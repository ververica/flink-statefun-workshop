FROM python:3.7-alpine

RUN mkdir -p /app

WORKDIR /app

RUN apk --no-cache --update-cache add \
    gcc \
    gfortran \
    build-base \
    wget \
    freetype-dev \
    libpng-dev \
    openblas-dev

# The following two lines would be removed once statefun would be published to PyPI
COPY apache_flink_statefun-2.0_SNAPSHOT-py3-none-any.whl /app

RUN pip install apache_flink_statefun-2.0_SNAPSHOT-py3-none-any.whl

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY main.py /app

COPY entities_pb2.py /app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w 4", "main:app"]

