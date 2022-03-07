from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class DashboardCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Create Dashboard')

class DashboardEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=5, max=50)])
    graph = SelectField('Select graph type',choices=[(1,"Lines"),(2,"Bars"),(3,"Gauge"),(4,"Pie chart")])
    submit = SubmitField('Save')

class GraphEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=5, max=50)])
    graph = SelectField('Select graph type',choices=[(1,"Lines"),(2,"Bars"),(3,"Gauge"),(4,"Pie chart")])
    submit = SubmitField('Save')
