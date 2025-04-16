# README - Web Application Setup

## Prerequisites

Before proceeding, ensure you have the following:

- An Ubuntu 24.04 server (AWS EC2 instance)
- Terraform and AWS CLI installed
- SSH access to the server
- Python 3 installed
- MySQL (RDS instance) deployed in AWS

---

## Infrastructure as Code w/Terraform

This project uses Terraform to automate the deployment of AWS infrastructure, including:

- **IAM Roles & Policies**: Ensure the EC2 instance can access S3 and RDS without hardcoded credentials.
- **S3 Bucket**: Private bucket with default encryption and lifecycle policies.
- **RDS Security Group**: Restricts access to the database to only the application security group.
- **RDS Parameter Group**: Custom parameter group for the database instance.
- **EC2 Instance**: Configured with user data to pass database credentials securely.

### **Deploy Infrastructure**

Run the following Terraform commands:

```bash
terraform init
terraform apply -auto-approve
```

To destroy the infrastructure:

```bash
terraform destroy -auto-approve
```

---

## Connecting to the EC2 Instance

To connect to your remote Ubuntu server, use the following command:

```bash
ssh -i ~/path/to/aws-key.pem ec2-user@<ec2-public-ip>
```

Once connected, verify the database hostname is passed in the user data script:

```bash
cat /opt/csye6225/.env
```

Expected Output:

```
DB_HOST='csye6225.xxxxx.rds.amazonaws.com'
DB_USER='csye6225'
DB_PASSWORD='your-db-password'
DB_NAME='csye6225'
S3_BUCKET_NAME='your-s3-bucket-name'
```

---

## Web Application Setup

### **1. Clone the Repository**

```sh
git clone <repository-url>
cd WebApp
```

### **2. Create Virtual Environment**

```sh
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

```sh
pip install -r requirements.txt
```

### **4. Configure ********`.env`******** File**

The application retrieves credentials from an `.env` file. If not set up via Terraform, manually create one:

```sh
touch .env
```

Add the following:

```
DB_USER=csye6225
DB_PASSWORD=your-db-password
DB_NAME=csye6225
DB_HOST=your-rds-endpoint
S3_BUCKET_NAME=your-s3-bucket
```

### **5. Start the Application**

```sh
python3 app.py
```

---

## **API Endpoints**

### **Upload a File**

```sh
curl -X POST "http://<your-ec2-ip>:8080/upload" -F "profilePic=@/path/to/file.jpg"
```

Expected Response:

```json
{
  "file_name": "file.jpg",
  "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "url": "your-s3-bucket-name/path/to/file.jpg",
  "upload_date": "2024-03-19"
}
```

### **Health Check**

```sh
curl -X GET http://<your-ec2-ip>:8080/healthz
```

Expected Response when DB is available:

```
HTTP/1.1 200 OK
```

If RDS is down:

```
HTTP/1.1 503 Service Unavailable
```

---

## **Testing & Troubleshooting**

### **1. Check MySQL Connection from EC2**

```bash
mysql -h <rds-endpoint> -u csye6225 -p
```

Run SQL commands to verify data:

```sql
SHOW DATABASES;
USE csye6225;
SHOW TABLES;
SELECT * FROM files;
```

### **2. Restart Application via Systemd**

The WebApp is configured as a **systemd service**.

```sh
sudo systemctl restart myapp
```

Check status:

```sh
sudo systemctl status myapp
```

### **3. Verify File Upload to S3**

List S3 objects:

```bash
aws s3 ls s3://your-s3-bucket-name/
```

To delete all objects manually:

```bash
aws s3 rm s3://your-s3-bucket-name --recursive
```

---

## **SystemD AutoRun**

Verify that the application starts automatically after an EC2 reboot.

1. **Reboot the instance:**
   ```sh
   sudo reboot
   ```
2. **After reboot, test API:**
   ```sh
   curl -X POST "http://<your-ec2-ip>:8080/upload"
   ```

✅ If the API works, the **systemd service is running correctly.**

---

## **Security Configurations**

- **S3 Bucket** is private and encrypted.
- **IAM Role** attached to EC2 allows access to S3 and RDS.
- **No hardcoded credentials** in code.
- **Application runs as a non-root user.**

---

# CSYE6225 Web Application

## Overview

This is a Python Flask-based web application deployed on EC2. It provides REST APIs for file upload, retrieval, and deletion via AWS S3. The application includes:

- ✅ Structured JSON logging sent to **AWS CloudWatch Logs**
- 📈 Custom **CloudWatch Metrics** for monitoring API usage, database latency, and S3 interactions using **StatsD**

---

## Features

### 🔒 REST APIs

- `GET /healthz` – Health check
- `POST /v1/file` – Upload file
- `GET /v1/file/<file_id>` – Get file metadata
- `DELETE /v1/file/<file_id>` – Delete file

---

## 🔧 Setup Overview

### Prerequisites

- AWS EC2 instance with IAM role having S3 + CloudWatch access
- MySQL database (via AWS RDS)
- StatsD + CloudWatch Agent installed and configured
- CloudWatch Agent config file placed at `/opt/csye6225/cloudwatch-config.json`

---

## 📁 Logging

### 🔹 Log Format

All logs are in **JSON format** using `python-json-logger` with the following fields:

```json
{
  "level": "INFO",
  "time": "2025-03-26 15:32:00",
  "message": "Health check passed and recorded to database"

}


