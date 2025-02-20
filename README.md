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

---

### 🎯 Successfully Deployed and Running the Web Application!

