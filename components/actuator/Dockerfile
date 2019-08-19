FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_APP "main.py"
ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 5000

CMD [ "flask", "run" ]