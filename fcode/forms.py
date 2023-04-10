from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,TextAreaField,IntegerField,SelectField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError,validators,DateField
# from models import *


class ADMINForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),validators.Length(min=3)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField("Log in")

class passwordForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),validators.Length(min=3)])
    password=PasswordField('Password',validators=[DataRequired()])
    newpassword=PasswordField('New Password',validators=[DataRequired()])
    submit=SubmitField("Submit")


class StudentForm(FlaskForm):
    username= StringField("Enter your Username",validators=[validators.input_required(),validators.Length(min=3)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField("Enter password for account-login",validators=[validators.input_required(),validators.Length(min=3)])
    place = StringField("Enter Address")
    submit=SubmitField("submit")

class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),validators.Length(min=3)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField("Log in")

# class Registration(FlaskForm):
#     username=StringField('Username',validators=[DataRequired()])
#     password=PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Password must match')])
#     pass_confirm=PasswordField('Confirm Password',validators=[DataRequired()])
#     submit=SubmitField('Register')

#     def check_mail(self,field):
#         if User_reg.query.filter_by(email=field.data).first():
#             raise ValidationError('Your email has been registred')

#     def check_username(self,field):
#         if User_reg.query.filter_by(username=field.data).first():
#             raise ValidationError('Username is taken')