# syntax=docker/dockerfile:1

FROM python:3.11

# Set the working directory
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY . .

# Copy the startup script
COPY startup.sh /code/startup.sh

# Ensure the startup script is executable
RUN chmod +x /code/startup.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the startup script
CMD ["/code/startup.sh"]
