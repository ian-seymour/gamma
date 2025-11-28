# Project Gamma
#
# File: routes.py
# Version: 0.1
# Date: 11/27/25
#
# Author: Ian Seymour / ian.seymour@cwu.edu
#
# Description:
# Authentication routes for web app.

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm, ResetPasswordForm, NewPasswordForm
from ..models import User
from .. import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('weather.dashboard'))
    
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('You are now registered! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Create Account', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request page."""
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None:
            flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        else:
            flash('Password reset link will be sent to your email. TEST VERSION: Use the reset link directly.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    """Password reset confirmation page."""
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard'))
    
    form = NewPasswordForm()
    if form.validate_on_submit():
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_confirm.html', title='Reset Password', form=form)
