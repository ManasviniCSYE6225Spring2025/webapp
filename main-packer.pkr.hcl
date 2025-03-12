packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = ">= 1.2.8"
    }
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = ">= 1"
    }
  }
}

# Variables
variable "aws_region" {
  default = "us-east-1"
}

variable "gcp_project_id" {
  default = "csye6225-dev-451700"
}

variable "gcp_zone" {
  default = "us-east1-b"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "disk_size" {
  default = 25
}

variable "gcp_machine_type" {
  default = "e2-medium"
}

variable "aws_ami" {
  default = "ami-04b4f1a9cf54c11d0"
}

variable "gcp_source_image" {
  default = "ubuntu-2404-lts-amd64"
}

variable "network" {
  default = "default"
}

variable "ssh_username" {
  default = "ubuntu"
}

variable "gcp_ssh_username" {
  default = "ubuntu"
}


#AWS AMI Source Configuration (Commented Out)
source "amazon-ebs" "aws_image" {
  ami_name      = "csye6225-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  instance_type = var.instance_type
  region        = var.aws_region
  source_ami    = var.aws_ami
  ssh_username  = var.ssh_username
  profile       = "dev"
}

# GCP Machine Image Source Configuration
source "googlecompute" "gcp_image" {
  project_id            = var.gcp_project_id
  source_image_family   = "ubuntu-2404-lts-amd64"
  image_name            = "csye6225-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  zone                  = var.gcp_zone
  disk_size             = var.disk_size
  network               = var.network
  communicator          = "ssh"
  ssh_username          = var.gcp_ssh_username
  service_account_email = "githubactions@csye6225-dev-451700.iam.gserviceaccount.com"
  tags                  = ["default-allow-ssh"]
}

build {
  sources = ["source.amazon-ebs.aws_image", "source.googlecompute.gcp_image"]

  provisioner "file" {
    source      = "webapp.zip"
    destination = "/tmp/webapp.zip"
  }


  provisioner "file" {
    source      = "myapp.service"
    destination = "/tmp/myapp.service"
  }

  # Copy setup script to the instance
  provisioner "file" {
    source      = "scripts/setupapp.sh"
    destination = "/tmp/setupapp.sh"
  }

  # Run the setup script
  provisioner "shell" {
    inline = [
      "chmod +x /tmp/setupapp.sh",
      "sudo /tmp/setupapp.sh"
    ]
  }

  # Post-processing (manifest output)
  post-processor "manifest" {
    output = "image_manifest.json"
  }

}
