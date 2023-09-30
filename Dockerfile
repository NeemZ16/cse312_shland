FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080


ENV FLASK_APP=my_flask.py

CMD python3 -u ./my_flask.py