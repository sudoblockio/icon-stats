FROM python:3.12-slim-bullseye

ARG SERVICE_NAME
ENV SERVICE_NAME ${SERVICE_NAME:-api}

# GO ENV VARS
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/opt:${PYTHONPATH}"

WORKDIR /opt

# TMP while sqlmodel is being upgraded to pyd2 / sqla2
RUN apt-get update && apt-get install -y git && apt-get clean

RUN pip install --upgrade pip
COPY ./requirements-$SERVICE_NAME.txt .
COPY ./requirements-common.txt .
RUN pip install -r ./requirements-$SERVICE_NAME.txt -r ./requirements-common.txt

COPY icon_stats ./icon_stats

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
