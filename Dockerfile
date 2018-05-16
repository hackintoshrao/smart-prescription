FROM ubuntu:latest
MAINTAINER Karthic Rao "rao@upyourgame.ai"
RUN apt-get update -y
RUN apt-get install  --assume-yes python-pyaudio python-numpy
RUN apt-get install  --assume-yes -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["bot-server.py"]
