# VPN Setup and Troubleshooting Guide

## Overview
All remote employees must use the corporate VPN to access internal resources. This guide covers setup and common troubleshooting steps.

## Initial Setup
1. **Download**: Install the GlobalProtect VPN client from https://itportal.company.com/vpn.
2. **Configuration**: Enter the VPN gateway address: `vpn.company.com`.
3. **Authentication**: Log in using your corporate email and Active Directory password.
4. **Multi-Factor Authentication**: Approve the MFA prompt on your registered authenticator app.

## Common Issues and Solutions

### Cannot Connect to VPN
- **Check internet connection**: Ensure you have a stable internet connection first.
- **Firewall blocking**: Temporarily disable personal firewall software and retry.
- **Outdated client**: Ensure you are running GlobalProtect version 6.0 or later.
- **DNS issues**: Try switching to Google DNS (8.8.8.8) or Cloudflare DNS (1.1.1.1).

### VPN Disconnects Frequently
- **Idle timeout**: The VPN disconnects after 30 minutes of inactivity. This is by design.
- **Network switching**: Moving between Wi-Fi networks will drop the connection. Reconnect manually.
- **Split tunneling**: Enabled by default — only corporate traffic goes through VPN.

### Forgot VPN Password
- VPN uses your Active Directory password. Reset it via the IT Self-Service Portal (see Password Reset Policy).

## Contact
- IT Help Desk: ext. 4500, helpdesk@company.com
- Emergency after-hours VPN issues: Call the 24/7 NOC at ext. 4599.
