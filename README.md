# README - Web Application Setup

## Prerequisites
Before proceeding, ensure you have the following:
- An Ubuntu server (DigitalOcean droplet or equivalent)
- SSH access to the server
- Python 3 installed
- MySQL installed

---

## Connecting to the Droplet
To connect to your remote Ubuntu server, use the following command:
```bash
ssh -i ~/.ssh/doo root@69.55.54.138
```
Once connected, open another terminal window on your local machine and send your zip file and setup script to the server:
```bash
scp -i ~/.ssh/doo /Users/manasvini/webapp-main root@69.55.54.138:
```

---

## Running the Setup Script
Once the files are uploaded, navigate to your server terminal and run the setup script:
```bash
bash setup_app.sh
```

To open and modify the setup file if necessary:
```bash
nano setup_app.sh
```

---

## Setting up the Virtual Environment
Create a Python virtual environment:
```bash
python3 -m venv menv
```
Activate the virtual environment:
```bash
source menv/bin/activate
```

---

## Checking Dependencies
Ensure MySQL and Python 3 are installed:
```bash
mysql --version
python3 --version
```
If required, install dependencies manually:
```bash
pip3 install -r requirements.txt
```

---

## Creating the .env File
Inside the project directory, create a `.env` file:
```bash
nano .env
```
Add the following database configuration:
```ini
DB_USER='root'
DB_PASSWORD='manasvini'
DB_NAME='cloudApplication'
DB_HOST='localhost'
```
Save and exit (`CTRL+X`, then `Y` and `Enter`).

---

## Starting the Application
After setting up the environment, run the application:
```bash
python3 app.py
```

---

## Database Connection
Start MySQL service if not already running:
```bash
sudo systemctl start mysql
```

Connect to MySQL:
```bash
mysql -u root -p
```
Check the database:
```sql
SHOW DATABASES;
USE cloudApplication;
SHOW TABLES;
```

---

## Running Tests with Pytest
Navigate to the test cases directory:
```bash
cd tests/healthcheck_test
```
Run Pytest within the virtual environment:
```bash
pytest tests/healthcheck_test
```
Ensure all test cases pass.

---

## Additional Notes
- Ensure the MySQL server is running before attempting database operations.
- Use `source menv/bin/activate` every time you work inside the virtual environment.
- If facing dependency issues, reinstall the packages:
  ```bash
  pip3 install -r requirements.txt
  ```
- If required, restart MySQL:
  ```bash
  sudo systemctl restart mysql
  ```

# WebApp Deployment (Assignment 4)

## 📌 Table of Contents
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [WebApp Setup](#webapp-setup)
- [API Endpoints](#api-endpoints)
- [Systemd Service Management](#systemd-service-management)
- [Testing & Troubleshooting](#testing-troubleshooting)

---

## **Project Overview**
This is a **Flask-based WebApp** that interacts with a MySQL database and includes **automated deployment and health checks**. The application runs as a **systemd service** to ensure high availability and restarts automatically if it crashes.

### ✅ **Key Features:**
- **Modular Flask application** with Blueprints.
- **MySQL database integration** via SQLAlchemy.
- **Secure credential handling** using `.env` files.
- **Automated deployment** with a setup script.
- **Systemd service** for persistent execution.

---

## **Prerequisites**
- Python 3.7 or higher
- MySQL database
- Pip for managing Python packages
- Ubuntu 24.04 server (AWS/GCP instance)

---

## **Installation**
### **Steps to Run Locally**
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd WebApp
   ```
2. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up `.env` file:
   ```sh
   touch .env
   ```
   Add your database credentials:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```
5. Run the WebApp:
   ```sh
   python run.py
   ```
6. Test the application:
   ```sh
   curl -X GET http://127.0.0.1:8080/healthz
   ```

---

## **WebApp Setup on Server**
### **Automated Deployment Using `setup_webapp.sh`**
This script performs the following actions:
- Installs **MySQL, Python, pip, nginx**.
- Sets up MySQL authentication & creates a database.
- Extracts WebApp files & sets up a virtual environment.
- Moves `.env` securely & installs dependencies.
- Configures **systemd service for WebApp**.

### **Deployment Steps**
1. Copy `setup_webapp.sh` & `Webapp.zip` to the server:
   ```sh
   scp setup_webapp.sh Webapp.zip user@server-ip:/tmp/
   ```
2. SSH into the server:
   ```sh
   ssh user@server-ip
   ```
3. Run the setup script:
   ```sh
   sudo bash /tmp/setup_webapp.sh
   ```
4. Verify systemd service status:
   ```sh
   sudo systemctl status myapp
   ```

---

## **API Endpoints**
### **GET /healthz**
- **Description**: Performs a health check by interacting with the database.
- **Response**:
  - `200 OK`: Database is healthy.
  - `503 Service Unavailable`: Database connection failed.
- **Headers**:
  - `Cache-Control`: `no-cache, no-store, must-revalidate`
  - `X-Content-Type-Options`: `nosniff`

---

## **Systemd Service Management**
The WebApp runs as a **systemd service**, ensuring automatic startup and crash recovery.

### **Useful Commands:**
- Start the service:
  ```sh
  sudo systemctl start myapp
  ```
- Restart the service:
  ```sh
  sudo systemctl restart myapp
  ```
- Check logs:
  ```sh
  journalctl -u myapp --no-pager | tail -50
  ```

---

## **Testing & Troubleshooting**
### **Health Check API (`/healthz`)**
- Test via `curl`:
  ```sh
  curl -X GET http://<server-ip>:8080/healthz
  ```

### **Troubleshooting Common Issues**
**1. MySQL Connection Issues**
   - Ensure MySQL is running:
     ```sh
     sudo systemctl status mysql
     ```
   - Verify credentials in `.env`.

**2. WebApp Not Running**
   - Restart the systemd service:
     ```sh
     sudo systemctl restart myapp
     ```
   - Check logs:
     ```sh
     journalctl -u myapp --no-pager | tail -50
     ```

---

## **🚀 Conclusion**
This WebApp setup ensures a **scalable, production-ready Flask application** with **automated deployment** and **systemd service management**. 🎯

---

### 🎯 Successfully Deployed and Running the Web Application!

