FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev \
    openjdk-11-jdk \
    libjpeg-dev zlib1g-dev libssl-dev libffi-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

COPY requirement.txt /app/requirement.txt

RUN pip3 install --no-cache-dir -r /app/requirement.txt

COPY . /app
EXPOSE 5020

CMD ["python3", "app.py"]















