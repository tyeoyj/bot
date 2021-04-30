# Each line represents a new layer which is cached: image is re-built faster: 
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/  

# STEP 1: download base image
FROM continuumio/miniconda3:latest

# STEP 2: set project folder
WORKDIR /project

# STEP 3: create conda environment
# Why copy just the environment.yml and not all files (see below COPY . .)
# Docker caches environment.yml, subsequent command to download packages depends on this line
# If the whole folder is copied at this step, any changes in the whole folder will cause the package download
# to NOT use the cached packages, resulting in a long image rebuild time     
COPY ./requirements.txt /project

#adds conda-forge channel to defaults
RUN conda config --append channels conda-forge
RUN conda install --file requirements.txt -q -y

#setting environment variable
ENV MODE="prod"

# STEP 4: copy entire folder to project folder
COPY . .

ENTRYPOINT ["python", "bot.py"]


# STEP 6: build image and run app from docker command line
# docker image build -t first_flask_app .
# docker run -p 5000:5000 -d first_flask_app