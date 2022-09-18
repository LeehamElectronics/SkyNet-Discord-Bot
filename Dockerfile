#Deriving the latest base image
FROM python:3.10.2


#Labels as key value pair
LABEL Maintainer="ldprice"


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/

#to COPY the remote file at working directory in container
COPY ./src ./src


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

COPY requirements.txt requirements.txt

RUN pip3 install -r ./requirements.txt
WORKDIR /usr/app/src/
CMD [ "python", "main.py"]
