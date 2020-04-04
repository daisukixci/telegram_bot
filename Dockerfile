FROM python:3

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY bot/ /bot
COPY main.py /
COPY config.yaml /

CMD [ "python", "main.py" ]
