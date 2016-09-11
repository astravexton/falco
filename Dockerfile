FROM python:3.5.2

MAINTAINER Nathan Barley <nathan@zyr.io>

WORKDIR /opt/falco
COPY . /opt/falco

RUN gcc ircize.c -o ircize \
    && mv ircize /usr/bin \
    && pip install -r requirements.txt

CMD ["python3", "falco.py", "config.json"]
