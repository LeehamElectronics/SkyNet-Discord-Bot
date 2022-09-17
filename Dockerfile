#Deriving the latest base image
FROM python:latest


#Labels as key value pair
LABEL Maintainer="ldprice"


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY ./src ./
COPY ./media ./


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

COPY ./config.yml ./conf/config.yml

RUN pip3 install ./requirements.txt
CMD [ "python", "./src/main.py"]
