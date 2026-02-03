# Use official Python image
FROM python:3.13

# Create base directory
RUN mkdir /app

# Set base workdir
WORKDIR /app

# Python settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (better caching)
COPY requirements.txt .

# Install deps
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary

# Copy project
COPY . .

# move working dir to Django root
WORKDIR /app/Task1

# Expose port
EXPOSE 8001

# Start server
CMD ["uvicorn", "Task1.asgi:application", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]
