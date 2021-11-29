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
    session.clear()
    return render_template('init.html')

@app.route('/getHtmlHeader')
def getHtmlHeader():
    user = getUserObject()
    address = getAddressUserDefault()
    return render_template('htmlHeader.html', user=user, endereco=address)

@app.route('/myorder')
def myorder():
    orders = selectOrderByUser();

    return render_template('myorder.html', orders=orders)


@app.route('/finalizar')
def finalizar():
    id_order = insertOrder();
    efectiveOrder(id_order);
    orders = selectOrderByUser();

    session.pop('card')

    return render_template('closedOrder.html', orders=orders)


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/closedOrder')
def closedOrder():
    return render_template('closedOrder.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/loginOpen', methods=['POST', 'GET'])
def loginOpen():
    data = request.get_json(force=True)
    ds_email = data.get("email", None)
    st_pwd = data.get("senha", None)

    id_user = getUserEmailAndPwd(ds_email, st_pwd)

    if id_user:
        session['IdUsuario'] = id_user
        return jsonify(
            message=f"OK",
            category="success",
            data=id_user,
            status=200
        )
        session.pop('card')

    return jsonify(
        message=f"Login Incorreto!",
        category="error",
        data="",
        status=200
    )


@app.route('/insertUser', methods=['POST', 'GET'])
def insertUser():
    data = request.get_json(force=True)
    ds_email = data.get("email", None)
    ds_nome = data.get("nome", None)
    ds_senha = data.get("senha", None)
    ds_cep = data.get("cep", None)
    ds_logradouro = data.get("lagradouro", None)
    ds_numero = data.get("numero", None)
    ds_cidade = data.get("cidade", None)
    ds_estado = data.get("estado", None)
    ds_bairro = data.get("bairro", None)
    ds_complemento = data.get("complemento", None)

    id_user = getUserEmail(ds_email)

    if id_user:
        return jsonify(
            message=f"Email já cadastrado !",
            category="success",
            data=id_user,
            status=200
        )
    else:
        id_user = createUser(ds_email, ds_nome, ds_senha)
        insertAddress(ds_bairro, ds_cep, ds_cidade, ds_complemento, ds_estado, ds_logradouro, ds_numero, id_user)

    return jsonify(
        message=f"OK",
        category="success",
        data=id_user,
        status=200
    )


def insertAddress(StBairro, StCep, StCidade, StComplemento, StEstado, StLagradouro, StNumero, id_user):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "INSERT INTO tbendereco (DsCep,IdUsuario,DsLagradouro,DsNumero,DsCidade,DsEstado,DsComplemento,DsBairro) " \
          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (StCep, id_user, StLagradouro, StNumero, StCidade, StEstado, StComplemento, StBairro)
    cursor.execute(sql, val)
    conn.commit()
    conn.close()


def createUser(StEmail, StNome, StSenha):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "INSERT INTO tbusuario (DsNome,DsEmail,IdPerfil,DsSenha) VALUES (%s,%s,%s,%s)"
    val = (StNome, StEmail, 1, StSenha)
    cursor.execute(sql, val)
    id_card = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_card


def getUserEmail(ds_email):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "select IdUsuario FROM tbusuario WHERE DsEmail = %s"
    val = (ds_email)
    cursor.execute(sql, val)
    id_user = cursor.fetchone()
    conn.close()
    return id_user


def getUserEmailAndPwd(ds_email, st_pwd):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "select IdUsuario FROM tbusuario WHERE DsEmail = %s and DsSenha = %s"
    val = (ds_email, st_pwd)
    cursor.execute(sql, val)
    id_user = cursor.fetchone()
    conn.close()
    return id_user


@app.route('/linkUpdateCardItens', methods=['POST', 'GET'])
def linkUpdateCardItens():
    id_ofer = request.json['oferta']
    id_card = request.json['carrinho']
    qt_item = request.json['quantidade']

    updateQuantityCardItens(id_card, id_ofer, qt_item)

    return json.dumps('OK')


@app.route('/createAccount')
def createAccount():
    return render_template('createAccount.html')

