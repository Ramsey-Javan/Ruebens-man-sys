#Use official Python base image
FROM python:3.9-slim

#Use working DIR
WORKDIR  /app

#Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application file 
COPY . .

# Expose the port your app runs on (change 5000 if needed)
EXPOSE 5000

# Command to run the application
CMD ["python","website/app.py"]