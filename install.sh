#!/bin/bash

# Exit on error
set -e

echo "Starting BLOCK NODES Bot Install..."

# Check for root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo bash install.sh)"
  exit 1
fi

echo "1. Installation System Updates..."
apt update

echo "2. Installing Dependencies..."
# Try to install LXD (the modern container manager)
# Check if snap is available
if command -v snap &> /dev/null; then
    echo "Installing LXD via Snap..."
    snap install lxd || echo "Snap install failed, trying apt..."
elif command -v apt &> /dev/null; then
    echo "Installing LXD via APT..."
    apt install -y lxd || echo "APT install failed."
fi

# Install legacy LXC tools just in case, and pip
apt install -y python3-pip lxc-utils || apt install -y python3-pip lxc

echo "3. Initializing LXD (required)..."
# Try to auto-init lxd if installed
if command -v lxd &> /dev/null; then
    lxd init --auto || echo "LXD init failed (already initialized?)"
else
    echo "WARNING: LXD command not found. You may need to install 'lxd' manually."
fi

echo "4. Installing Python Libs..."
pip3 install discord.py python-dotenv

echo "5. Setup Service..."
# Check if systemd exists
if pidof systemd &> /dev/null; then
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/blocknodes.service"

    cat <<EOF > $SERVICE_FILE
[Unit]
Description=BLOCK NODES Discord Bot (LXD)
After=network.target

[Service]
User=root
WorkingDirectory=$CURRENT_DIR
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 $CURRENT_DIR/lxc-bot-v1.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable blocknodes
    systemctl restart blocknodes
    echo "Service started!"
else
    echo "Systemd not detected (are you in a container?)."
    echo "Skipping service creation."
fi

echo "-----------------------------------"
echo "Done!"
echo "If systemd failed, run manually:"
echo "sudo python3 lxc-bot-v1.py"
echo "-----------------------------------"
