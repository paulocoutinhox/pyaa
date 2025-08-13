FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    nano \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-roboto \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# pip
RUN python3 -m pip install --upgrade pip

# uwsgi
RUN python3 -m pip install uwsgi

# create user/group
ENV USER=docker \
    GROUP=docker \
    UID=12345 \
    GID=23456 \
    HOME=/app

WORKDIR ${HOME}

RUN addgroup --gid "${GID}" "${GROUP}" \
    && adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --ingroup "${GROUP}" \
    --no-create-home \
    --uid "${UID}" \
    "${USER}"

# install app
COPY --chown=${USER}:${GROUP} . /app
RUN chown -R ${USER}:${GROUP} /app
WORKDIR /app

# change to a non-root user
USER ${USER}

# setup app
RUN make setup
RUN make deps

# expose ports
EXPOSE 8000

# entrypoint
ENTRYPOINT ["/app/app-entrypoint.sh"]
