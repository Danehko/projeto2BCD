from flask import Flask, render_template, session, url_for, redirect, flash, request
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from meusforms import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.testing import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import*

SECRET_KEY = 'projeto2'

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab02.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

boostrap = Bootstrap(app) # isso habilita o template bootstrap/base.html
nav = Nav()
nav.init_app(app) # isso habilita a criação de menus de navegação do pacote Flask-Nav

@nav.navigation()
def meunavbar():
    menu = Navbar('Urna 3000')
    menu.items = [View('Resultados','listarEleicaoResultados')]
    menu.items.append(View('Login', 'autenticar'))
    if ('logged_in' in session) and session['logged_in'] and (session['tipo'] == 1):
        menu.items.append(Subgroup('Manipular Pessoa',View('Adicionar Pessoa', 'criarPessoa'),View('Alterar tipo Pessoa', 'listarPessoaParaTrocarTipo')))
        menu.items.append(View('Criar Eleicao', 'criarEleicao'))
        menu.items.append(Subgroup('Manipular Eleicao',View('Adicionar Pergunta','listaEleicaoPerg'),View('Adicionar Resposta','listaEleicaoResp'),View('Adicionar Eleitor','listarEleicaoEleitor'),View('Iniciar Eleição', 'listaEleicaoAbrir'),View('Encerrar Eleição', 'listaEleicaoFechar'),View('Apurar Eleição', 'listaEleicaoApurar')))
        menu.items.append(View('Votar', 'listarEleicao'))
        menu.items.append(View('Sair', 'sair'))
    elif ('logged_in' in session) and session['logged_in'] and (session['tipo'] == 0):
        menu.items.append(View('Votar', 'listarEleicao'))
        menu.items.append(View('Sair', 'sair'))
    return menu

class Pessoa(db.Model):
    __tablename__ = "Pessoa"
    login = db.Column(db.String(), primary_key=True)
    nomePessoa = db.Column(db.String())
    tipo = db.Column(db.Integer())
    senha = db.Column(db.String(128))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login = kwargs.pop('login')
        self.nomePessoa = kwargs.pop('nomePessoa')
        self.tipo = kwargs.pop('tipo')
        self.senha = generate_password_hash(kwargs.pop('senha'))

    def set_password(self, password):
        self.senha = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha, password)

    def __repr__(self):
        return '<User {}>'.format(self.login)

class Eleicao(db.Model):
    __tablename__ = "Eleicao"
    idEleicao = db.Column(db.Integer, primary_key=True)
    eleicao = db.Column(db.String())
    dataInicio = db.Column(db.String())
    dataFinal = db.Column(db.String())
    statusEleicao = db.Column(db.Integer())
    apuracao = db.Column(db.Integer())
    login = db.Column(db.String(),ForeignKey('Pessoa.login'))
    pessoa = relationship(Pessoa)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.eleicao =  kwargs.pop('eleicao')
        self.dataInicio = (str(datetime.now())).split('.')[0]
        self.dataFinal = '0'
        self.statusEleicao = 0
        self.apuracao = 0
        self.login =  kwargs.pop('login')

class Eleitor(db.Model):
    __tablename__ = "Eleitor"
    statusVoto = db.Column(db.Integer())
    idEleicao = db.Column(db.Integer(), ForeignKey('Eleicao.idEleicao'), primary_key=True)
    eleicao = relationship(Eleicao)
    login = db.Column(db.String(),ForeignKey('Pessoa.login'),primary_key=True)
    pessoa = relationship(Pessoa)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.statusVoto = 0
        self.idEleicao =  kwargs.pop('idEleicao')
        self.login =  kwargs.pop('login')

class Pergunta(db.Model):
    __tablename__ = "Pergunta"
    idPergunta = db.Column(db.Integer, primary_key=True)
    pergunta = db.Column(db.String())
    numMinResposta = db.Column(db.Integer())
    numMaxResposta = db.Column(db.Integer())
    idEleicao = db.Column(db.Integer(), ForeignKey('Eleicao.idEleicao'))
    eleicao = relationship(Eleicao)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pergunta = kwargs.pop('pergunta')
        self.numMinResposta = kwargs.pop('numMinResposta')
        self.numMaxResposta = kwargs.pop('numMaxResposta')
        self.idEleicao = kwargs.pop('idEleicao')

