FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/tram_times.py .
COPY backend/static static/
CMD ["python", "tram_times.py"]