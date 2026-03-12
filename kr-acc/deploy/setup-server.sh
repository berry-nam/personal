#!/usr/bin/env bash
# Server setup script for kr-acc deployment on a fresh Ubuntu 22.04+ EC2 instance.
#
# Usage:
#   ssh ubuntu@your-ec2-ip 'bash -s' < deploy/setup-server.sh
#
# After running, configure .env and deploy with:
#   cd /opt/kr-acc && cp .env.example .env && nano .env
#   make deploy

set -euo pipefail

echo "=== kr-acc server setup ==="

# Update system
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Install Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    sudo systemctl enable docker
    echo "Docker installed. You may need to re-login for group changes."
fi

# Install Docker Compose plugin (v2)
if ! docker compose version &>/dev/null; then
    echo "Installing Docker Compose plugin..."
    sudo apt-get install -y -qq docker-compose-plugin
fi

# Install git
sudo apt-get install -y -qq git make

# Create app directory
sudo mkdir -p /opt/kr-acc
sudo chown "$USER:$USER" /opt/kr-acc

# Clone repository (if not already cloned)
if [ ! -d /opt/kr-acc/.git ]; then
    echo "Cloning kr-acc repository..."
    git clone https://github.com/berry-nam/kr-acc.git /opt/kr-acc
fi

# Set up swap (2GB — useful for t3.micro/small)
if [ ! -f /swapfile ]; then
    echo "Setting up 2GB swap..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Set up automatic security updates
sudo apt-get install -y -qq unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. cd /opt/kr-acc"
echo "  2. cp .env.example .env && nano .env"
echo "  3. Set ASSEMBLY_API_KEY, DB_PASSWORD, DOMAIN"
echo "  4. make deploy"
echo ""
echo "For HTTPS, point your domain's DNS to this server's IP first."
