# VPN Troubleshooting Guide

## Overview
Virtual Private Network (VPN) allows secure remote access to company resources. This guide covers common VPN issues and their solutions.

## Common Symptoms
- Cannot connect to VPN at all
- VPN connects but no access to internal resources
- VPN connection drops frequently
- Slow performance over VPN
- Two-factor authentication fails during VPN login

## Basic Troubleshooting

### Step 1: Check Internet Connection
- Confirm you have a working internet connection
- Try opening a website in your browser
- If on public WiFi, try switching to mobile hotspot

### Step 2: Restart VPN Client
1. Disconnect from VPN completely
2. Close the VPN application (check system tray)
3. Wait 10 seconds
4. Reopen the VPN client
5. Try connecting again

### Step 3: Check Credentials
- Ensure you are using your company email (not personal)
- Check that Caps Lock is off
- Try typing password in a text editor first to verify it works
- If using certificate, ensure it hasn't expired

## Specific Error Messages

### "Connection Failed - Timeout"
1. Check if the VPN server is down (IT will send alerts)
2. Try a different network (mobile hotspot)
3. Disable your firewall temporarily and retry
4. Try connecting to a different VPN gateway (us-east, us-west, eu)

### "Authentication Failed"
1. Verify your username and password
2. Check if your account is locked (call IT Help Desk)
3. If using MFA, ensure your authenticator app is synced
4. Try generating a new MFA code

### "No IP Address Assigned"
1. Disconnect and reconnect to VPN
2. Release and renew your IP address:
   - Open Command Prompt as Administrator
   - Type: `ipconfig /release`
   - Type: `ipconfig /renew`
3. Restart your computer

### "Split Tunneling Not Working"
1. Open VPN client settings
2. Ensure split tunneling is enabled
3. Add the required company domains to the split tunnel list
4. Save settings and reconnect

## Performance Issues

### Slow Connection
1. Check your internet speed (need at least 10 Mbps down, 5 Mbps up)
2. Try connecting to a closer VPN gateway
3. Close unnecessary applications during VPN use
4. Use wired connection instead of WiFi if possible
5. Disable bandwidth-heavy applications (streaming, downloads)

### Frequent Disconnections
1. Check WiFi signal strength (move closer to router)
2. Disable power management for WiFi adapter:
   - Device Manager > Network Adapters > WiFi Adapter > Properties > Power Management
   - Uncheck "Allow the computer to turn off this device to save power"
3. Update VPN client to latest version
4. Check if other devices on the same network have VPN issues

## VPN Client Installation

### Windows
1. Download from https://vpn.company.com/client
2. Run installer as Administrator
3. Follow installation wizard
4. Restart computer after installation
5. Launch VPN client and enter company server address: vpn.company.com

### Mac
1. Download from https://vpn.company.com/client-mac
2. Open the .dmg file and drag to Applications
3. Go to System Preferences > Security & Privacy
4. Allow the VPN system extension
5. Launch VPN client and connect

## When to Escalate
- VPN server is down (check status page first: status.company.com)
- Certificate issues (expired or invalid)
- Need access to specific internal resources not available via VPN
- Performance issues persist after all troubleshooting
- Need VPN access for a new employee (submit access request)

## Related Articles
- VPN Access Request Form
- Remote Work Security Policy
- Two-Factor Authentication Setup
