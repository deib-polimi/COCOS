FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_DEBUG 1

EXPOSE 5000

CMD [ "python", "main.py" ]