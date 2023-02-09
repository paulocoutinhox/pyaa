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

# create folders
RUN mkdir -p /app/static && \
    mkdir -p /app/media && \
    mkdir -p /app/db && \
    chown -R docker:docker /app && \
    chmod -R 755 /app

# install app
COPY --chown=docker:docker . .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# change to a non-root user
USER ${USER}

# collect static files
RUN python3 manage.py collectstatic --noinput

# expose ports
EXPOSE 8000

# endtrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
