FROM python:3.10

# install dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

# install app
WORKDIR /app
COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt
COPY . .

# expose ports
EXPOSE 8000

# endtrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
