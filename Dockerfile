FROM python:3

ARG TELEGRAM_API_KEY
ENV TELEGRAM_API_KEY=$TELEGRAM_API_KEY

COPY main.py /
COPY requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]