class Resposta(db.Model):
    __tablename__ = "Resposta"
    idResposta = db.Column(db.Integer, primary_key=True)
    resposta = db.Column(db.String())
    contadorResposta = db.Column(db.Integer())
    idPergunta = db.Column(db.Integer(), ForeignKey('Pergunta.idPergunta'), primary_key=True)
    perg = relationship(Pergunta)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resposta = kwargs.pop('resposta')
        self.contadorResposta = 0
        self.idPergunta = kwargs.pop('idPergunta')

@app.route('/criarPessoa', methods=['GET', 'POST'])
def criarPessoa():
    if session.get('logged_in') and (session['tipo'] == 1):
        form = FormDeRegistro()
        if form.validate_on_submit():
            pessoa = Pessoa(login=form.login.data, nomePessoa=form.nome.data, senha=form.password.data, tipo=form.tipo.data)
            if (Pessoa.query.filter_by(login=form.login.data).first() == None):
                db.session.add(pessoa)
                db.session.commit()
                flash('Usuário registrado')
                return render_template('index.html')
            else:
                flash('Esse login já está registrado')
                return render_template('index.html')
        return render_template('criarPessoa.html', title='Cadastro de usuário', form=form)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/sair')
def sair():
    session['logged_in'] = False
    return redirect(url_for('inicio'))

