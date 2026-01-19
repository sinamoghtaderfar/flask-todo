from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegisterForm(FlaskForm):

    username = StringField("Username", validators=[DataRequired(), Length(min=6, max=10)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired(), Length(min=8, max=12)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo("password")])

    submit = SubmitField("Register")

class LoginForm(FlaskForm):

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class AddTaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")  # توضیحات
    submit = SubmitField("Add Task")
