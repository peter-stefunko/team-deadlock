FROM python:3.13-slim-bullseye as prod

RUN apt-get update && apt-get install -y gcc && apt-get install -y libpq-dev gcc
RUN rm -rf /var/lib/apt/lists/*

ENV WORKERS_PER_CORE=3
RUN pip install poetry==1.8.4

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/
WORKDIR /app/

# Installing requirements
RUN poetry install --only main

# Cleanup
RUN apt-get purge -y gcc
RUN rm -rf /var/lib/apt/lists/*

# Copying actual application
COPY . /app/
CMD ["/usr/local/bin/python", "-m", "src"]

FROM prod as dev

RUN poetry install
CMD ["/usr/local/bin/python", "-m", "src"]
