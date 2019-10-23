FROM python:3.8-buster

MAINTAINER A.A. Trubilin <aatrubilin@gmail.com>

WORKDIR /redditbot

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod 755 /redditbot

ENV TELEGRAM_TOKEN <TELEGRAM_TOKEN>
#ENV TELEGRAM_PROXY <TELEGRAM_PROXY>
#ENV TELEGRAM_ADMIN_ID <ADMIN_ID>
#ENV GOOGLE_API_KEY <GOOGLE_API_KEY>
ENV LOGGER_LEVEL INFO
ENV DB_URL sqlite:///db.sqlite

CMD python app.py
