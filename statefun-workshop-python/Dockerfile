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

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY main.py /app

COPY entities_pb2.py /app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w 4", "main:app"]

