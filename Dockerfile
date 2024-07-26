# syntax=docker/dockerfile:1

FROM python:3.11

# Set the working directory
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create the startup script
RUN echo '#!/bin/sh' > /code/startup.sh && \
  echo 'eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1='\''\2'\''/p")' >> /code/startup.sh && \
  chmod +x /code/startup.sh

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["/bin/sh", "-c", "/code/startup.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
