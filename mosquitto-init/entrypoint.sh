#!/bin/sh

set -e

PASSWD_FILE="/mosquitto/config/passwd"
ACL_FILE="/mosquitto/config/mosquitto.acl"

echo "Creating Mosquitto password file..."
if [ ! -f "$PASSWD_FILE" ]; then
    mosquitto_passwd -c -b "$PASSWD_FILE" testclient testpassword
fi

echo "Creating Mosquitto ACL file..."
if [ ! -f "$ACL_FILE" ]; then
    echo "user testclient" > "$ACL_FILE"
    echo "topic readwrite #" >> "$ACL_FILE"
fi

chmod 644 /mosquitto/config/passwd
chmod 644 /mosquitto/config/mosquitto.acl

# Wait for both files to exist
while [ ! -f "$PASSWD_FILE" ] || [ ! -f "$ACL_FILE" ]; do
  echo "Waiting for config files to be ready..."
  sleep 1
done

echo "✅Password and ACL setup complete. Starting Mosquitto..."
sleep 1
exec mosquitto -c /mosquitto/config/mosquitto.conf
