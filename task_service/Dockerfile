FROM python:3.12-slim

WORKDIR /app

# Install minimal dependencies (uvicorn + fastapi). Use package-local requirements.txt
# (use the requirements inside the task_service context)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || pip install --no-cache-dir fastapi uvicorn[standard]

# Copy package files into /app/task_service so that importing `task_service` works
COPY . /app/task_service

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "task_service.main:app", "--host", "0.0.0.0", "--port", "9000"]