@app.route('/detailsOrder')
def detailsOrder():


    card = selectCard(id_card)

    product = selectCardItens(id_card)

    address = getAddressUserDefault()

    return render_template(page, produtos=product, carrinho=card, endereco=address)


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
    count_card = 0;
    if session.get('card'):
        id_card = session['card']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(QtProduto),0) FROM tbcarrinhoitens WHERE IdCarrinho=%s", (id_card))
        count_card = cursor.fetchone()
        conn.close()

    return render_template('countCard.html', count=count_card)


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


@app.route('/removeCardItem', methods=['POST', 'GET'])
def removeCardItem():
    id_ofer = request.args.get('IdOferta')
    id_card = request.args.get('IdCarrinho')

    removeCardItens(id_card, id_ofer)

    return getTemplateCard(id_card, 'card.html')


@app.route('/card', methods=['POST', 'GET'])
def card():
    id_card = getOrCreateCard()
    return getTemplateCard(id_card, 'card.html')


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    id_card = getOrCreateCard()
    return getTemplateCard(id_card, 'checkout.html')


@app.route('/cardInsert', methods=['POST', 'GET'])
def insertCard():

    id_ofer = request.args.get('IdOferta')
    qt_product = request.args.get('Quantidade')
    vr_product = request.args.get('VrProduto')

    id_card = getOrCreateCard()

    insertCardItens(id_card, id_ofer, qt_product, vr_product)

    return getTemplateCard(id_card, 'card.html')


def getTemplateCard(id_card, page):
    updateCard(id_card)

    card = selectCard(id_card)

    product = selectCardItens(id_card)

    address = getAddressUserDefault()

    return render_template(page, produtos=product, carrinho=card,endereco=address)


def insertCardItens(IdCarrinho, IdOferta, QtProduto, VrProduto):
    conn = mysql.connect()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT IdOferta "
        "FROM tbcarrinhoitens "
        "WHERE IdOferta=%s and IdCarrinho=%s", (IdOferta, IdCarrinho))
    itemCarrinho = cursor.fetchone()
    cursor.close()

    cursor_action = conn.cursor()
    if itemCarrinho:
        sql = "UPDATE tbcarrinhoitens SET QtProduto = %s WHERE IdOferta=%s and IdCarrinho=%s"
        val = (QtProduto, IdOferta, IdCarrinho)
        cursor_action.execute(sql, val)
    else:
        sql = "INSERT INTO tbcarrinhoitens (IdOferta, IdCarrinho, QtProduto, VrProduto, VrTotal) VALUES (%s,%s,%s,%s,%s)"
        val = (IdOferta, IdCarrinho, QtProduto, VrProduto, 0)
        cursor_action.execute(sql, val)

    conn.commit()
    cursor_action.close()

    conn.close()


def removeCardItens(id_card, id_ofer):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "DELETE FROM tbcarrinhoitens WHERE IdOferta=%s and IdCarrinho=%s"
    val = (id_ofer, id_card)
    cursor.execute(sql, val)
    conn.commit()
    conn.close()

    updateCard(id_card)


def updateCard(id_card):
    updateCardItens(id_card)

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "UPDATE tbcarrinho " \
          "SET VrSubTotal = (SELECT COALESCE(SUM(VrTotal),0) FROM tbcarrinhoitens WHERE IdCarrinho=%s)," \
          "VrTotal = (VrSubTotal + VrFrete) - VrDesconto " \
          "WHERE IdCarrinho=%s"
    val = (id_card, id_card)
    cursor.execute(sql, val)
    conn.commit()
    conn.close();


def updateCardItens(id_card):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "UPDATE tbcarrinhoitens " \
          "SET VrTotal = VrProduto * QtProduto " \
          "WHERE IdCarrinho=%s"
    val = (id_card)
    cursor.execute(sql, val)
    conn.commit()

    cursor.close();
    conn.close();


def updateQuantityCardItens(id_card, id_ofer, qt_item):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "UPDATE tbcarrinhoitens " \
          "SET QtProduto = %s " \
          "WHERE IdCarrinho=%s and IdOferta = %s"
    val = (qt_item, id_card, id_ofer)
    cursor.execute(sql, val)
    conn.commit()

    cursor.close();
    conn.close();

    updateCard(id_card)


