FROM debian:latest
ENV DEBIAN_FRONTEND noninteractive
ENV LANGUAGE C.UTF-8
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN echo 'Acquire::ForceIPv4 "true";' | tee /etc/apt/apt.conf.d/99force-ipv4

# Install as much as reasonable in one go to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    python \
    python-dev \
    python-tk \
    bash \
    curl \
    make \
    build-essential \
    gcc \
    supervisor \
    ca-certificates \
    less \
    sudo \
    htop \
    vcftools \
    fontconfig \
    crontab \
    tmpreaper \
    watch && \

    # Additional tools
    curl -SLk 'https://bootstrap.pypa.io/get-pip.py' | python && \
    curl -L https://github.com/tianon/gosu/releases/download/1.7/gosu-amd64 -o /usr/local/bin/gosu && chmod u+x /usr/local/bin/gosu && \

    # Cleanup
    cp -R /usr/share/locale/en\@* /tmp/ && rm -rf /usr/share/locale/* && mv /tmp/en\@* /usr/share/locale/ && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/groff/* /usr/share/info/* /tmp/* /var/cache/apt/* /root/.cache

ADD pip-requirements /dist/requirements.txt
RUN pip install -r /dist/requirements.txt

ENV PYTHONPATH /spiked1000g/src
ENV PYTHONIOENCODING utf-8
ENV PYTHONUNBUFFERED true

# Add crontab file in the cron directory
ADD crontab /etc/cron.d/cleantmp

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cleantmp

# Apply cron job
RUN crontab /etc/cron.d/cleantmp

# See .dockerignore for files that are ignored
# COPY . /anno
WORKDIR /spiked1000g

# Set supervisor as default cmd
CMD cron && /bin/bash -c "python src/api/main.py"
