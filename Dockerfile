FROM python:3.10-slim

# Install PostgreSQL client (contains pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-db.sh .

RUN chmod +x wait-for-db.sh

EXPOSE 5000

CMD ["./wait-for-db.sh"]
