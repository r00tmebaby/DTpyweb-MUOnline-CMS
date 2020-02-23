from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username    = StringField('Username', validators=[DataRequired(), Length(min=3, max=10)])
    email       = StringField('Email', validators=[DataRequired(), Email()])
    password   = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=10)])
    password_repeat = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    question = StringField('Secret Question', validators=[DataRequired()])
    answer = StringField('Secret Answer', validators=[DataRequired()])
    submit = SubmitField('Register')
