from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FormField, SelectField, FieldList, DateField, \
    DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput

'''
Veja mais na documentação do WTForms

https://wtforms.readthedocs.io/en/stable/
https://wtforms.readthedocs.io/en/stable/fields.html

Um outro pacote interessante para estudar:

https://wtforms-alchemy.readthedocs.io/en/latest/

'''

class LoginForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired("O preenchimento desse campo é obrigatório")])
    password = PasswordField('Senha', validators=[DataRequired("O preenchimento desse campo é obrigatório")])
    submit = SubmitField('Entrar')

class FormDeRegistro(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired("")])
    login = StringField('Login', validators=[DataRequired("")])
    tipo = SelectField('Tipo de usuário', choices=[('1', 'Administrador'),('0', 'Eleitor')], validators=[DataRequired("")])
    password = PasswordField('Senha', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

class FormEleicao(FlaskForm):
    eleicao = StringField('Digite o título da Eleição', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

class FormPergunta(FlaskForm):
    pergunta = StringField('Digite a pergunta', validators=[DataRequired("")])
    numMin = IntegerField('Digite o número mínimo de resposta', validators=[DataRequired("")])
    numMax = IntegerField('Digite o número máximo de resposta', validators=[DataRequired("")])
    submit = SubmitField('Gerar')

class FormResposta(FlaskForm):
    resposta = StringField('Digite a resposta da pergunta selecionada', validators=[DataRequired("")])
    submit = SubmitField('Cadastrar')

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class FormEleitores(FlaskForm):
    submit = SubmitField('Adicionar')
    eleitores = MultiCheckboxField('Eleitores:', coerce=str, validators=[DataRequired("")])

class FormAjusteResposta(FlaskForm):
    vezes = IntegerField('Digite quantas vezes você deseja votar nessa pergunta', validators=[DataRequired("")])
    submit = SubmitField('Próximo')

class FormVotando(FlaskForm):
    submit = SubmitField('Votar')
    voto = MultiCheckboxField('Voto:', coerce=int, validators=[DataRequired("")])