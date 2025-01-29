from flask import Flask, make_response, request
from models import db, HealthCheck  # Ensure you have a HealthCheck model in models.py
from config import Config
from sqlalchemy import create_engine, text
import os

# Load database credentials from environment variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")

# Flask app setup
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Function to create the database if it doesn't exist
def create_database():
    db_name = "cloudApplication"
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}")
    #engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3306/cloud_native_app", pool_recycle=1800,pool_pre_ping=True)

    with engine.connect() as connection:
        existing_databases = connection.execute(text("SHOW DATABASES;"))
        if db_name not in [row[0] for row in existing_databases]:
            connection.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database {db_name} created successfully!")

# Function to initialize tables
def initialize_tables():
    with app.app_context():  # Ensure app context is active
        db.create_all()  # Create all tables defined in models.py

# Health Check endpoint
@app.route('/healthz', methods=['GET'])
def healthz():
    # Check for a request payload
    if request.data:
        return make_response("", 400)  # Bad Request

    # Check for query parameters
    if request.args:
        return make_response("", 400)  # Bad Request

    try:
        # Insert a new health check record
        health_entry = HealthCheck()
        db.session.add(health_entry)
        db.session.commit()

        # Return HTTP 200 if successful
        response = make_response("", 200)
    except Exception:
        # Return HTTP 503 if there is an error
        response = make_response("", 503)

    # Set cache-control headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
@app.route('/healthz', methods=['POST', 'PUT', 'DELETE', 'PATCH'])
def method_not_allowed():
    return make_response("", 405)  # Method Not Allowed

# Custom error handlers
@app.errorhandler(404)
def not_found(error):
    return "", 404

@app.errorhandler(405)
def method_not_allowed_handler(error):
    return "", 405


if __name__ == "__main__":
    create_database()  # Ensure the database exists
    initialize_tables()  # Create tables
    app.run(debug=True)
