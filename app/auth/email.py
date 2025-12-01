# Project Gamma
#
# File: email.py
# Version: 0.1
# Date: 11/30/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Logic for reset password emails. This is simulated by printing the reset link to the terminal.
# this file could be modified to use a real email service if wanted. In order to do taht, you would
# to setup flask-mail library.

from flask import url_for

def send_reset_email(user):
    """
    Simulates sending a password reset email by printing the link to the console.
    This avoids the need for an SMTP server or Flask-Mail during development.
    """
    # Generate the secure token using the method in your User model
    token = user.get_reset_token()
    
    reset_url = url_for('auth.reset_password_confirm', token=token, _external=True)
    
    # Print to the terminal
    print(f" PASSWORD RESET REQUEST FOR: {user.email}")
    print(f" To reset the password, click the link below:\n")
    print(f" {reset_url}")