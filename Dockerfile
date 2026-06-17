# Use official lightweight Python image.
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set working directory in container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install system dependencies if any are needed (none for now)
# COPY requirements first to leverage Docker cache
COPY F.WebApp/requirements.txt ./F.WebApp/requirements.txt
RUN pip install --no-cache-dir -r ./F.WebApp/requirements.txt

# Copy all code/folders from workspace into container
COPY . ./

# Set PYTHONPATH to include key directories
ENV PYTHONPATH="${PYTHONPATH}:${APP_HOME}:${APP_HOME}/C. System Flow:${APP_HOME}/D. Model"

# Expose port (Cloud Run sets PORT env variable)
ENV PORT 8080

# Run the web service using Gunicorn.
# We run from F.WebApp subdirectory using --chdir.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --chdir F.WebApp app_integrated:app
