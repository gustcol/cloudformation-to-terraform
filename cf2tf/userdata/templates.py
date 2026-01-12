"""
User Data Templates for Common VM Configurations

This module provides ready-to-use user data templates for various
EC2 instance configurations and software installations.
"""

from typing import Any, Dict, List, Optional

# Template Categories
CATEGORIES = {
    "base": "Base System Configuration",
    "webserver": "Web Server Installation",
    "container": "Container Runtime",
    "database": "Database Installation",
    "monitoring": "Monitoring & Logging",
    "security": "Security Hardening",
    "devtools": "Development Tools",
    "aws": "AWS Tools & Integration",
}

USERDATA_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # ==========================================================================
    # BASE SYSTEM CONFIGURATION
    # ==========================================================================
    "base-amazon-linux-2": {
        "name": "Amazon Linux 2 Base Setup",
        "description": "Basic setup for Amazon Linux 2 with updates and common packages",
        "category": "base",
        "os": ["amazon-linux-2"],
        "template": '''#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user-data script at $(date)"

# Update system packages
yum update -y

# Install common utilities
yum install -y \
    wget \
    curl \
    vim \
    git \
    htop \
    tree \
    jq \
    unzip \
    tar \
    gzip

# Set timezone
timedatectl set-timezone ${timezone:-UTC}

# Configure hostname
hostnamectl set-hostname ${hostname:-$(curl -s http://169.254.169.254/latest/meta-data/instance-id)}

echo "Base setup completed at $(date)"
''',
        "variables": {
            "timezone": {"default": "UTC", "description": "System timezone"},
            "hostname": {"default": "", "description": "Custom hostname (defaults to instance-id)"},
        },
    },

    "base-ubuntu": {
        "name": "Ubuntu Base Setup",
        "description": "Basic setup for Ubuntu with updates and common packages",
        "category": "base",
        "os": ["ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user-data script at $(date)"

# Wait for cloud-init to complete
cloud-init status --wait

# Update system packages
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y

# Install common utilities
apt-get install -y \
    wget \
    curl \
    vim \
    git \
    htop \
    tree \
    jq \
    unzip \
    tar \
    gzip \
    net-tools \
    software-properties-common

# Set timezone
timedatectl set-timezone ${timezone:-UTC}

# Configure hostname
hostnamectl set-hostname ${hostname:-$(curl -s http://169.254.169.254/latest/meta-data/instance-id)}

echo "Base setup completed at $(date)"
''',
        "variables": {
            "timezone": {"default": "UTC", "description": "System timezone"},
            "hostname": {"default": "", "description": "Custom hostname"},
        },
    },

    # ==========================================================================
    # WEB SERVER TEMPLATES
    # ==========================================================================
    "webserver-nginx": {
        "name": "Nginx Web Server",
        "description": "Install and configure Nginx web server",
        "category": "webserver",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Nginx at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        amazon-linux-extras install nginx1 -y
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y nginx
        ;;
esac

# Configure Nginx
cat > /etc/nginx/conf.d/default.conf << 'NGINX_CONF'
server {
    listen 80;
    listen [::]:80;
    server_name ${server_name:-_};
    root ${document_root:-/var/www/html};
    index index.html index.htm;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        try_files $uri $uri/ =404;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy";
        add_header Content-Type text/plain;
    }
}
NGINX_CONF

# Create document root and sample page
mkdir -p ${document_root:-/var/www/html}
cat > ${document_root:-/var/www/html}/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head><title>Welcome</title></head>
<body>
<h1>Server is running!</h1>
<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
</body>
</html>
HTML

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

echo "Nginx installation completed at $(date)"
''',
        "variables": {
            "server_name": {"default": "_", "description": "Server name for Nginx"},
            "document_root": {"default": "/var/www/html", "description": "Document root path"},
        },
    },

    "webserver-apache": {
        "name": "Apache Web Server",
        "description": "Install and configure Apache HTTP Server",
        "category": "webserver",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Apache at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        yum install -y httpd mod_ssl
        APACHE_SERVICE="httpd"
        APACHE_CONF="/etc/httpd/conf/httpd.conf"
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y apache2
        APACHE_SERVICE="apache2"
        APACHE_CONF="/etc/apache2/apache2.conf"
        a2enmod ssl rewrite headers
        ;;
esac

# Create document root and sample page
mkdir -p ${document_root:-/var/www/html}
cat > ${document_root:-/var/www/html}/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head><title>Welcome</title></head>
<body>
<h1>Apache Server is running!</h1>
<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
</body>
</html>
HTML

# Enable and start Apache
systemctl enable $APACHE_SERVICE
systemctl start $APACHE_SERVICE

echo "Apache installation completed at $(date)"
''',
        "variables": {
            "document_root": {"default": "/var/www/html", "description": "Document root path"},
        },
    },

    # ==========================================================================
    # CONTAINER RUNTIME TEMPLATES
    # ==========================================================================
    "container-docker": {
        "name": "Docker Engine",
        "description": "Install Docker Engine with Docker Compose",
        "category": "container",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Docker at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        # Install Docker on Amazon Linux 2
        amazon-linux-extras install docker -y
        ;;
    ubuntu)
        # Install Docker on Ubuntu
        apt-get update -y
        apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release

        # Add Docker's official GPG key
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

        # Set up repository
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        ;;
esac

# Start and enable Docker
systemctl enable docker
systemctl start docker

# Add ec2-user/ubuntu to docker group
usermod -aG docker ${docker_user:-ec2-user} 2>/dev/null || usermod -aG docker ubuntu 2>/dev/null || true

# Install Docker Compose (standalone)
DOCKER_COMPOSE_VERSION="${docker_compose_version:-v2.24.0}"
curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configure Docker daemon
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'DOCKER_DAEMON'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "${log_max_size:-100m}",
        "max-file": "${log_max_files:-5}"
    },
    "storage-driver": "overlay2",
    "live-restore": true
}
DOCKER_DAEMON

systemctl restart docker

echo "Docker installation completed at $(date)"
docker --version
docker-compose --version
''',
        "variables": {
            "docker_user": {"default": "ec2-user", "description": "User to add to docker group"},
            "docker_compose_version": {"default": "v2.24.0", "description": "Docker Compose version"},
            "log_max_size": {"default": "100m", "description": "Max log file size"},
            "log_max_files": {"default": "5", "description": "Max number of log files"},
        },
    },

    "container-kubernetes-node": {
        "name": "Kubernetes Node (kubeadm)",
        "description": "Prepare node for Kubernetes cluster with kubeadm",
        "category": "container",
        "os": ["ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Preparing Kubernetes node at $(date)"

# Disable swap
swapoff -a
sed -i '/swap/d' /etc/fstab

# Load required kernel modules
cat > /etc/modules-load.d/k8s.conf << EOF
overlay
br_netfilter
EOF

modprobe overlay
modprobe br_netfilter

# Set sysctl params
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sysctl --system

# Install containerd
apt-get update -y
apt-get install -y containerd

mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd

# Install kubeadm, kubelet, kubectl
apt-get install -y apt-transport-https ca-certificates curl gpg

curl -fsSL https://pkgs.k8s.io/core:/stable:/v${k8s_version:-1.29}/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v${k8s_version:-1.29}/deb/ /" | tee /etc/apt/sources.list.d/kubernetes.list

apt-get update -y
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

systemctl enable kubelet

echo "Kubernetes node preparation completed at $(date)"
''',
        "variables": {
            "k8s_version": {"default": "1.29", "description": "Kubernetes version (e.g., 1.29)"},
        },
    },

    # ==========================================================================
    # MONITORING & LOGGING TEMPLATES
    # ==========================================================================
    "monitoring-cloudwatch-agent": {
        "name": "CloudWatch Agent",
        "description": "Install and configure AWS CloudWatch Agent",
        "category": "monitoring",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing CloudWatch Agent at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

# Download and install CloudWatch Agent
case $OS in
    amzn)
        yum install -y amazon-cloudwatch-agent
        ;;
    ubuntu)
        wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
        dpkg -i amazon-cloudwatch-agent.deb
        rm amazon-cloudwatch-agent.deb
        ;;
esac

# Create CloudWatch Agent configuration
mkdir -p /opt/aws/amazon-cloudwatch-agent/etc
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'CW_CONFIG'
{
    "agent": {
        "metrics_collection_interval": ${metrics_interval:-60},
        "run_as_user": "root"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "${log_group_prefix:-/ec2}/messages",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": ${log_retention:-30}
                    },
                    {
                        "file_path": "/var/log/user-data.log",
                        "log_group_name": "${log_group_prefix:-/ec2}/user-data",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": ${log_retention:-30}
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "${metrics_namespace:-CWAgent}",
        "metrics_collected": {
            "cpu": {
                "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
                "metrics_collection_interval": ${metrics_interval:-60},
                "totalcpu": true
            },
            "disk": {
                "measurement": ["used_percent", "inodes_free"],
                "metrics_collection_interval": ${metrics_interval:-60},
                "resources": ["*"]
            },
            "diskio": {
                "measurement": ["io_time", "read_bytes", "write_bytes"],
                "metrics_collection_interval": ${metrics_interval:-60},
                "resources": ["*"]
            },
            "mem": {
                "measurement": ["mem_used_percent"],
                "metrics_collection_interval": ${metrics_interval:-60}
            },
            "netstat": {
                "measurement": ["tcp_established", "tcp_time_wait"],
                "metrics_collection_interval": ${metrics_interval:-60}
            }
        }
    }
}
CW_CONFIG

# Start CloudWatch Agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

echo "CloudWatch Agent installation completed at $(date)"
''',
        "variables": {
            "metrics_interval": {"default": "60", "description": "Metrics collection interval in seconds"},
            "log_group_prefix": {"default": "/ec2", "description": "CloudWatch Log Group prefix"},
            "log_retention": {"default": "30", "description": "Log retention in days"},
            "metrics_namespace": {"default": "CWAgent", "description": "CloudWatch metrics namespace"},
        },
    },

    "monitoring-prometheus-node-exporter": {
        "name": "Prometheus Node Exporter",
        "description": "Install Prometheus Node Exporter for system metrics",
        "category": "monitoring",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Prometheus Node Exporter at $(date)"

NODE_EXPORTER_VERSION="${version:-1.7.0}"

# Create node_exporter user
useradd --no-create-home --shell /bin/false node_exporter || true

# Download and install
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v$NODE_EXPORTER_VERSION/node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
tar xzf node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
cp node_exporter-$NODE_EXPORTER_VERSION.linux-amd64/node_exporter /usr/local/bin/
chown node_exporter:node_exporter /usr/local/bin/node_exporter
rm -rf node_exporter-$NODE_EXPORTER_VERSION.linux-amd64*

# Create systemd service
cat > /etc/systemd/system/node_exporter.service << 'SERVICE'
[Unit]
Description=Prometheus Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --web.listen-address=:${port:-9100} \
    --collector.systemd \
    --collector.processes

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

echo "Node Exporter installation completed at $(date)"
echo "Metrics available at http://localhost:${port:-9100}/metrics"
''',
        "variables": {
            "version": {"default": "1.7.0", "description": "Node Exporter version"},
            "port": {"default": "9100", "description": "Node Exporter port"},
        },
    },

    # ==========================================================================
    # SECURITY HARDENING TEMPLATES
    # ==========================================================================
    "security-hardening-base": {
        "name": "Base Security Hardening",
        "description": "Apply basic security hardening configurations",
        "category": "security",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Applying security hardening at $(date)"

# Kernel security parameters
cat >> /etc/sysctl.conf << 'SYSCTL'
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP broadcast requests
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Block SYN attacks
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = ${disable_ipv6:-0}
net.ipv6.conf.default.disable_ipv6 = ${disable_ipv6:-0}
SYSCTL

sysctl -p

# SSH hardening
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config
sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 300/' /etc/ssh/sshd_config
sed -i 's/#ClientAliveCountMax 3/ClientAliveCountMax 2/' /etc/ssh/sshd_config

# Add SSH banner
echo "Authorized access only. All activity may be monitored and reported." > /etc/ssh/banner
echo "Banner /etc/ssh/banner" >> /etc/ssh/sshd_config

systemctl restart sshd

# Set secure permissions
chmod 700 /root
chmod 600 /etc/ssh/sshd_config

# Disable unused filesystems
cat > /etc/modprobe.d/disable-filesystems.conf << 'DISABLE_FS'
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install udf /bin/true
DISABLE_FS

echo "Security hardening completed at $(date)"
''',
        "variables": {
            "disable_ipv6": {"default": "0", "description": "Set to 1 to disable IPv6"},
        },
    },

    "security-fail2ban": {
        "name": "Fail2Ban Installation",
        "description": "Install and configure Fail2Ban for intrusion prevention",
        "category": "security",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Fail2Ban at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        amazon-linux-extras install epel -y
        yum install -y fail2ban
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y fail2ban
        ;;
esac

# Configure Fail2Ban
cat > /etc/fail2ban/jail.local << 'JAIL_CONF'
[DEFAULT]
bantime = ${bantime:-3600}
findtime = ${findtime:-600}
maxretry = ${maxretry:-5}
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = ${ssh_maxretry:-3}
bantime = ${ssh_bantime:-86400}
JAIL_CONF

systemctl enable fail2ban
systemctl start fail2ban

echo "Fail2Ban installation completed at $(date)"
fail2ban-client status
''',
        "variables": {
            "bantime": {"default": "3600", "description": "Default ban time in seconds"},
            "findtime": {"default": "600", "description": "Time window for counting failures"},
            "maxretry": {"default": "5", "description": "Default max retries before ban"},
            "ssh_maxretry": {"default": "3", "description": "SSH max retries before ban"},
            "ssh_bantime": {"default": "86400", "description": "SSH ban time in seconds (24h)"},
        },
    },

    # ==========================================================================
    # AWS TOOLS & INTEGRATION
    # ==========================================================================
    "aws-cli-v2": {
        "name": "AWS CLI v2",
        "description": "Install AWS CLI version 2",
        "category": "aws",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing AWS CLI v2 at $(date)"

# Remove AWS CLI v1 if present
pip uninstall awscli -y 2>/dev/null || true
yum remove awscli -y 2>/dev/null || true
apt-get remove awscli -y 2>/dev/null || true

# Install AWS CLI v2
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install --update
rm -rf aws awscliv2.zip

# Install Session Manager plugin
case $(cat /etc/os-release | grep ^ID= | cut -d= -f2 | tr -d '"') in
    amzn)
        yum install -y https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm
        ;;
    ubuntu)
        curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
        dpkg -i session-manager-plugin.deb
        rm session-manager-plugin.deb
        ;;
esac

echo "AWS CLI v2 installation completed at $(date)"
aws --version
''',
        "variables": {},
    },

    "aws-ssm-agent": {
        "name": "AWS SSM Agent",
        "description": "Install/update AWS Systems Manager Agent",
        "category": "aws",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Configuring SSM Agent at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        # SSM Agent is pre-installed on Amazon Linux 2
        yum install -y amazon-ssm-agent
        ;;
    ubuntu)
        # Install SSM Agent
        snap install amazon-ssm-agent --classic || true
        systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service || true

        # Alternative: direct installation
        if ! command -v amazon-ssm-agent &> /dev/null; then
            cd /tmp
            wget https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb
            dpkg -i amazon-ssm-agent.deb
            rm amazon-ssm-agent.deb
        fi
        ;;
esac

# Enable and start SSM Agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

echo "SSM Agent configuration completed at $(date)"
systemctl status amazon-ssm-agent --no-pager || true
''',
        "variables": {},
    },

    "aws-efs-mount": {
        "name": "AWS EFS Mount",
        "description": "Install EFS utilities and mount an EFS filesystem",
        "category": "aws",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Configuring EFS mount at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        yum install -y amazon-efs-utils
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y git binutils
        cd /tmp
        git clone https://github.com/aws/efs-utils
        cd efs-utils
        ./build-deb.sh
        apt-get install -y ./build/amazon-efs-utils*deb
        cd /
        rm -rf /tmp/efs-utils
        ;;
esac

# Create mount point
mkdir -p ${mount_point:-/mnt/efs}

# Add to fstab for persistent mount
echo "${efs_id}:/ ${mount_point:-/mnt/efs} efs _netdev,tls,iam 0 0" >> /etc/fstab

# Mount EFS
mount -a -t efs

echo "EFS mount completed at $(date)"
df -h ${mount_point:-/mnt/efs}
''',
        "variables": {
            "efs_id": {"default": "", "description": "EFS filesystem ID (required)", "required": True},
            "mount_point": {"default": "/mnt/efs", "description": "Mount point path"},
        },
    },

    # ==========================================================================
    # DATABASE INSTALLATION
    # ==========================================================================
    "database-mysql": {
        "name": "MySQL Server",
        "description": "Install MySQL/MariaDB server",
        "category": "database",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing MySQL at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        # Install MariaDB on Amazon Linux 2
        yum install -y mariadb-server
        MYSQL_SERVICE="mariadb"
        ;;
    ubuntu)
        # Install MySQL on Ubuntu
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -y
        apt-get install -y mysql-server
        MYSQL_SERVICE="mysql"
        ;;
esac

# Start and enable MySQL
systemctl enable $MYSQL_SERVICE
systemctl start $MYSQL_SERVICE

# Secure installation
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
mysql -e "FLUSH PRIVILEGES;"

# Create application database and user if specified
if [ -n "${db_name}" ]; then
    mysql -e "CREATE DATABASE IF NOT EXISTS ${db_name};"
fi

if [ -n "${db_user}" ] && [ -n "${db_password}" ]; then
    mysql -e "CREATE USER IF NOT EXISTS '${db_user}'@'${db_host:-localhost}' IDENTIFIED BY '${db_password}';"
    if [ -n "${db_name}" ]; then
        mysql -e "GRANT ALL PRIVILEGES ON ${db_name}.* TO '${db_user}'@'${db_host:-localhost}';"
    fi
    mysql -e "FLUSH PRIVILEGES;"
fi

echo "MySQL installation completed at $(date)"
''',
        "variables": {
            "db_name": {"default": "", "description": "Database name to create"},
            "db_user": {"default": "", "description": "Database user to create"},
            "db_password": {"default": "", "description": "Database user password"},
            "db_host": {"default": "localhost", "description": "Host for user access"},
        },
    },

    "database-postgresql": {
        "name": "PostgreSQL Server",
        "description": "Install PostgreSQL server",
        "category": "database",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing PostgreSQL at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        amazon-linux-extras install postgresql${pg_version:-14} -y
        yum install -y postgresql-server postgresql-contrib
        postgresql-setup --initdb
        PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y postgresql postgresql-contrib
        PG_HBA="/etc/postgresql/*/main/pg_hba.conf"
        ;;
esac

# Start and enable PostgreSQL
systemctl enable postgresql
systemctl start postgresql

# Create database and user if specified
if [ -n "${db_name}" ]; then
    sudo -u postgres psql -c "CREATE DATABASE ${db_name};" 2>/dev/null || true
fi

if [ -n "${db_user}" ] && [ -n "${db_password}" ]; then
    sudo -u postgres psql -c "CREATE USER ${db_user} WITH PASSWORD '${db_password}';" 2>/dev/null || true
    if [ -n "${db_name}" ]; then
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO ${db_user};"
    fi
fi

echo "PostgreSQL installation completed at $(date)"
''',
        "variables": {
            "pg_version": {"default": "14", "description": "PostgreSQL version"},
            "db_name": {"default": "", "description": "Database name to create"},
            "db_user": {"default": "", "description": "Database user to create"},
            "db_password": {"default": "", "description": "Database user password"},
        },
    },

    # ==========================================================================
    # DEVELOPMENT TOOLS
    # ==========================================================================
    "devtools-nodejs": {
        "name": "Node.js Runtime",
        "description": "Install Node.js and npm",
        "category": "devtools",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Node.js at $(date)"

NODE_VERSION="${version:-20}"

# Install Node.js using NodeSource
curl -fsSL https://rpm.nodesource.com/setup_$NODE_VERSION.x | bash - 2>/dev/null || \
curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | bash -

# Detect OS and install
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        yum install -y nodejs
        ;;
    ubuntu)
        apt-get install -y nodejs
        ;;
esac

# Install global packages
npm install -g pm2 yarn

echo "Node.js installation completed at $(date)"
node --version
npm --version
''',
        "variables": {
            "version": {"default": "20", "description": "Node.js major version"},
        },
    },

    "devtools-python": {
        "name": "Python Development Environment",
        "description": "Install Python with development tools",
        "category": "devtools",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Python at $(date)"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        amazon-linux-extras install python${python_version:-3.8} -y
        yum install -y python3-pip python3-devel gcc
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y python${python_version:-3} python3-pip python3-venv python3-dev build-essential
        ;;
esac

# Upgrade pip
python3 -m pip install --upgrade pip

# Install common packages
pip3 install \
    virtualenv \
    pipenv \
    poetry \
    black \
    flake8 \
    pytest

echo "Python installation completed at $(date)"
python3 --version
pip3 --version
''',
        "variables": {
            "python_version": {"default": "3", "description": "Python version"},
        },
    },

    "devtools-java": {
        "name": "Java Development Kit",
        "description": "Install OpenJDK and Maven",
        "category": "devtools",
        "os": ["amazon-linux-2", "ubuntu-20.04", "ubuntu-22.04"],
        "template": '''#!/bin/bash
set -e

exec > >(tee /var/log/user-data.log) 2>&1
echo "Installing Java at $(date)"

JAVA_VERSION="${version:-17}"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

case $OS in
    amzn)
        amazon-linux-extras install java-openjdk$JAVA_VERSION -y || \
        yum install -y java-$JAVA_VERSION-amazon-corretto-devel
        yum install -y maven
        ;;
    ubuntu)
        apt-get update -y
        apt-get install -y openjdk-$JAVA_VERSION-jdk maven
        ;;
esac

# Set JAVA_HOME
JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_HOME" >> /etc/profile.d/java.sh
echo "export PATH=\\$PATH:\\$JAVA_HOME/bin" >> /etc/profile.d/java.sh

echo "Java installation completed at $(date)"
java -version
mvn -version
''',
        "variables": {
            "version": {"default": "17", "description": "Java version (11, 17, 21)"},
        },
    },
}


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user data template by ID.

    Args:
        template_id: Template identifier

    Returns:
        Template dictionary or None if not found
    """
    return USERDATA_TEMPLATES.get(template_id)


def list_templates(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List available user data templates.

    Args:
        category: Optional category filter

    Returns:
        List of template summaries
    """
    templates = []
    for tid, template in USERDATA_TEMPLATES.items():
        if category and template.get("category") != category:
            continue
        templates.append({
            "id": tid,
            "name": template["name"],
            "description": template["description"],
            "category": template["category"],
            "os": template.get("os", []),
        })
    return sorted(templates, key=lambda x: (x["category"], x["name"]))


def get_categories() -> Dict[str, str]:
    """Get available template categories."""
    return CATEGORIES.copy()
