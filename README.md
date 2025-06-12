# Complete Systemd Service Setup Documentation

## Overview

This documentation covers setting up a Python script (`fetchNplaceData.py`) as a systemd service with timer functionality on Ubuntu Linux. The service will automatically run every 24 hours and can be managed using standard systemd commands.

## Prerequisites

- Ubuntu Linux system with systemd
- Python 3 installed
- PM2 installed and accessible via `/usr/bin/pm2`
- Express backend service named `express-backend` configured in PM2
- Root or sudo access
- Script located at `/root/ohlcDataFetchnStore/fetchNplaceData.py`

## File Structure

```
/etc/systemd/system/
├── fetchnplace.service    # Service definition file
└── fetchnplace.timer      # Timer configuration file

/root/ohlcDataFetchnStore/
├── fetchNplaceData.py     # Main Python script
├── nifty_ohlc_fetcher.py  # Dependency script
└── send_new_data_to_postgre.py  # Dependency script
```

## Service Configuration Files

### 1. Service File (`fetchnplace.service`)

**Location:** `/etc/systemd/system/fetchnplace.service`

```ini
[Unit]
Description=Fetch and Place Data Pipeline
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/ohlcDataFetchnStore
ExecStart=/usr/bin/python3 /root/ohlcDataFetchnStore/fetchNplaceData.py
ExecStartPost=/usr/bin/pm2 restart express-backend
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Configuration Breakdown:**

- **`[Unit]` Section:**
  - `Description`: Human-readable description of the service
  - `After=network.target`: Ensures service starts after network is available

- **`[Service]` Section:**
  - `Type=oneshot`: Service runs once and exits (not a daemon)
  - `User=root`: Runs as root user
  - `WorkingDirectory`: Sets the working directory for script execution
  - `ExecStart`: Command to execute (full path to Python and script)
  - `ExecStartPost`: Command to run after successful completion of ExecStart
  - `StandardOutput=journal`: Redirects stdout to systemd journal
  - `StandardError=journal`: Redirects stderr to systemd journal

- **`[Install]` Section:**
  - `WantedBy=multi-user.target`: Enables service for multi-user runlevel

### 2. Timer File (`fetchnplace.timer`)

**Location:** `/etc/systemd/system/fetchnplace.timer`

```ini
[Unit]
Description=Run Fetch and Place Data Pipeline every 24 hours
Requires=fetchnplace.service

[Timer]
OnUnitActiveSec=24h
Persistent=true
RandomizedDelaySec=0

[Install]
WantedBy=timers.target
```

**Configuration Breakdown:**

- **`[Unit]` Section:**
  - `Description`: Human-readable description of the timer
  - `Requires=fetchnplace.service`: Declares dependency on the service

- **`[Timer]` Section:**
  - `OnUnitActiveSec=24h`: Runs every 24 hours after successful completion
  - `Persistent=true`: Catches up missed runs if system was offline
  - `RandomizedDelaySec=0`: No random delay added to execution time

- **`[Install]` Section:**
  - `WantedBy=timers.target`: Enables timer for systemd timer target

## Setup Commands

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/fetchnplace.service
```

**Purpose:** Opens nano editor to create the service configuration file
**Privilege Required:** sudo (writing to /etc/systemd/system/)
**Alternative Editors:** vim, gedit, or any text editor

### 2. Create Timer File

```bash
sudo nano /etc/systemd/system/fetchnplace.timer
```

**Purpose:** Opens nano editor to create the timer configuration file
**Privilege Required:** sudo (writing to /etc/systemd/system/)

### 3. Reload Systemd Configuration

```bash
sudo systemctl daemon-reload
```

**Purpose:** Reloads systemd manager configuration
**When to Use:** After creating, modifying, or deleting service/timer files
**What it Does:** 
- Scans for new or changed unit files
- Updates systemd's internal configuration
- Does not restart existing services

### 4. Enable Timer Service

```bash
sudo systemctl enable fetchnplace.timer
```

**Purpose:** Enables the timer to start automatically on system boot
**What it Does:**
- Creates symbolic links in appropriate systemd directories
- Adds timer to system startup sequence
- Persists across reboots

### 5. Start Timer Service

```bash
sudo systemctl start fetchnplace.timer
```

