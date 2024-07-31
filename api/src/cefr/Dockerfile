#fast api uvicorn app with python3.10

FROM python:3.10.0-slim-buster


LABEL name="fastAPI CEFR level checker"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ="Asia/Tashkent"

WORKDIR /app

# install dependencies
COPY src/cefr/requirements.txt /app/requirements.txt

COPY src/cefr/newmain.py /app/main.py

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# RUN #apt-get update && apt-get install -y tzdata

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

expose 8080

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


# docker build -t speaklish_payme . &&  docker stop speaklish_payme && docker rm speaklish_payme && docker run -d -p 8080:8080 --name speaklish_payme speaklish_payme