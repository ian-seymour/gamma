# Project Gamma
#
# File: forms.py
# Version: 0.1
# Date: 11/27/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Forms for authentication in the Project Gamma web application.

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from ..models import User
import re

class ComplexityValidator:
    """
    Custom validator to enforce password complexity requirements:
    - Must contain 3 out of 4 character types: lowercase, uppercase, number, special character.
    """
    def __init__(self, message=None):
        if not message:
            message = 'Password must contain at least 3 of the following: lowercase, uppercase, number, or special character.'
        self.message = message

    def __call__(self, form, field):
        password = field.data
        if not password:
            # DataRequired handles empty password
            return

        # Check for presence of character types using regex
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        # Checks for anything that is not a letter or number
        has_special = bool(re.search(r'[^\w\s]', password)) 

        # Count how many types are present
        complexity_score = sum([has_lower, has_upper, has_digit, has_special])

        if complexity_score < 3:
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    """Form for user login."""
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    """Form for user registration."""
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=20, message='Password must be between 6 and 20 characters long'),
        ComplexityValidator() # this checks password for requirements
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')
    
    def validate_email(self, field):
        """Check if email already exists."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. Please log in or use a different email.')


class ResetPasswordForm(FlaskForm):
    """Form for password reset."""
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    submit = SubmitField('Reset Password')


class NewPasswordForm(FlaskForm):
    """Form for setting a new password."""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=20, message='Password must be between 6 and 20 characters long'),
        ComplexityValidator() # this checks password afor requirements
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