**Purpose:** Immediately starts the timer service
**What Happens:**
- Timer becomes active and begins scheduling
- First execution will occur after 24 hours from the first manual run
- Subsequent executions every 24 hours after each completion

## Management Commands

### Service Status and Information

#### Check Timer Status
```bash
sudo systemctl status fetchnplace.timer
```

**Output Information:**
- Active/inactive status
- Last execution time
- Next scheduled execution
- Recent log entries
- Process ID and memory usage

#### List All Timers
```bash
sudo systemctl list-timers
```

**Purpose:** Shows all active timers in the system
**Useful Columns:**
- NEXT: Next execution time
- LEFT: Time remaining until next execution
- LAST: Last execution time
- PASSED: Time since last execution
- UNIT: Timer unit name
- ACTIVATES: Associated service unit

#### Check Specific Timer
```bash
sudo systemctl list-timers fetchnplace.timer
```

**Purpose:** Shows information only for the specified timer

### Manual Service Execution

#### Run Service Immediately
```bash
sudo systemctl start fetchnplace.service
```

**Purpose:** Manually triggers the service without waiting for timer
**Use Cases:**
- Testing the service
- Emergency data fetch
- Troubleshooting

#### Check Service Status
```bash
sudo systemctl status fetchnplace.service
```

**Shows:**
- Service execution status
- Exit code from last run
- Execution time
- Resource usage

### Service Control Commands

#### Stop Timer
```bash
sudo systemctl stop fetchnplace.timer
```

**Purpose:** Stops the timer (prevents future scheduled executions)
**Note:** Does not stop currently running service instances

#### Disable Timer
```bash
sudo systemctl disable fetchnplace.timer
```

**Purpose:** Removes timer from system startup
**What it Does:**
- Removes symbolic links created by enable command
- Timer will not start automatically on boot
- Must be manually started after system restart

#### Restart Timer
```bash
sudo systemctl restart fetchnplace.timer
```

**Purpose:** Stops and starts the timer
**Use Cases:**
- After modifying timer configuration
- Resetting timer schedule
- Troubleshooting timer issues

## Logging and Monitoring

### View Service Logs

#### Real-time Log Following
```bash
sudo journalctl -u fetchnplace.service -f
```

**Purpose:** Shows live log output from the service
**Parameters:**
- `-u`: Specifies unit name
- `-f`: Follows log output (like tail -f)
- `Ctrl+C`: Exits log following

#### View Recent Logs
```bash
sudo journalctl -u fetchnplace.service --since today
```

**Time Filters:**
- `--since today`: Today's logs
- `--since yesterday`: Yesterday's logs
- `--since "2024-01-01"`: Since specific date
- `--since "1 hour ago"`: Last hour's logs

#### View Logs with Line Numbers
```bash
sudo journalctl -u fetchnplace.service -n 50
```

**Purpose:** Shows last 50 log entries
**Parameter:** `-n [number]` specifies number of lines

#### View Timer Logs
```bash
sudo journalctl -u fetchnplace.timer -f
```

**Purpose:** Shows timer-specific log entries
**Shows:**
- Timer start/stop events
- Scheduling information
- Timer activation logs

### Advanced Logging Options

#### View Logs in JSON Format
```bash
sudo journalctl -u fetchnplace.service -o json
```

**Purpose:** Structured log output for parsing or analysis

#### View Logs with Priority
```bash
sudo journalctl -u fetchnplace.service -p err
```

**Priority Levels:**
- `emerg`: System is unusable
- `alert`: Action must be taken immediately
- `crit`: Critical conditions
- `err`: Error conditions
- `warning`: Warning conditions
- `notice`: Normal but significant condition
- `info`: Informational messages
- `debug`: Debug-level messages

## Troubleshooting

### Common Issues and Solutions

#### Service Fails to Start
```bash
# Check service status for error details
sudo systemctl status fetchnplace.service

# View detailed error logs
sudo journalctl -u fetchnplace.service --no-pager

# Verify file permissions
ls -la /root/ohlcDataFetchnStore/fetchNplaceData.py

# Test Python script manually
cd /root/ohlcDataFetchnStore
python3 fetchNplaceData.py
```

#### Timer Not Executing
```bash
# Verify timer is active
sudo systemctl is-active fetchnplace.timer

# Check timer schedule
sudo systemctl list-timers fetchnplace.timer

# Verify timer service file syntax
sudo systemd-analyze verify fetchnplace.timer
```

#### Permission Issues
```bash
# Make script executable
chmod +x /root/ohlcDataFetchnStore/fetchNplaceData.py

# Check file ownership
chown root:root /root/ohlcDataFetchnStore/fetchNplaceData.py
```

### Validation Commands

#### Verify Service File Syntax
```bash
sudo systemd-analyze verify fetchnplace.service
```

#### Verify Timer File Syntax
```bash
sudo systemd-analyze verify fetchnplace.timer
```

#### Check PM2 Path and Service
```bash
which pm2
pm2 list
```

**Expected Output:** 
- PM2 path: `/usr/bin/pm2` or `/usr/local/bin/pm2`
- Should show `express-backend` in the list

#### PM2 Permission Issues
```bash
# If PM2 is installed globally for another user
sudo npm install -g pm2

# Or specify full path in service file
# Replace /usr/bin/pm2 with actual path from 'which pm2'
```

#### Test Script Manually
```bash
cd /root/ohlcDataFetchnStore
/usr/bin/python3 fetchNplaceData.py
```

## Alternative Timer Configurations

### Run at Specific Time Daily
```ini
[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
```

### Run Every 6 Hours
```ini
[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
Persistent=true
```

### Run on Weekdays Only
```ini
[Timer]
OnCalendar=Mon..Fri *-*-* 09:00:00
Persistent=true
```

### Run Every 24 Hours from First Start
```ini
[Timer]
OnUnitActiveSec=24h
Persistent=true
```

## Security Considerations

### Running as Root
- Service runs as root user due to file location in /root/
- Consider moving files to /opt/ or /var/lib/ for better security
- Create dedicated user for service if handling sensitive data

### File Permissions
```bash
# Secure service files
sudo chmod 644 /etc/systemd/system/fetchnplace.service
sudo chmod 644 /etc/systemd/system/fetchnplace.timer

# Secure script files
chmod 750 /root/ohlcDataFetchnStore/fetchNplaceData.py
```

## Maintenance

### Regular Maintenance Tasks

#### Clean Old Logs
```bash
# Clean logs older than 30 days
sudo journalctl --vacuum-time=30d

# Clean logs larger than 100MB
sudo journalctl --vacuum-size=100M
```

#### Update Service Configuration
1. Edit service/timer files
2. Run `sudo systemctl daemon-reload`
3. Restart timer: `sudo systemctl restart fetchnplace.timer`

#### Backup Configuration
```bash
# Backup service files
sudo cp /etc/systemd/system/fetchnplace.* /backup/location/
```

## Complete Setup Script

```bash
#!/bin/bash
# Complete setup script for fetchnplace service

# Create service file
sudo tee /etc/systemd/system/fetchnplace.service > /dev/null <<EOF
[Unit]
Description=Fetch and Place Data Pipeline
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/ohlcDataFetchnStore
ExecStart=/usr/bin/python3 /root/ohlcDataFetchnStore/fetchNplaceData.py
ExecStartPost=/usr/bin/pm2 restart express-backend
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create timer file
sudo tee /etc/systemd/system/fetchnplace.timer > /dev/null <<EOF
[Unit]
Description=Run Fetch and Place Data Pipeline every 24 hours
Requires=fetchnplace.service

[Timer]
OnUnitActiveSec=24h
Persistent=true
RandomizedDelaySec=0

[Install]
WantedBy=timers.target
EOF

# Reload systemd and enable timer
sudo systemctl daemon-reload
sudo systemctl enable fetchnplace.timer
sudo systemctl start fetchnplace.timer

# Run the service once manually to start the 24-hour cycle
sudo systemctl start fetchnplace.service

echo "Service setup complete!"
echo "First run completed manually - next run will be in 24 hours"
echo "Check status with: sudo systemctl status fetchnplace.timer"
echo "View logs with: sudo journalctl -u fetchnplace.service -f"
```

## Summary

This systemd service configuration provides:
- Automatic execution every 24 hours
- Immediate first run (1 minute after timer start)
- Comprehensive logging through systemd journal
- Easy management through standard systemctl commands
- Automatic startup on system boot
- Robust error handling and monitoring capabilities

The service is now ready for production use with full monitoring and management capabilities.