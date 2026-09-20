# Printer Setup and Troubleshooting Guide

## Overview
This guide covers printer installation, common printing issues, and their solutions for network and local printers.

## Common Symptoms
- Printer not found or not listed
- Documents stuck in print queue
- Poor print quality (streaks, fading, smudges)
- Paper jams
- Wrong paper size or tray selected
- Printer offline status

## Adding a New Printer

### Step 1: Find Available Printers
1. Open Settings > Devices > Printers & Scanners
2. Click "Add a printer or scanner"
3. Wait for Windows to search for available printers
4. Select your printer from the list

### Step 2: If Printer Not Listed
1. Click "The printer that I want isn't listed"
2. Select "Add a printer using a TCP/IP address or hostname"
3. Enter the printer IP address (found on the printer's display or from IT)
4. Click Next and follow the installation wizard

### Step 3: Install Printer Drivers
1. Windows will automatically install basic drivers
2. For full features, download drivers from the manufacturer's website:
   - HP: https://support.hp.com/drivers
   - Canon: https://www.usa.canon.com/support
   - Brother: https://www.brother-usa.com/support
3. Run the installer and follow the prompts

## Common Printing Issues

### Printer Shows "Offline"
1. Check if the printer is powered on and connected to the network
2. Restart the printer (power off, wait 10 seconds, power on)
3. On your computer:
   - Settings > Devices > Printers & Scanners
   - Select the printer
   - Click "Open queue"
   - Click "Printer" menu > Uncheck "Use Printer Offline"
4. If still offline, remove and re-add the printer

### Documents Stuck in Print Queue
1. Open the print queue (double-click the printer)
2. Click "Printer" menu > "Cancel All Documents"
3. If that doesn't work:
   - Stop the Print Spooler service:
     - Open Services (services.msc)
     - Find "Print Spooler"
     - Right-click > Stop
   - Delete files in C:\Windows\System32\spool\PRINTERS
   - Start the Print Spooler service again

### Poor Print Quality
1. Run the printer's built-in cleaning utility:
   - Open printer properties
   - Look for "Maintenance" or "Tools" tab
   - Run "Print Head Cleaning" or "Nozzle Check"
2. Check ink or toner levels
3. Ensure you're using the correct paper type setting
4. Try printing a test page from printer properties

### Paper Jams
1. Turn off the printer
2. Open all access doors and panels
3. Gently pull out any jammed paper (don't tear it)
4. Check for small pieces of paper stuck inside
5. Close all doors and turn the printer back on
6. If jams persist, check for:
   - Worn or damaged pickup rollers
   - Incorrect paper type or size
   - Overloaded paper tray

### Wrong Paper Size
1. Open the document you want to print
2. Go to File > Print
3. Click "Printer Properties" or "Preferences"
4. Check the "Paper Size" setting
5. Select the correct size (Letter, A4, Legal, etc.)
6. Also check the paper tray settings on the printer itself

## Network Printer Setup

### Finding Printer IP Address
- Check the printer's display panel (usually under Network or Info)
- Print a network configuration page from the printer menu
- Ask IT for the printer IP address

### Connecting via IP Address
1. Open Settings > Devices > Printers & Scanners
2. Click "Add a printer or scanner"
3. Click "The printer that I want isn't listed"
4. Select "Add a printer using TCP/IP address"
5. Enter the IP address
6. Select the correct driver
7. Name the printer and complete installation

## Print Quality Settings

### Draft Mode (Saves Ink)
1. Open Printer Properties
2. Look for "Print Quality" or "Quality Settings"
3. Select "Draft" or "Economy" mode

### Best Quality
1. Open Printer Properties
2. Select "Best" or "High Quality" mode
3. Use appropriate paper type setting

## When to Escalate
- Persistent paper jams after troubleshooting
- Printer hardware failure (grinding noises, error codes)
- Need printer installed in a new location
- Special printing needs (large format, color calibration)
- Network printer connectivity issues
- Ink or toner replacement needed

## Related Articles
- Paper and Supplies Order Form
- Printer Security Policy
- Print Quota Information
- Label Printer Setup
