FROM python:latest

RUN apt-get update
RUN apt-get install -y poppler-utils

WORKDIR /JobFitAIApp

COPY requirements.txt requirements.txt
COPY app/ ./app/

RUN pip install -r requirements.txt

CMD [ "python", "-m", "app.main"]