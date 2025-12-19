FROM python:alpine

WORKDIR /tibber2mqtt

COPY requirements.txt ./
COPY tibber2mqtt ./src

RUN pip install --no-cache-dir -r ./requirements.txt

ENV PYTHONUNBUFFERED=1
CMD [ "python3", "./src/tibber2mqtt.py","--config","/config/tibber2mqtt.yaml"]
