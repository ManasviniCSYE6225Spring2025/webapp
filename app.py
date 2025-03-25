from flask import Flask, make_response, request, jsonify
from models import db, HealthCheck, FileMetadata   # Ensure you have a HealthCheck model in models.py
from config import Config
from sqlalchemy import create_engine, text
import os
import boto3
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import os, time, json, sys, traceback
import logging
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
from statsd import StatsClient

# Load database credentials from environment variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_name = os.getenv("DB_NAME")

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

logger = logging.getLogger()
# Flask app setup
app = Flask(__name__)

# Structured JSON Logging Setup
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

formatter = CustomJsonFormatter()

# if os.name == 'posix':
#     log_dir = '/var/log/webapp'
#     os.makedirs(log_dir, exist_ok=True)
#     log_file_path = os.path.join(log_dir, 'requests.log')
# else:
#     log_file_path = 'requests.log'

# file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3)
# file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.INFO)

# stdout_handler = logging.StreamHandler(sys.stdout)
# stdout_handler.setFormatter(formatter)
# stdout_handler.setLevel(logging.INFO)

# logger = logging.getLogger()
# logger.addHandler(file_handler)
# logger.addHandler(stdout_handler)
# logger.setLevel(logging.INFO)
# Check if we are running in test mode
IS_TESTING = os.getenv("IS_TESTING") == "1"

if os.name == 'posix' and not IS_TESTING:
    log_dir = '/var/log/webapp'
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'requests.log')
else:
    log_file_path = 'requests.log'

json_log_handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
json_log_handler.setFormatter(formatter)

logger.addHandler(json_log_handler)
logger.setLevel(logging.INFO)

formatter.default_time_format = '%Y-%m-%dT%H:%M:%SZ'

#load_dotenv()

# StatsD client for emitting custom metrics
statsd = StatsClient(host='localhost', port=8125, prefix='webapp')


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
    start_time = time.time()
    statsd.incr('api.healthz.count')
    # Check for a request payload
    if request.data:
        logger.warning("Health check failed: unexpected request body")
        return make_response("", 400)  # Bad Request

    # Check for query parameters
    if request.args:
        logger.warning("Health check failed: unexpected query parameters")
        return make_response("", 400)  # Bad Request

    try:
        # Insert a new health check record
        db_start = time.time()
        health_entry = HealthCheck()
        db.session.add(health_entry)
        db.session.commit()
        statsd.timing('db.healthz.insert', int((time.time() - db_start) * 1000))

        # Return HTTP 200 if successful
        logger.info("Health check passed and recorded to database")
        response = make_response("", 200)
    except Exception:
        # Return HTTP 503 if there is an error
        logger.error("Health check failed:\n%s", traceback.format_exc())
        response = make_response("", 503)
    statsd.timing('api.healthz.time', int((time.time() - start_time) * 1000))
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

    api_start = time.time()
    statsd.incr('api.file_upload.count')

    if 'profilePic' not in request.files:
        logger.warning("File upload failed: No file provided")
        return jsonify({"error": "No file provided"}), 400

    try:
        file = request.files['profilePic']
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        user_id = "default-user"
        s3_key = f"{BUCKET_NAME}/{user_id}/{file_id}_{filename}"

        # S3 Upload Timing
        s3_start = time.time()
        s3.upload_fileobj(file, BUCKET_NAME, s3_key)
        statsd.timing('s3.file_upload.time', int((time.time() - s3_start) * 1000))

        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

        # DB Insert
        db_start = time.time()
        new_file = FileMetadata(id=file_id, filename=filename, s3_key=s3_key, s3_url=s3_url, created_at=datetime.utcnow())
        db.session.add(new_file)
        db.session.commit()
        statsd.timing('db.file_insert.time', int((time.time() - db_start) * 1000))

        logger.info(f"File uploaded: {filename} (ID: {file_id})")
        return jsonify({
            "file_name": filename,
            "id": file_id,
            "url": s3_key,
            "upload_date": new_file.created_at.isoformat()
        }), 201

    except Exception:
        logger.error("File upload failed:\n%s", traceback.format_exc())
        return jsonify({"error": "Upload failed"}), 500

    finally:
        statsd.timing('api.file_upload.time', int((time.time() - api_start) * 1000))
 
#GET
@app.route('/v1/file/<string:file_id>', methods=['GET'])
def get_file_metadata(file_id):

    api_start = time.time()
    statsd.incr('api.file_get.count')
    try:
        db_start = time.time()
        file_entry = FileMetadata.query.get(file_id)
        statsd.timing('db.file_get.time', int((time.time() - db_start) * 1000))

        if not file_entry:
            logger.warning(f"File not found for ID: {file_id}")
            return jsonify({"error": "File not found"}), 404

        logger.info(f"File metadata retrieved for ID: {file_id}")
        return jsonify({
            "file_name": file_entry.filename,
            "id": file_entry.id,
            "url": file_entry.s3_key,
            "upload_date": file_entry.created_at.isoformat()
        }), 200

    except Exception:
        logger.error("Error retrieving file metadata:\n%s", traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

    finally:
        statsd.timing('api.file_get.time', int((time.time() - api_start) * 1000))

#DELETE
@app.route('/v1/file/<string:file_id>', methods=['DELETE'])
def delete_file(file_id):
    api_start = time.time()
    statsd.incr('api.file_delete.count')

    try:
        db_start = time.time()
        file_entry = FileMetadata.query.get(file_id)
        statsd.timing('db.file_lookup.time', int((time.time() - db_start) * 1000))

        if not file_entry:
            logger.warning(f"Delete failed: File not found for ID {file_id}")
            return jsonify({"error": "File not found"}), 404

        # Delete from S3
        s3_start = time.time()
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_entry.s3_key)
        statsd.timing('s3.file_delete.time', int((time.time() - s3_start) * 1000))

        # Delete from DB
        db_start = time.time()
        db.session.delete(file_entry)
        db.session.commit()
        statsd.timing('db.file_delete.time', int((time.time() - db_start) * 1000))

        logger.info(f"File deleted: {file_id}")
        return "", 204

    except Exception:
        logger.error("File deletion failed:\n%s", traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

    finally:
        statsd.timing('api.file_delete.time', int((time.time() - api_start) * 1000))

if __name__ == "__main__":
    create_database()  # Ensure the database exists
    initialize_tables()  # Create tables
    app.run(host ="0.0.0.0",port = 8080,debug=False)