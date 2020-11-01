FROM continuumio/miniconda3
MAINTAINER Andre Pereira andrespp@gmail.com

# Basic packages
RUN apt-get update && apt-get install -y vim build-essential && cd ~/ && \
 wget https://raw.githubusercontent.com/andrespp/dotfiles/master/.vimrc-basic && \
 mv .vimrc-basic .vimrc

# Timezone and locale settings
RUN rm /etc/localtime && \
    ln -s /usr/share/zoneinfo/America/Belem /etc/localtime && \
    apt-get install -y locales && \
    dpkg-reconfigure -f noninteractive tzdata && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="en_US.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LC_MONETARY=pt_BR.UTF-8

# Aditional packages
RUN apt-get -y install unixodbc-dev python3-psycopg2 libpq-dev

# Setup Conda Environment
ARG CONDA_ENV_NAME=dash-dwbra
COPY ./environment.yml ./
RUN conda env create -f environment.yml
RUN echo "source activate $CONDA_ENV_NAME" > ~/.bashrc
ENV PATH /opt/conda/envs/$CONDA_ENV_NAME/bin:$PATH

# Install app
COPY . .

WORKDIR /usr/src/app

EXPOSE 8050

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
CMD ["help"]
