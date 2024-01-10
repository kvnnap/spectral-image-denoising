FROM python:3.11 as builder

ARG USER=kevin
ARG HOME=/home/$USER

# Install OpenEXR deps
RUN apt-get update \
 && apt-get -y --no-install-recommends install libopenexr-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash $USER
USER $USER
WORKDIR $HOME

# https://pylops.github.io/curvelops/installation.html#installation

COPY --chown=$USER:$USER CurveLab-2.1.3.tar.gz $HOME

RUN    cd $HOME \
    && wget https://www.fftw.org/fftw-2.1.5.tar.gz \
    && tar xvzf fftw-2.1.5.tar.gz \
    && rm fftw-2.1.5.tar.gz \
    && mkdir -p $HOME/opt/ \
    && mv fftw-2.1.5/ $HOME/opt/ \
    && cd $HOME/opt/fftw-2.1.5/ \
    && ./configure --with-pic --prefix=$HOME/opt/fftw-2.1.5 \
    && make \
    && make install \
    && cd $HOME \
    && tar xvzf CurveLab-2.1.3.tar.gz \
    && rm CurveLab-2.1.3.tar.gz \
    && mkdir -p $HOME/opt/ \
    && mv CurveLab-2.1.3/ $HOME/opt/ \
    && cd $HOME/opt/CurveLab-2.1.3/ \
    && sed -i 's/lexing\/pkge/kevin\/opt/' makefile.opt \
    && make lib

COPY --chown=$USER:$USER requirements.txt .
ENV FFTW=$HOME/opt/fftw-2.1.5 FDCT=$HOME/opt/CurveLab-2.1.3
RUN pip3 install --no-compile -r requirements.txt

FROM python:3.11-slim
ARG USER=kevin
ARG HOME=/home/$USER
RUN useradd -ms /bin/bash $USER \
    && mkdir -p /app/data \
    && chown -R $USER:$USER /app
# Install OpenEXR deps
RUN apt-get update \
 && apt-get -y install libopenexr-3-1-30 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
USER $USER
WORKDIR /app/data
COPY --chown=$USER:$USER --from=builder $HOME/opt $HOME/opt
COPY --chown=$USER:$USER --from=builder $HOME/.local $HOME/.local
COPY --chown=$USER:$USER core /app/core
COPY --chown=$USER:$USER evaluation /app/evaluation
COPY --chown=$USER:$USER utils /app/utils
COPY --chown=$USER:$USER version.py /app
ENV FFTW=$HOME/opt/fftw-2.1.5 FDCT=$HOME/opt/CurveLab-2.1.3
ENTRYPOINT ["python3", "-Xfrozen_modules=off", "/app/evaluation/run.py"]
