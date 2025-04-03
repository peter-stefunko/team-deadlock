FROM postgres:17.2-bullseye

USER root
RUN apt-get update 
RUN apt-get install -y build-essential 
RUN apt-get install -y git
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-server-dev-all

RUN rm -rf /var/lib/apt/lists/*

# Clone, build, and install the pgvector extension
RUN cd /tmp \
  && git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git \
  && cd pgvector \
  && make \
  && make install
