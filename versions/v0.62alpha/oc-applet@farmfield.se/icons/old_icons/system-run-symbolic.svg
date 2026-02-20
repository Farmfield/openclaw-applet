#!/bin/bash

# 1. Define variables
USER_HOME="/home/johnny"
OC_DIR="$USER_HOME/.openclaw"
BACKUP_ROOT="$USER_HOME/Documents/oc_backup"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/openclaw_bak_$BACKUP_DATE"

echo "--- Starting OpenClaw Maintenance ---"

# 2. Stop the gateway to prevent file locking
echo "Stopping OpenClaw Gateway..."
openclaw gateway stop

# 3. Create backup root if it doesn't exist and backup current directory
if [ -d "$OC_DIR" ]; then
    mkdir -p "$BACKUP_ROOT"
    echo "Archiving current configuration to $BACKUP_DIR..."
    cp -r "$OC_DIR" "$BACKUP_DIR"
else
    echo "Warning: ~/.openclaw directory not found. Skipping backup."
fi

# 4. Update OpenClaw to the latest version
echo "Updating OpenClaw CLI..."
npm install -g openclaw@latest

# 5. Run the doctor fix to repair memory/context pipes
echo "Running diagnostics and memory fixes..."
openclaw doctor --fix

# 6. Restart the gateway
echo "Restarting OpenClaw Gateway..."
openclaw gateway restart

# 7. Verification Test
echo "Running Sync Test to verify disk-write capabilities..."
# In v2026.2.15, 'exec' was renamed to 'run'
openclaw run "echo 'Sync Test - $BACKUP_DATE' >> ~/.openclaw/workspace/memory/sync_check.md"

echo "--- Maintenance Complete ---"
openclaw --version


