# Initiate Flask application 
from flask import Flask
app = Flask(__name__)

# Load Configuration
app.config.from_pyfile('config.py', silent=True)

# Import routes after app is created
from . import app, route