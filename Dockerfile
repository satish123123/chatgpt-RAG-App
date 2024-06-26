FROM ubuntu:latest
RUN apt-get update -y  &&  apt-get upgrade -y && apt-get update --fix-missing
RUN apt-get install -y python3.10 python3-pip unixodbc-dev python3-venv
RUN apt-get install -y curl apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
COPY . /app
WORKDIR /app
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
    CMD ["venv/bin/python", "-m", "streamlit", "run", "chat_rag.py", "--server.port", "8080"]