@app.route('/login', methods=['GET', 'POST'])
def autenticar():
    if (session.get('logged_in') == True):
        flash('Você já está logado.')
        return redirect(url_for('inicio'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            usuario = Pessoa.query.filter_by(login=form.username.data).first_or_404()
            if (usuario.check_password(form.password.data)):
                session['logged_in'] = True
                session['login'] = usuario.login
                session['nome'] = usuario.nomePessoa
                session['tipo'] = usuario.tipo
                return render_template('autenticado.html', user=session.get('nome'))
            else:
                flash('Senha inválidos')
                return redirect(url_for('inicio'))
    return render_template('login.html', title='Autenticação de usuários', form=form)

@app.route('/criarEleicao',methods=['GET', 'POST'])
def criarEleicao():
    if session.get('logged_in') and (session['tipo'] == 1):
        form = FormEleicao()
        if form.validate_on_submit():
            eleicao = Eleicao(eleicao=form.eleicao.data,login=session['login'])
            if(Eleicao.query.filter_by(eleicao=form.eleicao.data,login=session['login']).first() == None):
                db.session.add(eleicao)
                db.session.commit()
                flash('Eleição criada com sucesso.')
                return render_template('index.html')
            else:
                flash('Essa eleição já existe.')
                return render_template('index.html')
        return render_template('criarEleicao.html', title='Criando Eleição', form=form)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selec_pessoa', methods=['GET', 'POST'])
def listarPessoaParaTrocarTipo():
    if session.get('logged_in') and (session['tipo'] == 1):
        pessoa = Pessoa.query.filter_by().all()
        cont = 0
        while(cont!=len(pessoa)):
            if(pessoa[cont].login == session['login']):
                auxiliar = Pessoa.query.filter_by(login=str(session['login'])).first()
                pessoa.remove(auxiliar)
                cont = cont - 1
            cont = cont + 1
        return render_template('selecionarPessoaParaTrocarTipo.html', title='Lista de Pessoas', pessoas=pessoa)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/trocarTipo', methods=['GET', 'POST'])
def tipo():
    if session.get('logged_in') and (session['tipo'] == 1):
        aux = str(request.args['login'])
        if(Pessoa.query.filter_by(login=aux).first() != None):
            pessoa = Pessoa.query.filter_by(login=aux).first()
            if(pessoa.login != session['login']):
                if(pessoa.tipo==0):
                    pessoa.tipo=1
                else:
                    pessoa.tipo=0
                db.session.commit()
                flash('Pessoa alterada com sucesso.')
                return render_template('index.html')
            else:
                flash('Você não pode alterar o seu próprio tipo.')
                return render_template('index.html')
        else:
            flash('Essa pessoa não existe.')
            return render_template('index.html')
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicaoParaResposta', methods=['GET', 'POST'])
def listaEleicaoResp():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(dataFinal='0', statusEleicao=0, apuracao=0,login=session['login']).all()
        return render_template('selecionarEleicaoParaCriarResposta.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarPerguntaParaCriarResposta', methods=['GET', 'POST'])
def listaPergResp():
    if session.get('logged_in') and (session['tipo'] == 1):
        aux = int(request.args['idEleicao'])
        pergunta = Pergunta.query.filter_by(idEleicao=aux).all()
        return render_template('selecionarPerguntaParaCriarResposta.html', title='Listar perguntas da Eleição', perguntas=pergunta)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/criarResposta', methods=['GET', 'POST'])
def criarResp():
    if session.get('logged_in') and (session['tipo'] == 1):
        form = FormResposta()
        if form.validate_on_submit():
            aux = int(request.args['idPergunta'])
            resposta = Resposta(resposta=form.resposta.data, idPergunta=aux)
            if(Resposta.query.filter_by(resposta=form.resposta.data, idPergunta=aux).first() == None):
                db.session.add(resposta)
                db.session.commit()
                flash('Resposta criada com sucesso.')
                return render_template('index.html')
            else:
                flash('Essa resposta já existe.')
                return render_template('index.html')
        return render_template('criarResposta.html', title='Criando resposta', form=form)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicaoParaPergunta', methods=['GET', 'POST'])
def listaEleicaoPerg():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(dataFinal='0', statusEleicao=0, apuracao=0, login=session['login']).all()
        return render_template('selecionarEleicaoParaCriarPergunta.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/criarPergunta', methods=['GET', 'POST'])
def criarPerg():
    if session.get('logged_in') and (session['tipo'] == 1):
        form = FormPergunta()
        if form.validate_on_submit():
            aux = int(request.args['idEleicao'])
            pergunta = Pergunta(pergunta=form.pergunta.data,numMinResposta=form.numMin.data,numMaxResposta=form.numMax.data,idEleicao=aux)
            if(Pergunta.query.filter_by(pergunta=form.pergunta.data,numMinResposta=form.numMin.data,numMaxResposta=form.numMax.data,idEleicao=aux).first() == None):
                db.session.add(pergunta)
                db.session.commit()
                pergunta = Pergunta.query.filter_by(pergunta=form.pergunta.data,numMinResposta=form.numMin.data,numMaxResposta=form.numMax.data,idEleicao=aux).first()
                resposta = Resposta(resposta='Voto Branco', idPergunta=pergunta.idPergunta)
                resposta1 = Resposta(resposta='Voto Nulo', idPergunta=pergunta.idPergunta)
                db.session.add(resposta)
                db.session.add(resposta1)
                db.session.commit()
                flash('Pergunta criada com sucesso.')
                return render_template('index.html')
            else:
                flash('Essa pergunta já existe.')
                return render_template('index.html')
        return render_template('criarPergunta.html', title='Criando Pergunta', form=form)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/abrirEleicao', methods=['GET', 'POST'])
def abrirEleicao():
    if session.get('logged_in') and (session['tipo'] == 1):
        aux = str(request.args['idEleicao'])
        if(Eleicao.query.filter_by(idEleicao=aux).first() != None):
            eleicao = Eleicao.query.filter_by(idEleicao=aux).first()
            print(eleicao.dataFinal)
            if((eleicao.dataFinal=='0') and (eleicao.apuracao == 0) and (eleicao.statusEleicao == 0)):
                eleicao.statusEleicao = 1
                db.session.commit()
                flash('Eleição aberta!')
                return render_template('index.html')
            else:
                flash('Essa eleição já foi aberta!')
                return render_template('index.html')
        else:
            flash('Essa eleição não existe.')
            return render_template('index.html')
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/fecharEleicao', methods=['GET', 'POST'])
def fecharEleicao():
    if session.get('logged_in') and (session['tipo'] == 1):
        aux = str(request.args['idEleicao'])
        if(Eleicao.query.filter_by(idEleicao=aux).first() != None):
            eleicao = Eleicao.query.filter_by(idEleicao=aux).first()
            print(eleicao.dataFinal)
            if((eleicao.dataFinal=='0') and (eleicao.apuracao == 0) and (eleicao.statusEleicao == 1)):
                eleicao.statusEleicao = 2
                eleicao.dataFinal = (str(datetime.now())).split('.')[0]
                db.session.commit()
                flash('Eleição encerrada!')
                return render_template('index.html')
            else:
                flash('Eleicão ainda não foi aberta, já foi fechada ou apurada.')
                return render_template('index.html')
        else:
            flash('Eleição não existe.')
            return render_template('index.html')
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/apurarEleicao', methods=['GET', 'POST'])
def apurarEleicao():
    if session.get('logged_in') and (session['tipo'] == 1):
        aux = str(request.args['idEleicao'])
        if(Eleicao.query.filter_by(idEleicao=aux).first() != None):
            eleicao = Eleicao.query.filter_by(idEleicao=aux).first()
            print(eleicao.dataFinal)
            if((eleicao.dataFinal!='0') and (eleicao.apuracao == 0) and (eleicao.statusEleicao == 2)):
                eleicao.apuracao = 1
                db.session.commit()
                flash('Eleição apurada!')
                return render_template('index.html')
            else:
                flash('Eleicão está aberta, não foi fechada ou já foi apurada.')
                return render_template('index.html')
        else:
            flash('Eleição não existe.')
            return render_template('index.html')
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicaoParaResultados', methods=['GET', 'POST'])
def listarEleicaoResultados():
    eleicao = Eleicao.query.filter_by(statusEleicao=2, apuracao=1).all()
    return render_template('selecionarEleicaoParaResultados.html', title='Listar suas Eleições', eleicoes=eleicao)

@app.route('/selecionarPerguntaParaResultado', methods=['GET', 'POST'])
def listaPergResultado():
    aux = int(request.args['idEleicao'])
    pergunta = Pergunta.query.filter_by(idEleicao=aux).all()
    return render_template('selecionarPerguntaParaResultado.html', title='Listar suas perguntas', perguntas=pergunta)

@app.route('/exibirResultado', methods=['GET', 'POST'])
def exibirResultado():
    aux = int(request.args['idPergunta'])
    resposta = Resposta.query.filter_by(idPergunta=aux).order_by(Resposta.contadorResposta).all()
    cont = 0
    branco = []
    nulo = []
    while (cont != len(resposta)):
        if (resposta[cont].resposta == 'Voto Branco'):
            branco = Resposta.query.filter_by(idPergunta=aux, resposta='Voto Branco').first()
            resposta.remove(branco)
            cont = cont - 1
        elif (resposta[cont].resposta == 'Voto Nulo'):
            nulo = Resposta.query.filter_by(idPergunta=aux, resposta='Voto Nulo').first()
            resposta.remove(nulo)
            cont = cont - 1
        cont = cont + 1
    resposta.append(branco)
    resposta.append(nulo)
    return render_template('exibirResultado.html', title='Listando resultado', resultados=resposta)

@app.route('/selecionarEleicaoParaEleitor', methods=['GET', 'POST'])
def listarEleicaoEleitor():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(dataFinal='0', statusEleicao=0, apuracao=0, login=session['login']).all()
        return render_template('selecionarEleicaoParaEleitor.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/addPessoaEleicao', methods=['GET', 'POST'])
def listarPessoaEleitor():
    if session.get('logged_in') and (session['tipo'] == 1):
        pessoa = Pessoa.query.filter_by().all()
        listaPessoas = [(i.login, i.nomePessoa) for i in pessoa]
        form = FormEleitores()
        aux = int(request.args['idEleicao'])
        form.eleitores.choices = listaPessoas
        listaAux=[]
        if request.method == 'POST':
            loginEleitores = form.eleitores.data
            while (len(loginEleitores) != 0):
                variavel = loginEleitores.pop(0)
                listaAux.append(variavel)
                if(Eleitor.query.filter_by(login=variavel,idEleicao=aux).first() != None):
                    flash("Eleitor já adicionado, operação cancelada")
                    return render_template('index.html')
            while (len(listaAux) != 0):
                variavel = listaAux.pop(0)
                eleitor = Eleitor(idEleicao=aux, login=variavel)
                db.session.add(eleitor)
                db.session.commit()
            flash('Eleitor(es) adicionado')
            return render_template('index.html')
        return render_template('selecionarPessoaEleitor.html', title='Lista de pessoas', form=form)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicao', methods=['GET', 'POST'])
def listarEleicao():
    if session.get('logged_in'):
        eleitor = Eleitor.query.filter_by(statusVoto=0,login=session['login']).all()
        listaidEleicao = [(i.idEleicao) for i in eleitor]
        eleicao = []
        while(len(listaidEleicao)!=0):
            aux = listaidEleicao.pop(0)
            eleicao.append(Eleicao.query.filter_by(dataFinal='0', statusEleicao=1, apuracao=0, idEleicao=aux).first())
        return render_template('selecionarEleicao.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita fazer login para acessar.')
        return render_template('index.html', title='Sem autenticação')

@app.route('/listaPerguntaDaEleicao', methods=['GET', 'POST'])
def listaPergdaEleicao():
    if session.get('logged_in'):
        aux = int(request.args['idEleicao'])
        pergunta = Pergunta.query.filter_by(idEleicao=aux).all()
        variavel = pergunta.pop(0)
        perg = dict()
        perg['idPergunta'] = variavel.idPergunta
        perg['pergunta'] = variavel.pergunta
        perg['idEleicao'] = variavel.idEleicao
        perg['max'] = variavel.numMaxResposta
        perg['min'] = variavel.numMinResposta
        resposta = Resposta.query.filter_by(idPergunta=variavel.idPergunta).all()
        repostasDic = dict()
        repostasDic['Resposta'] = []
        while (len(resposta) != 0):
            lista = dict()
            aux = resposta.pop(0)
            lista['idResposta'] = aux.idResposta
            lista['resposta'] = aux.resposta
            lista['cont'] = aux.contadorResposta
            repostasDic['Resposta'].append(lista)
        pergsDic = dict()
        pergsDic['Perguntas'] = []
        while (len(pergunta) != 0):
            lista = dict()
            aux = pergunta.pop(0)
            lista['idPergunta'] = aux.idPergunta
            lista['pergunta'] = aux.pergunta
            lista['idEleicao'] = aux.idEleicao
            lista['max'] = aux.numMaxResposta
            lista['min'] = aux.numMinResposta
            pergsDic['Perguntas'].append(lista)
        if (variavel.numMinResposta==variavel.numMaxResposta):
            return redirect(url_for('teste', perguntasSobrando=pergsDic, pergunta=perg, resposta=repostasDic, num=variavel.numMaxResposta))
        else:
            return redirect(url_for('teste1', perguntasSobrando=pergsDic, pergunta=perg, resposta=repostasDic, num=0))
    else:
        flash('Necessita fazer login para acessar.')
        return render_template('index.html', title='Sem autenticação')

@app.route('/teste1', methods=['GET', 'POST'])
def teste1():
    if session.get('logged_in'):
        pergunta = eval(request.args['perguntasSobrando'])
        variavel = eval(request.args['pergunta'])
        resposta = eval(request.args['resposta'])
        form = FormAjusteResposta()
        if request.method == 'POST':
            if form.validate_on_submit():
                vezes = form.vezes.data
                return redirect(url_for('teste', perguntasSobrando=pergunta, pergunta=variavel, resposta=resposta, num=vezes))
        return render_template('inserindoVezes.html', form=form, perguntasSobrando=pergunta, pergunta=variavel, resposta=resposta)
    else:
        flash('Necessita fazer login para acessar.')
        return render_template('index.html', title='Sem autenticação')

@app.route('/teste', methods=['GET', 'POST'])
def teste():
    if session.get('logged_in'):
        pergunta = eval(request.args['perguntasSobrando'])
        variavel = eval(request.args['pergunta'])
        resposta = eval(request.args['resposta'])
        num = int(request.args['num'])
        print('idEleicao')
        print(variavel['idEleicao'])
        listaResposta = []
        while (len(resposta['Resposta']) != 0):
            aux = resposta['Resposta'].pop(0)
            listaResposta.append((int(aux['idResposta']), aux['resposta']))
        form = FormVotando()
        form.voto.choices = listaResposta
        if request.method == 'POST':
            respostaId = form.voto.data
            if(len(respostaId)!=num):
                flash('Quantidade de votos esta errada!')
                return render_template('teste.html', form=form, perg=variavel['pergunta'], numVotos=num)
            else:
                cont = 0
                while (cont!=num):
                    auxiliar = Resposta.query.filter_by(idResposta=respostaId[cont]).first()
                    auxiliar.contadorResposta = auxiliar.contadorResposta + 1
                    db.session.commit()
                    cont = cont + 1
                    if (cont == num) and (len(pergunta['Perguntas']) == 0):
                        eleitor = Eleitor.query.filter_by(idEleicao=variavel['idEleicao'], login=session['login']).first()
                        eleitor.statusVoto = 1
                        db.session.commit()
                        flash('Votação finalizada!')
                        return render_template('index.html')
                    elif (cont == num):
                        return redirect(url_for('teste10', perguntasSobrando=pergunta))
        else:
            return render_template('teste.html', form=form, perg=variavel['pergunta'], numVotos=num)
        return render_template('teste.html', title='Votação', form=form)
    else:
        flash('Necessita fazer login para acessar.')
        return render_template('index.html', title='Sem autenticação')

@app.route('/teste10', methods=['GET', 'POST'])
def teste10():
    if session.get('logged_in'):
        pergunta = eval(request.args['perguntasSobrando'])
        variavel = pergunta['Perguntas'].pop(0)
        resposta = Resposta.query.filter_by(idPergunta=variavel['idPergunta']).all()
        respostasDic = dict()
        respostasDic['Resposta'] = []
        while (len(resposta) != 0):
            lista = dict()
            aux = resposta.pop(0)
            lista['idResposta'] = aux.idResposta
            lista['resposta'] = aux.resposta
            lista['cont'] = aux.contadorResposta
            respostasDic['Resposta'].append(lista)
        if(variavel['min']==variavel['max']):
            return redirect(url_for('teste', perguntasSobrando=pergunta, pergunta=variavel,resposta=respostasDic, num=variavel['max']))
        else:
            return redirect(url_for('teste1', perguntasSobrando=pergunta, pergunta=variavel, resposta=respostasDic, num=0))
    else:
        flash('Necessita fazer login para acessar.')
        return render_template('index.html', title='Sem autenticação')

@app.route('/selecionarEleicaoParaAbrir', methods=['GET', 'POST'])
def listaEleicaoAbrir():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(dataFinal='0', statusEleicao=0, apuracao=0,login=session['login']).all()
        return render_template('selecionarEleicaoParaAbrir.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicaoParaFechar', methods=['GET', 'POST'])
def listaEleicaoFechar():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(dataFinal='0', statusEleicao=1, apuracao=0,login=session['login']).all()
        return render_template('selecionarEleicaoParaFechar.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.route('/selecionarEleicaoParaApurar', methods=['GET', 'POST'])
def listaEleicaoApurar():
    if session.get('logged_in') and (session['tipo'] == 1):
        eleicao = Eleicao.query.filter_by(statusEleicao=2, apuracao=0,login=session['login']).all()
        return render_template('selecionarEleicaoParaApurar.html', title='Listar suas Eleições', eleicoes=eleicao)
    else:
        flash('Necessita ser administrador para acessar.')
        return render_template('index.html', title='Sem autorização')

@app.errorhandler(404)
def page_not_found(e):
    '''
    Para tratar erros de páginas não encontradas - HTTP 404
    :param e:
    :return:
    '''
    return render_template('404.html'), 404

@app.route('/')
def inicio():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
