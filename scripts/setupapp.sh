#!/bin/bash

# Variables (Modify as needed)
DB_TYPE="mysql"   # Change to "postgresql" or "mariadb" if needed
DB_NAME="cloudApplication"
DB_USER="root"
DB_PASS="manasvini"  # Set root password for MySQL
APP_DIR="/opt/csye6225"

# Ensure script runs as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Function to check if a package is installed
check_package() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 installation failed or is not available. Exiting."
        exit 1
    else
        echo "$1 is installed successfully."
    fi
}

# Update and upgrade system packages
echo "Updating system packages..."
apt update -y && apt upgrade -y

# Install required packages
echo "Installing required packages..."
export DEBIAN_FRONTEND=noninteractive  # Suppress password prompt
apt install -y mysql-server python3 python3-pip python3-venv unzip pkg-config libmysqlclient-dev

# Check if installations were successful
check_package "mysql"
check_package "python3"
check_package "pip3"
check_package "unzip"

# Start and enable MySQL
systemctl enable mysql && systemctl start mysql

# Secure MySQL root user and allow password authentication
echo "Configuring MySQL root user..."
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_PASS';"
mysql -u root -e "FLUSH PRIVILEGES;"

# Create the database
echo "Creating database: $DB_NAME..."
mysql -u root -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"

# Setup application directory (running as root)
echo "Setting up application directory: $APP_DIR..."
mkdir -p $APP_DIR
chown -R root:root $APP_DIR
chmod -R 755 $APP_DIR

# Extract application files
echo "Extracting application files..."
if [ -f "webapp-main.zip" ]; then
    unzip -o webapp-main.zip -d "$APP_DIR"
    chown -R root:root "$APP_DIR"
    chmod -R 755 "$APP_DIR"
else
    echo "Warning: Application ZIP file not found! Skipping extraction."
fi

# Change to extracted directory (handling possible variations in folder name)
cd "$APP_DIR"/webapp-main* || { echo "Error: Webapp folder not found"; exit 1; }

# Setup virtual environment
echo "Setting up virtual environment..."
python3 -m venv menv
source menv/bin/activate || { echo "Error: Virtual environment activation failed"; exit 1; }

# Install dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Setup completed successfully!"