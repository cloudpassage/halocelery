FROM docker.io/halotools/python-sdk:ubuntu-16.04_sdk-1.0.6
MAINTAINER toolbox@cloudpassage.com

ENV HALO_API_HOSTNAME=api.cloudpassage.com
ENV HALO_API_PORT=443

ENV APP_USER=fieryboat
ENV APP_GROUP=fieryboatgroup


# Install components from pip
RUN pip install \
    boto3==1.4.3 \
    celery[redis]==4.0.2 \
    docker==2.6.1 \
    flower==0.9.1

# Copy over the app
RUN mkdir -p /app/halocelery

ADD . /app/halocelery

RUN cd /app/halocelery

WORKDIR /app/

# Set the user and chown the app
RUN groupadd ${APP_GROUP}

RUN useradd \
        --groups ${APP_GROUP} \
        --shell /bin/sh \
        --home-dir /app \
        ${APP_USER}

RUN chown -R ${APP_USER}:${APP_GROUP} /app

USER ${APP_USER}
