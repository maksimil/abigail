FROM python:3

COPY ./src /src/src
COPY ./requirements.txt /src/requirements.txt
COPY ./env.sh /src/env.sh

RUN pip install -r /src/requirements.txt

WORKDIR /src

CMD ["sh", "./src/main.sh"]