def getOrCreateCard():
    id_user = getUser()

    id_card: int

    if session.get('card'):
        id_card = session['card'];
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO tbcarrinho (VrTotal, IdUsuario, VrFrete, VrDesconto, VrSubTotal) VALUES (%s,%s,%s,%s,%s)"
        val = (0, id_user, 0, 0, 0)
        cursor.execute(sql, val)
        id_card = cursor.lastrowid
        session['card'] = id_card;
        conn.commit();

    return id_card;


def getUser():
    idUsuario = 0

    if session.get('IdUsuario'):
        idUsuario = session['IdUsuario'];

    return idUsuario

def getUserObject():
    id_user = 0

    if session.get('IdUsuario'):
        id_user = session['IdUsuario'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "IdUsuario,DsNome,DsEmail " \
          "FROM tbusuario " \
          "WHERE IdUsuario=%s"
    val = id_user
    cursor.execute(sql, val)
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def getAddressUserDefault():
    id_user = 0

    if session.get('IdUsuario'):
        id_user = session['IdUsuario'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "CdEndereco,DsCep,IdUsuario,DsLagradouro,DsNumero,DsCidade,DsEstado,DsComplemento,DsBairro " \
          "FROM tbendereco " \
          "WHERE IdUsuario=%s ORDER BY 1 DESC"
    val = id_user
    cursor.execute(sql, val)
    address = cursor.fetchone()

    cursor.close();
    conn.close();

    return address


def selectCard(id_card):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "IdCarrinho,VrTotal,IdUsuario,VrFrete,VrDesconto,VrSubTotal " \
          "FROM tbcarrinho " \
          "WHERE IdCarrinho=%s"
    val = id_card
    cursor.execute(sql, val)
    card = cursor.fetchone()

    cursor.close();
    conn.close();

    return card


def selectCardItens(IdCarrinho):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso," \
        "pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,emp.IdEmpresa," \
        "item.QtProduto,item.VrProduto,item.VrTotal, ofe.IdOferta, item.IdCarrinho " \
        "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
        "inner join frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
        "inner join frutas.tbcarrinhoitens item on item.IdOferta = ofe.IdOferta " \
        "WHERE item.IdCarrinho=%s", IdCarrinho)
    produtos = cursor.fetchall();

    conn.commit()
    conn.close()

    return produtos;


def insertOrder():
    id_user = getUser()

    id_card: int
    id_card = session['card'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "INSERT INTO tbpedido (IdCarrinho, IdFormaPagamento, DsStatus) VALUES (%s,%s,%s)"
    val = (id_card, 1, 'INICIADO')
    cursor.execute(sql, val)
    id_ord = cursor.lastrowid

    conn.commit();

    return id_ord;


def selectOrderByUser():
    id_user = getUser()

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "ped.IdPedido,ped.IdFormaPagamento,ped.DsStatus,pag.DsDescricao,car.VrTotal " \
          "FROM tbpedido ped inner join tbcarrinho car on ped.IdCarrinho = car.IdCarrinho " \
          "INNER JOIN tbformapagamento pag on pag.IdFormaPagamento = ped.IdFormaPagamento " \
          "WHERE car.IdUsuario = %s ORDER BY 1 desc"
    val = id_user
    cursor.execute(sql, val)
    orders = cursor.fetchall()

    return orders;


def efectiveOrder(id_order):
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "UPDATE tboferta ofe " \
          "inner join tbcarrinhoitens ite on ite.IdOferta = ofe.IdOferta " \
          "inner join tbpedido ped on ped.IdCarrinho = ite.IdCarrinho " \
          "SET ofe.QtProduto = (ofe.QtProduto - ite.IdOferta) " \
          "WHERE ped.IdPedido = %s"

    val = (id_order)
    cursor.execute(sql, val)
    conn.commit()
    conn.close();


if __name__ == "__main__":
    app.run(port=5002)
