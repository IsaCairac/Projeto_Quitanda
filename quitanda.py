from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandazezinho"

usuario = "bella"
senha = "2006"
login = False

#FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False
    
    
#se houver uma conta logada deslogar
if session:
    session.clean()
    
#CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)


#ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    title="Login"
    return render_template("login.html", title=title)


# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha ==senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")


#ROTA DA PÁGINA ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT *FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        title = 'Administração'
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")


#CÓDIGO DO LOGOUT
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

#ROTA DA PÁGINA DE CADASTRO
@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de produtos"
        return render_template("cadprodutos.html", title=title)
    else:
        return redirect("/login")

# ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro",methods=["post"])
def cadastro():
    if verifica_sessao():
        nome_prod=request.form['nome_prod']
        desc_prod=request.form['desc_prod']
        preco_prod=request.form['preco_prod']
        img_prod=request.files['img_prod']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+nome_prod+'.png'
        img_prod.save("static/img/produtos/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?,?,?,?)', (nome_prod, desc_prod, preco_prod, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/login")
    
#ROTA DE EXCLUSÂO
@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

#CRIAR ROTA EDITAR
@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?',(id_prod,)).fetchall()
        conexao.close()
        title = "Edição de produtos"
        return render_template("editar.html", produtos=produtos,title=title)
    else:
        return redirect("/login")
    

#ROTA PARA TRATAR A EDIÇÂO
@app.route("/editarprodutos", methods=['post'])
def editprod():
    id_prod=request.form['id_prod']
    nome_prod=request.form['nome_prod']
    desc_prod=request.form['desc_prod']
    preco_prod=request.form['preco_prod']
    img_prod=request.files['img_prod']
    id_foto=str(uuid.uuid4().hex)
    filename=id_foto+nome_prod+'.png'
    img_prod.save("static/img/produtos/"+filename)
    conexao = conecta_database()
    conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ?, img_prod = ? WHERE id_prod = ?', (nome_prod,desc_prod,preco_prod,filename,id_prod))
    conexao.commit()
    conexao.close()
    return redirect("/adm")

#ROTA DA PÁGINA DE BUSCA
@app.route("/busca", methods=["post"])
def busca():
    busca= request.form['Buscar']
    conexao = conecta_database()
    produtos = conexao.execute(' SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"', (busca,)).fetchall()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

#ROTA DA PÀGINA SOBRE
@app.route("/sobre")
def sobre():
    if verifica_sessao():
        title = "Sobre"
        return render_template("sobre.html", title=title)

# FINAL DO CODIGO - EXECUTANDO O SERVIDOR
app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0' post=5000)