from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, SelectField, \
    PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email


message = "Password must match"
date = "input date by YYYY/MM/DD (ex. 2014/10/10)"


class AddTaskForm(Form):
    task_id = IntegerField('Task id')
    name = TextField('Task name', validators=[DataRequired()])
    due_date = DateField('Due date(yy/mm/ddd)',
                         validators=[DataRequired(message=date)],
                         format="%Y/%m/%d")
    priority = SelectField('Priority', validators=[DataRequired()],
                           choices=[('1', '1'), ('2', '2'), ('3', '3'),
                                    ('4', '4'), ('5', '5'), ('6', '6'),
                                    ('7', '7'), ('8', '8'), ('9', '9'),
                                    ('10', '10')])
    status = IntegerField('Status')


class RegisterForm(Form):
    name = TextField('Username', validators=[DataRequired(),
                                             Length(min=6, max=25)])
    email = TextField('Email', validators=[DataRequired(), Email(),
                                           Length(min=6, max=40)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=6, max=40)])
    confirm = PasswordField('Repeat password',
                            validators=[DataRequired(), Length(min=6, max=40),
                                        EqualTo('password', message=message)])


class LoginForm(Form):
    name = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