🧱 CI/CD, AMI & Deployment Enhancements
✅ Automated AMI Builds with Packer
A custom AMI is built using Packer, which includes:

Python dependencies pre-installed

CloudWatch Agent pre-configured

Flask app set up in /opt/csye6225

This improves consistency and reduces launch time.

bash
Copy
Edit
packer build -var "aws_region=us-east-1" .
✅ GitHub Actions CI/CD Integration
The pipeline is defined in .github/workflows/packer-build.yml and performs:

Automated test runs with pytest

Integration with MySQL container as service

Secure secrets using secrets.*

AMI creation and packaging:

yaml
Copy
Edit
- name: Build Application Artifact
  run: zip -r webapp.zip .
✅ Launch Template Versioning
A new version of the Launch Template is created automatically using:

bash
Copy
Edit
aws ec2 create-launch-template-version \
  --launch-template-id $LAUNCH_TEMPLATE_ID \
  --source-version 1 \
  --version-description "Updated with new AMI" \
  --launch-template-data "{\"ImageId\":\"$AMI_ID\"}"
Then set as the default:

bash
Copy
Edit
aws ec2 modify-launch-template \
  --launch-template-id $LAUNCH_TEMPLATE_ID \
  --default-version $LATEST_VERSION
✅ Demo Environment Deployment via Cross-Account Access
The new AMI is securely shared with the Demo account:

bash
Copy
Edit
aws ec2 modify-image-attribute --image-id $AMI_ID \
  --launch-permission "Add=[{UserId=$DEMO_ACCOUNT_ID}]"
Also shares the snapshot:

bash
Copy
Edit
aws ec2 modify-snapshot-attribute --snapshot-id $SNAPSHOT_ID \
  --attribute createVolumePermission --operation-type add \
  --user-ids $DEMO_ACCOUNT_ID
✅ Auto Scaling Group Instance Refresh
After updating the Launch Template, an Instance Refresh is triggered:

bash
Copy
Edit
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name "$ASG_NAME" \
  --strategy Rolling
This ensures new EC2 instances are launched using the latest AMI.

✅ User Data Dynamic Configuration
The EC2 user data script retrieves secrets from AWS Secrets Manager:

bash
Copy
Edit
aws secretsmanager get-secret-value --secret-id $INFRA_SECRET_ID
Then writes them to the app environment:

bash
Copy
Edit
echo "DB_HOST='...'" >> /opt/csye6225/.env
✅ No Downtime Deployments
By combining Launch Template versioning and ASG Instance Refresh, deployments happen with:

Zero downtime

Rolling EC2 instance replacements

Minimal manual intervention

✅ This ensures your production environment stays highly available during updates.



## **Submission Instructions**

1. Create a directory named **`firstname_lastname_neuid_05`**.
2. Clone all required repositories:
   ```sh
   git clone <org-repo>
   ```
3. Create a zip file:
   ```sh
   zip -r firstname_lastname_neuid_05.zip firstname_lastname_neuid_05
   ```
4. Unzip to verify:
   ```sh
   unzip firstname_lastname_neuid_05.zip -d /tmp/verify
   ```
5. Upload to Canvas.

✅ **Ensure the latest submission is correct!**

---

## **Conclusion**

This Terraform-deployed WebApp uses AWS services including **EC2, RDS, and S3**, ensuring a **scalable, production-ready cloud-native solution.** 🚀

