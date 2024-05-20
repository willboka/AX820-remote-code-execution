FROM debian:buster

RUN apt-get update
RUN apt install mosquitto -y

EXPOSE 1883/tcp

RUN mkdir /WORK
WORKDIR /WORK

COPY conf/mosquitto.conf .
COPY conf/acl.txt .
COPY conf/passwd.txt .

CMD ["mosquitto", "-c", "mosquitto.conf", "-v"]