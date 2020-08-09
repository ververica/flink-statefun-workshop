# Copyright 2020 Ververica GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

CMD ["gunicorn", "-b", "0.0.0.0:8888", "-w 4", "main:app"]

