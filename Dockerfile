FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY start_server.py .

EXPOSE 6088

CMD ["python", "start_server.py"]