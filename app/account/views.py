from datetime import datetime
import os
import secrets
from .. import bcrypt
from flask import  current_app, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from .. import  db
from .form import  LoginForm, RegistrationForm, ResetPasswordForm, UpdateAccountForm
from .models import  User
from . import account_bp
from PIL import Image

import app

@account_bp.route('/users')
@login_required
def users():
    all_users = User.query.all()
    return render_template('users_data.html', all_users=all_users)

@account_bp.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('account.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and user.verify_password(form.password.data):
			login_user(user,remember=form.remember.data)
			flash('You have been logged in!', category='success')
			return redirect(url_for('home.home'))
		else:
			flash('Login unsuccessful.', category='warning')
			return redirect(url_for('account.login'))
	return render_template('login.html', form=form)

@account_bp.route('/user/delete/<id>')
def delete_user_by_id(id):
    data = User.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("account.users"))

@account_bp.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('home.home'))

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home.home'))
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(
			name = form.name.data, 
			email = form.email.data,
			password = form.password.data
			)
		try:
			db.session.add(user)
			db.session.commit()
		except:
			db.session.flush()
			db.session.rollback()
		flash('Thanks for registering')
		return redirect(url_for('home.home'))	
	return render_template('registration.html', form=form)

@account_bp.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf8')
        try:
            db.session.commit()
        except:
            db.session.flush()
            db.session.rollback()
        flash(f"Password successfully changed", category='success')
        return redirect(url_for('account.account'))
    return render_template('reset_password.html', form=form)

@account_bp.route('/account')
@login_required
def account():
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', image_file = image_file)

@account_bp.route('/account/update', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account.account'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.email.data = current_user.email
    return render_template('update_account.html', form=form)

@account_bp.after_request
def after_request(response):
    if current_user:
        current_user.last_seen = datetime.now()
        try:
            db.session.commit()
        except:
            flash('Error while update user last seen!', 'danger')
    return response

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
   
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn