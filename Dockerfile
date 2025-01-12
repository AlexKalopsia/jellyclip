FROM alpine:3.15
ARG SERVER_PLATFORM
ARG SERVER_URL
ARG SERVER_TOKEN
ARG STREAMABLE_LOGIN
ARG STREAMABLE_PASSWORD
RUN apk --no-cache add build-base
RUN apk --no-cache add tzdata
RUN apk --no-cache add ffmpeg
RUN apk --no-cache add python3
RUN apk --no-cache add python3-dev
RUN apk --no-cache add py-pip
RUN cd /usr/bin \
  && ln -sf python3.9 python
ENV TZ=America/New_York
ENV SERVER_PLATFORM=$SERVER_PLATFORM
ENV SERVER_URL=$SERVER_URL
ENV SERVER_TOKEN=$SERVER_TOKEN
ENV STREAMABLE_LOGIN=$STREAMABLE_LOGIN
ENV STREAMABLE_PASSWORD=$STREAMABLE_PASSWORD
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN set FLASK_APP=main.py
CMD flask run --host 0.0.0.0
