# Python version
FROM python:3.8

# Working Directory
WORKDIR /fcode

# Reuirements
COPY ./requirements.txt  /fcode/requirements.txt

# Install Requirements
RUN pip install --upgrade -r /fcode/requirements.txt
# App code copy
COPY ./fcode  /fcode/

EXPOSE 8000

# Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]