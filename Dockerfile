FROM python:3.11-bullseye as builder

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

COPY --chown=$USER:$USER .devcontainer/CurveLab-2.1.3.tar.gz $HOME

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

COPY --chown=$USER:$USER .devcontainer/installer_input.txt $HOME
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

#This is the hdrpy package I generated from Matlab Online
COPY --chown=$USER:$USER .devcontainer/hdrpy.zip $HOME
RUN cd $HOME \
    && unzip -qq hdrpy.zip \
    && cd hdrpy \
    && python3 setup.py install --user \
    && cd $HOME \
    && rm -rf hdrpy  hdrpy.zip

COPY --chown=$USER:$USER requirements.txt .
ENV FFTW=$HOME/opt/fftw-2.1.5 FDCT=$HOME/opt/CurveLab-2.1.3
RUN pip3 install --no-compile -r requirements.txt \
 && pip3 install --no-compile torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

FROM python:3.11-slim-bullseye
ARG USER=kevin
ARG HOME=/home/$USER
RUN useradd -ms /bin/bash $USER \
    && mkdir -p /app/data \
    && chown -R $USER:$USER /app
# Install OpenEXR deps - not sure if can put everything with --no-install-recommends
RUN apt-get update \
 && apt-get -y install libopenexr25 tk \
 && apt-get -y --no-install-recommends install libxtst6 libxt6 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
USER $USER
WORKDIR /app/data
COPY --chown=$USER:$USER --from=builder $HOME/opt $HOME/opt
COPY --chown=$USER:$USER --from=builder $HOME/MR $HOME/MR
COPY --chown=$USER:$USER --from=builder $HOME/.local $HOME/.local
COPY --chown=$USER:$USER core /app/core
COPY --chown=$USER:$USER flip /app/flip
COPY --chown=$USER:$USER flip_torch /app/flip_torch
COPY --chown=$USER:$USER evaluation /app/evaluation
COPY --chown=$USER:$USER visualisation /app/visualisation
COPY --chown=$USER:$USER utils /app/utils
COPY --chown=$USER:$USER tools /app/tools
COPY --chown=$USER:$USER version.py /app
ENV FFTW=$HOME/opt/fftw-2.1.5 FDCT=$HOME/opt/CurveLab-2.1.3
ENV XAPPLRESDIR=$HOME/MR/R2023b/X11/app-defaults LD_LIBRARY_PATH=$HOME/MR/R2023b/runtime/glnxa64:$HOME/MR/R2023b/bin/glnxa64:$HOME/MR/R2023b/sys/os/glnxa64:$HOME/MR/R2023b/sys/opengl/lib/glnxa64
ENTRYPOINT ["python3", "-Xfrozen_modules=off", "/app/evaluation/run.py"]
