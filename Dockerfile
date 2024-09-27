# Pulling the python image from docker hub
FROM python:3.9-slim 

# Setting the working directory in the container
WORKDIR /usr/ds5760

# Copying the requirements file to the working directory and installing the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

