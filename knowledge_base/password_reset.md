# Password Reset Guide

## Overview
This guide covers the standard procedure for resetting user passwords across company systems.

## Common Symptoms
- User cannot log into their workstation
- User cannot access email or company applications
- Account locked after too many failed attempts
- User forgot their password after vacation

## Self-Service Password Reset

### Step 1: Try the Self-Service Portal
1. Go to https://accounts.company.com/reset
2. Enter your employee ID or email address
3. Check your personal email for the reset link
4. Click the link and create a new password
5. Password must be at least 12 characters with uppercase, lowercase, number, and symbol

### Step 2: If Self-Service Fails
1. Call the IT Help Desk at ext. 5555
2. Verify your identity with employee ID and last 4 digits of SSN
3. The agent will send a temporary password to your manager's email
4. Log in with the temporary password and change it immediately

## IT Admin Reset Procedure

### Step 1: Verify Identity
- Confirm employee name, department, and manager
- Verify employee ID number
- Check that the employee is still active in HR system

### Step 2: Reset in Active Directory
1. Open Active Directory Users and Computers
2. Search for the user by name or employee ID
3. Right-click the user and select "Reset Password"
4. Enter a temporary password (must meet complexity requirements)
5. Check "User must change password at next logon"
6. Click OK

### Step 3: Reset Related Systems
- **Email (Exchange):** Password syncs automatically via AD
- **VPN:** Password syncs automatically via AD
- **HR System:** May need manual reset - contact HR IT liaison
- **Specialty Applications:** Check application-specific access list

### Step 4: Notify User
- Call or email the user with the temporary password
- Instruct them to log in and change the password immediately
- Document the reset in the ticketing system

## Password Policy Requirements
- Minimum 12 characters
- Must include uppercase, lowercase, numbers, and symbols
- Cannot reuse last 10 passwords
- Must change every 90 days
- Account locks after 5 failed attempts

## When to Escalate
- User is locked out and cannot verify identity
- Suspicious activity on the account (possible compromise)
- Service account password reset needed
- Executive or privileged account reset (requires manager approval)

## Related Articles
- Account Lockout Policy
- Multi-Factor Authentication Setup
- Service Account Management
