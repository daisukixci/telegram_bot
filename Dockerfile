FROM python:3

RUN adduser bot

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ /bot
COPY main.py /
COPY config.yaml /

USER bot

CMD [ "python", "main.py" ]
