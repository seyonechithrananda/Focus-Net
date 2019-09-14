# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class IPForm(FlaskForm):

    address = StringField("IP Adress:")
    port = IntegerField("Port:")
    submit = SubmitField("Submit")