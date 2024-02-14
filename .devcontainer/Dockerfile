FROM mcr.microsoft.com/devcontainers/python:0-3.11

ARG USER=vscode
ARG HOME=/home/$USER

# Install OpenEXR deps - libxtst6 libxt6 are for Matlab runtime
RUN apt-get update \
 && apt-get -y --no-install-recommends install libopenexr-dev libxtst6 libxt6 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

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

COPY installer_input.txt $HOME
RUN    cd $HOME \
    && mkdir matlab MR \
    && mv installer_input.txt matlab/ \
    && cd matlab \
    && wget -nv https://ssd.mathworks.com/supportfiles/downloads/R2023b/Release/6/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2023b_Update_6_glnxa64.zip \
    && unzip -qq MATLAB_Runtime_R2023b_Update_6_glnxa64.zip \
    && rm MATLAB_Runtime_R2023b_Update_6_glnxa64.zip \
    && ./install -inputFile installer_input.txt -destinationFolder $HOME/MR \
    && cd $HOME \
    && rm -rf matlab

ENV LD_LIBRARY_PATH=$HOME/MR/R2023b/runtime/glnxa64:$HOME/MR/R2023b/bin/glnxa64:$HOME/MR/R2023b/sys/os/glnxa64:$HOME/MR/R2023b/sys/opengl/lib/glnxa64
ENV XAPPLRESDIR=$HOME/MR/R2023b/X11/app-defaults

#This is the hdrpy package I generated from Matlab Online
COPY hdrpy.zip $HOME
RUN cd $HOME \
    && unzip -qq hdrpy.zip \
    && cd hdrpy \
    && python3 setup.py install --user \
    && cd $HOME \
    && rm -rf hdrpy  hdrpy.zip
