FROM docker.io/halotools/python-sdk:ubuntu-18.04_sdk-latest_py-3.6

MAINTAINER toolbox@cloudpassage.com

ARG DEBIAN_FRONTEND=noninteractive

ENV HALO_API_HOSTNAME='api.cloudpassage.com'
ENV HALO_API_PORT='443'

ENV APP_USER='halocelery'
ENV APP_GROUP='halocelery'


# Install components from pip3
RUN pip3 install \
    boto3==1.17.34 \
    celery[redis]==5.0.5 \
    docker==4.4.4 \
    flower==0.9.7 \
	redis==3.5.3 \
	cloudpassage==1.6.2

# Install expect, so that we can run 'unbuffer'
RUN apt-get update && \
    apt-get install -y \
    expect

# Copy over the testing script
COPY run-tests.sh /app/

# Copy over the app
RUN mkdir -p /app/halocelery

ADD . /app/halocelery

RUN cd /app/halocelery

WORKDIR /app/

# Set the user and chown the app
RUN groupadd ${APP_GROUP}

RUN useradd \
        -g ${APP_GROUP} \
        --shell /bin/sh \
        --home-dir /app \
        ${APP_USER}

RUN chown -R ${APP_USER}:${APP_GROUP} /app

USER ${APP_USER}
