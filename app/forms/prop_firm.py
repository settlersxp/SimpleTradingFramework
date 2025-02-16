from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange

class PropFirmForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    full_balance = FloatField('Full Balance', validators=[DataRequired(), NumberRange(min=0)])
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    ip_address = StringField('MT5 Server', validators=[DataRequired()])
    platform_type = SelectField('Platform Type', 
                              choices=[('MT5', 'MT5'), ('MT4', 'MT4')],
                              validators=[DataRequired()])
    is_active = BooleanField('Active') 