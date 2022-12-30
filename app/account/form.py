from flask_wtf import FlaskForm  
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField, BooleanField ,validators,ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from .models import User

class ContactForm(FlaskForm):
    name = StringField("Name", 
                      [DataRequired("Please enter your name."), 
                       Length(min=4, max=10, message ='Length must be between 4 and 10')
                       ])
    email = StringField('Email', validators=[Email("Please enter correct email")])
    phone = StringField('Phone',
    validators=[Regexp('(^380\s?[0-9]{2}\s?[0-9]{3}\s?[0-9]{4}$)$', message='Enter correct number')])
    subject = SelectField('Subject', choices=['Football', 'Basketball', 'Golf', 'Voleyball'])
    message = TextAreaField('Message', validators=[DataRequired("Enter a message."), Length(min=0,max=500)])
    submit = SubmitField("Send")

class RegistrationForm(FlaskForm):
	name = StringField("Name", 
	                  [
						DataRequired("Please enter your name."), 
					    Regexp('^[A-Za-z][a-zA-Z0-9_.-]+$', message='Name must have only letters, numbers, dots or underscores.'),
	                    Length(min=4, max=10, message ='Length must be between 4 and 10')
	                   ])
	email = StringField('Email', validators=[Email("Please enter correct email")])
	password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('password_confirm', message='Passwords must match')
    ])
	password_confirm = PasswordField('Repeat Password')
	submit = SubmitField("Send")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_name(self,field):
		if User.query.filter_by(name=field.data).first():
			raise ValidationError('Name already taken.')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired("Please enter your name."), Length(min=4, max=14, message ='Length of this field must be between 4 and 14')])
    email = StringField('Email', validators=[DataRequired("Please enter your email."), Email("Please enter correct email")])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    about_me = TextAreaField("About me", validators=[Length(max=120, message='Max length is 120')])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.name:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('This username is taken.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('This email is taken.')

class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password',
                             validators=[Length(min=6,
                                                message='Password must be longer then 6')])
    confirm_password = PasswordField('Confirm new password',
                                     validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Reset password")

    def validate_old_password(self, old_password):
        if not current_user.verify_password(old_password.data):
            raise ValidationError('Wrong password. Try again!')