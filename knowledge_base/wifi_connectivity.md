# WiFi Connectivity Troubleshooting Guide

## Overview
This guide covers common WiFi issues and their solutions for company and guest networks.

## Common Symptoms
- Cannot see company WiFi network
- Connected but no internet access
- Very slow WiFi speeds
- Frequent disconnections
- Cannot connect to WiFi after password change
- Guest network not working

## Company WiFi Networks
- **Company-Prod:** Main production network (requires company credentials)
- **Company-Guest:** Guest network (limited access, no internal resources)
- **Company-IoT:** For company devices only (printers, IoT devices)

## Basic Troubleshooting

### Step 1: Check WiFi is Enabled
1. Look for the WiFi icon in the system tray (bottom right)
2. If disabled, click the icon and toggle WiFi ON
3. Or use keyboard shortcut: Fn + F2 (varies by laptop)

### Step 2: Restart WiFi Adapter
1. Open Settings > Network & Internet > WiFi
2. Toggle WiFi OFF
3. Wait 10 seconds
4. Toggle WiFi ON
5. Try connecting again

### Step 3: Restart Computer
- Sometimes a simple restart fixes WiFi issues
- Save your work first, then restart

### Step 4: Forget and Reconnect
1. Settings > Network & Internet > WiFi > Manage known networks
2. Select the company network
3. Click "Forget"
4. Click the WiFi icon in system tray
5. Select the company network
6. Enter your credentials

## Specific Issues

### "Connected, No Internet"
1. Check if other devices have internet (same network)
2. If others work, restart your WiFi adapter
3. If no one works, the network may be down - contact IT
4. Try releasing and renewing IP:
   - Open Command Prompt as Administrator
   - Type: `ipconfig /release`
   - Type: `ipconfig /renew`

### Slow WiFi Speeds
1. Check your distance from the WiFi access point
2. Move closer to an access point if possible
3. Check for interference:
   - Microwaves, cordless phones, and Bluetooth devices can interfere
   - Move away from these devices
4. Switch to 5GHz band if available (faster, shorter range):
   - Look for network name with "_5G" suffix
5. Close bandwidth-heavy applications (streaming, large downloads)

### Frequent Disconnections
1. Update your WiFi driver:
   - Device Manager > Network Adapters > WiFi Adapter
   - Right-click > Update Driver
2. Disable power management for WiFi:
   - Device Manager > Network Adapters > WiFi Adapter > Properties
   - Power Management tab > Uncheck "Allow the computer to turn off this device to save power"
3. Check WiFi signal strength (need at least 2 bars)
4. Move closer to an access point

### Cannot See Company Network
1. Ensure you're in range of a company access point
2. Check if other devices can see the network
3. Try refreshing the network list:
   - Click WiFi icon
   - Click "Refresh" or toggle WiFi off/on
4. If no one can see it, the access point may be down

### Authentication Issues After Password Change
1. Forget the network (as described in Basic Troubleshooting)
2. Reconnect with your new password
3. If using certificate-based auth, ensure your certificate is renewed

## Guest Network

### Connecting to Guest Network
1. Select "Company-Guest" from WiFi list
2. Open a browser
3. Accept the terms and conditions
4. Enter your name and email
5. You'll receive a temporary access code
6. Enter the code to connect

### Guest Network Limitations
- No access to internal company resources
- Internet access only
- Limited bandwidth
- Session expires after 8 hours
- No printing to company printers

## WiFi Settings Optimization

### Windows WiFi Settings
1. Settings > Network & Internet > WiFi
2. Ensure "Connect automatically" is checked for company network
3. Set "Network profile" to "Private" for company network

### Mac WiFi Settings
1. System Preferences > Network
2. Select WiFi > Advanced
3. Drag "Company-Prod" to the top of the preferred networks list
4. Ensure "Auto-join" is checked

## Advanced Troubleshooting

### Network Reset (Windows)
1. Settings > Network & Internet > Status
2. Click "Network reset"
3. Click "Reset now"
4. Computer will restart
5. Reconnect to WiFi

### Check WiFi Signal Strength
1. Click the WiFi icon in system tray
2. Look at the signal bars for each network
3. Need at least 2 bars for reliable connection
4. If weak, move closer to an access point

## When to Escalate
- Cannot connect after all troubleshooting steps
- Need access to special WiFi networks
- WiFi hardware issues (adapter not detected)
- Need guest network access for extended period
- Performance issues in specific building locations
- Need WiFi for new employee on first day

## Related Articles
- WiFi Access Request Form
- Network Security Policy
- Guest Network Policy
- Remote Work WiFi Setup
