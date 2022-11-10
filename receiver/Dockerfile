FROM ubuntu
LABEL maintainer="steven.chang420@gmail.com"
RUN apt update -y && apt install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]