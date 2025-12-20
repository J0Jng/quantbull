FROM python:3.12-slim

WORKDIR /app

# Install minimal dependencies (uvicorn + fastapi). Use root requirements if available.
COPY ../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || pip install --no-cache-dir fastapi uvicorn[standard]

# Copy task_service package
COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "task_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
