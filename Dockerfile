FROM python:3.10

# install dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
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
    HOME=/app \
    PYTHONUNBUFFERED=1

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
ENTRYPOINT ["/app/docker-entrypoint.sh"]
