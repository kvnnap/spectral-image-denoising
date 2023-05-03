FROM mcr.microsoft.com/devcontainers/python:0-3.11

ARG USER=vscode
ARG HOME=/home/$USER

USER $USER
WORKDIR $HOME

# https://pylops.github.io/curvelops/installation.html#installation

COPY CurveLab-2.1.3.tar.gz $HOME

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
    && sed -i 's/lexing\/pkge/vscode\/opt/' makefile.opt \
    && make lib

ENV FFTW=$HOME/opt/fftw-2.1.5
ENV FDCT=$HOME/opt/CurveLab-2.1.3
