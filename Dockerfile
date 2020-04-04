FROM python:3

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY app/ /app
COPY config.yaml /

CMD [ "python", "app/main.py" ]
