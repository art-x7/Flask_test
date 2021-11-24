from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class TppConfigForm(FlaskForm):
    choices = ["ТПП единичных изделий", "ТПП серийных изделий"]
    prod_name = StringField('Наименование продукта', validators=[DataRequired()])
    tpp_stage = SelectField('Этап ТПП', choices=choices, validators=[DataRequired()])
    tpp_numb = IntegerField('Номер ТПП', validators=[DataRequired()])
    prod_owner = StringField('Фамилия менеджера проекта', validators=[DataRequired()])
    comment = StringField('Комментарий')
    submit = SubmitField('Добавить')


class TppConfigUpdate(FlaskForm):
    choices = ["ТПП единичных изделий", "ТПП серийных изделий"]
    prod_name = StringField('Наименование продукта', validators=[DataRequired()])
    prod_owner = StringField('Фамилия менеджера проекта', validators=[DataRequired()])
    comment = StringField('Комментарий')
    status = StringField('Статус', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class ConfigMaterials(FlaskForm):
    choices = ["Pre-Assembly", "Attach Print", "Wire Bond", "Molding", "Ball Placing", "Singulation", "Functional Test", "MSP"]
    process = SelectField('Процесс', choices=choices, validators=[DataRequired()])
    material = StringField('Наименование материала', validators=[DataRequired()])
    unit = StringField('Единица измерения', validators=[DataRequired()])
    submit = SubmitField('Добавить')
