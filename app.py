from flask import Flask, render_template, json, request, jsonify, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

mysql = MySQL()
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'frutas123'
app.config['MYSQL_DATABASE_DB'] = 'frutas'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('init.html')


@app.route('/home')
def home():
    email = session['email']
    return render_template('index.html', email=email)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/insertUser', methods=['POST', 'GET'])
def insertUser():
    nome = request.json['nome']
    email = request.json['email']

    session['email'] = email

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "INSERT INTO customers (DsNome, DsEmail, DsSenha) VALUES (%s, %s, %s)"
    val = ("John", "Highway 21")
    cursor.execute(sql, val)

    conn.commit()
    conn.close()

    return jsonify(nome=nome, email=email)


@app.route('/createAccount')
def createAccount():
    return render_template('createAccount.html')


@app.route('/details')
def details():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        id = request.args.get('id')
        IdEmpresa = request.args.get('IdEmpresa')

        cursor.execute(
            "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso,pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,ofe.IdOferta " \
            "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
            "inner join frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
            "WHERE pro.IdProduto=%s and emp.IdEmpresa=%s",
            (id, IdEmpresa))

        produto = cursor.fetchone()

        return render_template('details.html', produto=produto)

    except Exception as e:
        return render_template('erro.html')
    finally:
        cursor.close()
        conn.close()


@app.route('/htmlCategoria')
def getCategorias():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT IdCategoria,IdNomeCategoria FROM tbCategoria")
    categorias = cursor.fetchall()
    conn.close()

    return render_template('htmlCategoria.html', categorias=categorias)

@app.route('/countCard')
def getCountCard():

    count = 0;
    if session.get('card'):
        IdCarrinho = session['card']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count(*) FROM tbcarrinhoitens WHERE IdCarrinho=%s", (IdCarrinho))
        count = cursor.fetchone()
        conn.close()

    return render_template('countCard.html', count=count)




@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/list')
def list():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        id = request.args.get('categoria')

        cursor.execute(
            "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso,pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,emp.IdEmpresa " \
            "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
            "inner join frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
            "WHERE pro.IdCategoria=%s", id)
        produtos = cursor.fetchall();

        return render_template('list.html', produtos=produtos)

    except Exception as e:
        return render_template('erro.html')
    finally:
        cursor.close()
        conn.close()


@app.route('/cardInsert', methods=['POST', 'GET'])
def insertCard():
    IdOferta = request.args.get('IdOferta')
    QtProduto = request.args.get('Quantidade')
    VrProduto = request.args.get('VrProduto')

    # forced
    session['IdUsuario'] = 1

    conn = mysql.connect()
    cursor = conn.cursor()

    if session.get('card'):
        card = session['card']

    IdUsuario = session['IdUsuario']

    VrTotal = 100.0
    VrSubTotal = 70.0
    VrFrete = 30.0
    VrDesconto = 130.00

    IdCarrinho = 0

    if session.get('card'):
        IdCarrinho = session['card'];
    else:
        sql = "INSERT INTO tbcarrinho (VrTotal, IdUsuario) VALUES (%s,%s)"
        val = (VrTotal, IdUsuario)
        cursor.execute(sql, val)
        IdCarrinho = cursor.lastrowid
        session['card'] = IdCarrinho;

    cursor4 = conn.cursor()
    cursor4.execute(
        "SELECT IdOferta FROM tbcarrinhoitens WHERE IdOferta=%s and IdCarrinho=%s", (IdOferta, IdCarrinho))
    itemCarrinho = cursor4.fetchone()

    cursor5 = conn.cursor()
    if itemCarrinho:
        sql = "UPDATE tbcarrinhoitens SET QtProduto = %s WHERE IdOferta=%s and IdCarrinho=%s"
        val = (QtProduto, IdOferta, IdCarrinho)
        cursor5.execute(sql, val)
        conn.commit()
    else:
        sql = "INSERT INTO tbcarrinhoitens (IdOferta, IdCarrinho, QtProduto, VrProduto, VrTotal) VALUES (%s,%s,%s,%s,%s)"
        val = (IdOferta, IdCarrinho, QtProduto, VrProduto, VrTotal)
        cursor5.execute(sql, val)
        conn.commit()

    cursor3 = conn.cursor()
    cursor3.execute(
        "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso,pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,emp.IdEmpresa," \
        "item.QtProduto,item.VrProduto,item.VrTotal " \
        "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
        "inner join frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
        "inner join frutas.tbcarrinhoitens item on item.IdOferta = ofe.IdOferta " \
        "WHERE item.IdCarrinho=%s", IdCarrinho)
    produtos = cursor3.fetchall();

    conn.commit()
    conn.close()

    return render_template('card.html', produtos=produtos, VrTotal=VrTotal,VrFrete=VrFrete, VrDesconto=VrDesconto, VrSubTotal=VrSubTotal)


if __name__ == "__main__":
    app.run(port=5002)
