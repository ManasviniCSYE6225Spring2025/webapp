from flask import Flask, make_response, request, jsonify
from models import db, HealthCheck, FileMetadata   # Ensure you have a HealthCheck model in models.py
from config import Config
from sqlalchemy import create_engine, text
import os
import boto3
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Load database credentials from environment variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_name = os.getenv("DB_NAME")

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Flask app setup
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Function to create the database if it doesn't exist
def create_database():
    # db_name = "cloudApplication"
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db_name}")
    #engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3306/cloud_native_app", pool_recycle=1800,pool_pre_ping=True)

    with engine.connect() as connection:
        existing_databases = connection.execute(text("SHOW DATABASES;"))
        # if db_name not in [row[0] for row in existing_databases]:
        #     connection.execute(text(f"CREATE DATABASE {db_name}"))
        #     print(f"Database {db_name} created successfully!")

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

# S3 Configuration
s3 = boto3.client('s3')
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
 
#POST
@app.route('/v1/file', methods=['POST'])
def upload_file():
    if 'profilePic' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['profilePic']
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())  # Generate a unique file ID
    user_id = "default-user"  # Placeholder, update as needed (e.g., from request)
    s3_key = f"{BUCKET_NAME}/{user_id}/{file_id}_{filename}"

    # Upload file to S3
    s3.upload_fileobj(file, BUCKET_NAME, s3_key)
    s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

    # Save metadata to database
    new_file = FileMetadata(id=file_id,filename=filename, s3_key=s3_key, s3_url=s3_url, created_at=datetime.utcnow())
    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        "file_name": filename,
        "id": file_id,
        "url": s3_key,
        "upload_date": new_file.created_at.isoformat()
    }), 201
 
#GET
@app.route('/v1/file/<string:file_id>', methods=['GET'])
def get_file_metadata(file_id):
    file_entry = FileMetadata.query.get(file_id)
    
    if not file_entry:
        return jsonify({"error": "File not found"}), 404

    return jsonify({
        "file_name": file_entry.filename,
        "id": file_entry.id,
        "url": file_entry.s3_key,
        "upload_date": file_entry.created_at.isoformat()
    }), 200

#DELETE
@app.route('/v1/file/<string:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_entry = FileMetadata.query.get(file_id)
    
    if not file_entry:
        return jsonify({"error": "File not found"}), 404

    # Delete from S3
    s3.delete_object(Bucket=BUCKET_NAME, Key=file_entry.s3_key)

    # Delete metadata from database
    db.session.delete(file_entry)
    db.session.commit()

    return "", 204  # No Content

if __name__ == "__main__":
    create_database()  # Ensure the database exists
    initialize_tables()  # Create tables
    app.run(host ="0.0.0.0",port = 8080,debug=True)
