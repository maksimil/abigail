FROM python:3

COPY ./src /src/src
COPY ./requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

CMD ["python", "/src/src/main.py"]