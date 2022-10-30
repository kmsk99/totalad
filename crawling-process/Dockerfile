# set base image (host OS)
FROM python:3.8-slim

# set the working directory in the container

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
# COPY app/ .

# EXPOSE 5000

# # command to run on container start
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]