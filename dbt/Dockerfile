FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dbt-postgres==1.7.4 \
    protobuf==4.25.1

WORKDIR /app

COPY . .

CMD dbt debug && dbt build