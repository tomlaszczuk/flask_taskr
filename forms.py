from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired


class AddTaskForm(Form):
    task_id = IntegerField('Task id')
    name = TextField('Task name', validators=[DataRequired()])
    due_date = DateField('Due date(yy/mm/ddd)',
                         validators=[DataRequired()],
                         format="%Y/%m/%d")
    priority = SelectField('Priority', validators=[DataRequired()],
                           choices=[('1', '1'), ('2', '2'), ('3', '3'),
                           ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                           ('8', '8'), ('9', '9'), ('10', '10')])
    status = IntegerField('Status')
