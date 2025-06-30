# Use official Azure Functions Python image
FROM mcr.microsoft.com/azure-functions/python:4-python310

# Install ODBC driver for SQL Server and build tools
RUN apt-get update && \
    apt-get install -y unixodbc-dev gcc g++ gnupg curl && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy function app code
COPY . /home/site/wwwroot
