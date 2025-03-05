# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

ARG TRAINSIM_SUPABASE_URL
ARG TRAINSIM_SUPABASE_KEY

ENV TRAINSIM_SUPABASE_URL=$TRAINSIM_SUPABASE_URL
ENV TRAINSIM_SUPABASE_KEY=$TRAINSIM_SUPABASE_KEY

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 7000

# Define environment variable (optional, but good practice - you can override these later)
ENV PYTHONPATH=/app

# Run uvicorn when the container launches
#CMD ["uvicorn", "app.main:app", "--port", "7000"]

COPY run.sh /usr/src/fastapi/

CMD sh run.sh