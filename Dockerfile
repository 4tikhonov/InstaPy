FROM ubuntu:16.04

MAINTAINER Grossmann Tim <contact.timgrossmann@gmail.com>

# Set env variables
ENV CHROME https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
ENV CRHOMEDRIVER http://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip

# Environment setup
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
        apt-utils \
        locales \
        unzip \
	sed \
        python3-pip \
        python3-dev \
        build-essential \
        libgconf2-4 \
        libnss3-1d \
        libxss1 \
        libssl-dev \
        libffi-dev \
        xvfb \
        wget \
        libcurl3 \
        gconf-service \
        libasound2 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libfontconfig1 \
        libgdk-pixbuf2.0-0 \
        libgtk2.0-0 \
        libpango1.0-0 \
        libxcomposite1 \
        libxtst6 \
        fonts-liberation \
        libappindicator1 \
        xdg-utils \
        git \
	lsb-release \
    && pip3 install --upgrade pip \
    && locale-gen "en_US.UTF-8" \
    && dpkg-reconfigure locales 

RUN pip3 install --upgrade pip \ 
    && apt-get -f install

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Installing latest chrome
RUN cd ~ \
    && wget ${CHROME} \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -y -f \
    && rm google-chrome-stable_current_amd64.deb

# Cleanup
RUN apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Adding InstaPy
RUN mkdir InstaPy \
    && mkdir InstaPy/assets \
    wget ${CRHOMEDRIVER} \
    && unzip chromedriver_linux64 \
    && mv chromedriver InstaPy/assets/chromedriver \
    && chmod +x InstaPy/assets/chromedriver \
    && chmod 755 InstaPy/assets/chromedriver \
    && cd InstaPy \
    && pip install . \
    && pip install langdetect \
    && pip install daemonize \
    && pip install arrow \
    && pip install selenium clarifai pyvirtualdisplay emoji GitPython

# Copying the your quickstart file into the container and setting directory
COPY docker_conf/all_in_one/quickstart.py ./InstaPy
WORKDIR /InstaPy
ADD /* ./

CMD ["python3.5", "quickstart.py"]

