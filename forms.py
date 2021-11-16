from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class TppConfigForm(FlaskForm):
    prod_name = StringField('Наименование продукта', validators=[DataRequired()])
    tpp_stage = SelectField('Этап ТПП', choices=["ТПП единичных изделий", "ТПП серийных изделий"], validators=[DataRequired()])
    tpp_numb = IntegerField('Номер ТПП', validators=[DataRequired()])
    prod_owner = StringField('Фамилия менеджера проекта', validators=[DataRequired()])
    comment = StringField('Комментарий')
    submit = SubmitField('Добавить')


class TppConfigUpdate(FlaskForm):
    prod_name = StringField('Наименование продукта', validators=[DataRequired()])
    tpp_stage = SelectField('Этап ТПП', choices=["ТПП единичных изделий", "ТПП серийных изделий"], validators=[DataRequired()])
    tpp_numb = IntegerField('Номер ТПП', validators=[DataRequired()])
    prod_owner = StringField('Фамилия менеджера проекта', validators=[DataRequired()])
    comment = StringField('Комментарий')
    status = StringField('Статус', validators=[DataRequired()])
    submit = SubmitField('Изменить')
   
    
