# Nosso 1º API - Flask
# Flask & Flask Restful

'''
1 - Definir o objetivo da API:
    ex: Iremos montar uma api de blog, onde eu poderei consultar, editar, criar e excluir postagens em
    um blog usando a API
2 - Qual será a URL base do api?
    ex: Quando você cria uma aplicação local ela terá um url tipo http://localhost:5000, porém quando
    você for subir isso para a nuvem, você terá que comprar ou usar um domínio como url base, vamos
    imaginar um exemplo de devaprender.com/api/
3 - Quais são os endpoints?
    ex: Se seu requisito é de poder consultar, editar, criar e excluir, você terá que disponibilizar os
     endpoints para essas questões
        > /postagens
4 - Quais recursos serão disponibilizados pelo api: informações sobre as postagens
5 - Quais verbos http serão disponibilizados?
    * GET
    * POST
    * PUT
    * DELETE
6 - Quais são as URLs completas para cada um?
    * GET http://localhost:500/postagens
    * GET id http://localhost:500/postagens/1
    * POST id http://localhost:500/postagens
    * PUT id http://localhost:500/postagens/1
    * DELETE id http://localhost:500/postagens/1
    '''

from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor,Postagem,app,db
import jwt
from datetime import datetime,timedelta
from functools import wraps


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem':'Token não foi incluído'}, 401)
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            autor = Autor.query.filter_by(
                id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem':'Token é inválido'}, 401)
        return f(autor,*args,**kwargs)
    return decorated

# Rota padrão - GET http://localhost:5000
@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})        
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor':usuario.id_autor,'exp':datetime.utcnow() + timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token':token})
    return make_response('Login inválido', 401, {'WWW-Authenticate':'Basic realm="Login obrigatório"'})

@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['id_postagem'] = postagem.id_postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['email'] = postagem.email
        lista_de_postagens.append(postagem_atual)
    return jsonify({'postagens': lista_de_postagens})

# Obter postagem por Id - GET http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor,indice):
    postagem = Postagem.query.filter_by(id_postagem=indice).first()
    if not postagem:
        return jsonify('Postagem não encontrada!')
    postagem_atual = {}
    postagem_atual['id_postagem'] = postagem.id_postagem
    postagem_atual['titulo'] = postagem.titulo
    postagem_atual['email'] = postagem.email
    return jsonify({'postagem': postagem_atual})

# Criar uma nova postagem - POST http://localhost:5000/postagem
@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(titulo=nova_postagem['titulo'], senha=nova_postagem['senha'], email=nova_postagem['email'])
    db.session.add(postagem)
    db.session.commit()
    return jsonify({'mensagem': 'Postagem criada com sucesso!'}, 200)

# Alterar uma postagem - PUT http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>',methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor,indice):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=indice).first()
    if not postagem:
        return jsonify({'mensagem': 'Esta postagem não foi encontrada.'})
    try:
        if postagem_alterada['titulo']:
            postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        if postagem_alterada['email']:
            postagem.email = postagem_alterada['email']
    except:
        pass
    try:
        if postagem_alterada['senha']:
            postagem.senha = postagem_alterada['senha']
        db.session.commit()
    except:
        pass
    return jsonify({'mensagem': 'Postagem alterada com sucesso!'})

# Excluir uma postagem - DELETE http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor,indice):
    postagem_existente = Postagem.query.filter_by(id_postagem=indice).first()
    if not postagem_existente:
        return jsonify({'mensagem': 'Esta postagem não foi encontrada.'})
    db.session.delete(postagem_existente)
    db.session.commit()
    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})
    
@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)

    return jsonify({'autores': lista_de_autores})

@app.route('/autores/<int:indice>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor,indice):
    autor = Autor.query.filter_by(id_autor = indice).first()
    if not autor:
        return jsonify(f'Autor não encontrado!')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify({'autor': autor_atual})

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor['nome'],senha=novo_autor['senha'],email=novo_autor['email'])
    
    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso'}, 200)

@app.route('/autores/<int:indice>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor,indice):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=indice).first()
    if not autor:
        return jsonify({'Mensagem': 'Este usuário não foi encontrado!'})
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Usuário alterado com sucesso!'})

@app.route('/autores/<int:indice>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor,indice):
    autor_existente = Autor.query.filter_by(id_autor=indice).first()
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor não foi encontrado'})
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})

# Rodar o servidor do flask
app.run(port=5000, host='localhost', debug=True)