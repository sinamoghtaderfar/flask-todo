from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed

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
    description = TextAreaField("Description")
    submit = SubmitField("Add Task")

class UpdateProfileForm(FlaskForm):
    #username = StringField("Username", validators=[DataRequired()])
    profile_image = FileField("Profile Image", validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField("Update Profile")
