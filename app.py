from flask import Flask, render_template, json, request, jsonify, session, request_tearing_down
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

@app.route('/help')
def help():
    user = getUserObject()
    return render_template('ajuda.html',user=user)

@app.route('/logout')
def logout():
    return main()

@app.route('/homeEmpresa')
def homeEmpresa():
    empresa = getEmpresa()
    return render_template('indexEmpresa.html',empresa=empresa)

@app.route('/orderForMe')
def orderForMe():
    empresa = getEmpresa()
    orders = selectOrderByEmpresa(empresa[0]);
    return render_template('orderForMe.html',orders=orders)

@app.route('/getHtmlHeader')
def getHtmlHeader():
    user = getUserObject()
    address = getAddressUserDefault()
    return render_template('htmlHeader.html', user=user, endereco=address)

@app.route('/getHtmlHeaderEmpresa')
def getHtmlHeaderEmpresa():
    user = getUserObject()
    address = getAddressUserDefault()
    return render_template('htmlHeaderEmpresa.html', user=user, endereco=address)

@app.route('/myorder')
def myorder():
    orders = selectOrderByUser();
    return render_template('myorder.html', orders=orders)

@app.route('/changeAddress')
def changeAddress():
    address = getAddressAll()
    return render_template('changeAddress.html', address=address)

@app.route('/selectEnd')
def selectEnd():

    id_adr = request.args.get('CdEndereco')
    session['IdEndereco'] = id_adr

    return home()

@app.route('/removeEnd')
def removeEnd():

    id_adr = request.args.get('CdEndereco')

    removeAddress(id_adr)

    return changeAddress()

@app.route('/finalizar')
def finalizar():
    id_order = insertOrder();
    efectiveOrder(id_order);
    orders = selectOrderByUser();

    session.pop('card')

    return render_template('closedOrder.html', orders=orders)


@app.route('/home')
def home():
    user = getUserObject()

    if user[3] == 2:
        return homeEmpresa()

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

    return jsonify(
        message=f"Login Incorreto!",
        category="error",
        data="",
        status=200
    )

@app.route('/insertAddress', methods=['POST', 'GET'])
def insertAddress():
    data = request.get_json(force=True)

    ds_senha = data.get("senha", None)
    ds_cep = data.get("cep", None)
    ds_logradouro = data.get("lagradouro", None)
    ds_numero = data.get("numero", None)
    ds_cidade = data.get("cidade", None)
    ds_estado = data.get("estado", None)
    ds_bairro = data.get("bairro", None)
    ds_complemento = data.get("complemento", None)

    id_user = getUser();

    insertAddress(ds_bairro, ds_cep, ds_cidade, ds_complemento, ds_estado, ds_logradouro, ds_numero, id_user)

    return jsonify(
        message=f"OK",
        category="success",
        data=id_user,
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
    sql = "INSERT INTO tbendereco (DsCep,IdUsuario,DsLagradouro,DsNumero,DsCidade,DsEstado,DsComplemento,DsBairro,InAtivo) " \
          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1)"
    val = (StCep, id_user, StLagradouro, StNumero, StCidade, StEstado, StComplemento, StBairro)
    cursor.execute(sql, val)
    id_add = cursor.lastrowid
    session['CdEndereco'] = id_add
    conn.commit()
    conn.close()

def removeAddress(id_add):

    count = getCountAddressAll()

    #Somente 1 endereço, não pode mudar
    if count > 1:

        #verificar se está sendo usado em algum pedido
        count = getOrderByAddress(id_add)

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = ""

        if count[0] > 0:
            sql = "UPDATE tbendereco SET InAtivo = 0 WHERE CdEndereco = %s"
        else:
            sql = "DELETE FROM tbendereco WHERE CdEndereco = %s"

        val = id_add
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

def getCardByOrder(id_ord):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT IdCarrinho FROM tbpedido where IdPedido= %s",(id_ord))
    id_card = cursor.fetchall()
    conn.close()

    return id_card;

def getAddressByOrder(id_ord):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT CdEndereco FROM tbpedido where IdPedido= %s",(id_ord))
    id_adr = cursor.fetchall()
    conn.close()

    return id_adr;

def getOrderByAddress(id_adr):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM tbpedido where CdEndereco= %s",(id_adr))
    count = cursor.fetchall()
    conn.close()

    return count[0];

@app.route('/detailsOrder')
def detailsOrder():

    id_ord = request.args.get('order')

    id_card = getCardByOrder(id_ord)

    cod_adr = getAddressByOrder(id_ord)

    card = selectCard(id_card)

    product = selectCardItens(id_card)

    address = getAddressSelectUnique(cod_adr)

    return render_template("detailsOrder.html", produtos=product, carrinho=card, endereco=address, id_ord=id_ord)


@app.route('/detailsOrderEmpresa')
def detailsOrderEmpresa():

    id_ord = request.args.get('order')

    id_card = getCardByOrder(id_ord)

    cod_adr = getAddressByOrder(id_ord)

    #card = selectCard(id_card)

    id_emp = getEmpresa()

    product = selectCardItensByEmpresa(id_card, id_emp[0])

    card = selectOrderByEmpresaAndCard(id_card, id_emp[0])

    address = getAddressSelectUnique(cod_adr)

    return render_template("detailsOrderEmpresa.html", produtos=product, carrinho=card, endereco=address, id_ord=id_ord)


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

@app.route('/detailsHash')
def detailsHash():
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

        return render_template('detailsHash.html', produto=produto)


    except Exception as e:
        return render_template('erro.html')
    finally:
        cursor.close()
        conn.close()


@app.route('/raio')
def raio():
    return render_template('raio.html')

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

@app.route('/listEmpresa')
def listEmpresa():
    conn = mysql.connect()
    cursor = conn.cursor()

    id_emp = getEmpresa()

    try:
        cursor.execute(
            "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso,pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,emp.IdEmpresa,ofe.QtProduto " \
            "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
            "INNER JOIN frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
            "WHERE ofe.IdEmpresa=%s", id_emp[0])
        produtos = cursor.fetchall();

        return render_template('listEmpresa.html', produtos=produtos)

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
          "IdUsuario,DsNome,DsEmail,IdPerfil " \
          "FROM tbusuario " \
          "WHERE IdUsuario=%s"
    val = id_user
    cursor.execute(sql, val)
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def getEmpresa():

    id_user = getUser()

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "emp.IdEmpresa,emp.DsNome " \
          "FROM tbempresa emp INNER JOIN tbUsuario usu on emp.IdEmpresa = usu.IdEmpresa " \
          "WHERE usu.IdUsuario=%s"

    val = id_user
    cursor.execute(sql, val)
    empresa = cursor.fetchone()

    cursor.close()
    conn.close()
    return empresa


def getCountAddressAll():
    id_user = 0

    if session.get('IdUsuario'):
        id_user = session['IdUsuario'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "count(*) " \
          "FROM tbendereco " \
          "WHERE IdUsuario=%s and InAtivo = 1 "
    val = id_user
    cursor.execute(sql, val)
    count = cursor.fetchone()

    cursor.close();
    conn.close();

    return count[0]


def getAddressAll():
    id_user = 0

    if session.get('IdUsuario'):
        id_user = session['IdUsuario'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "CdEndereco,DsCep,IdUsuario,DsLagradouro,DsNumero,DsCidade,DsEstado,DsComplemento,DsBairro " \
          "FROM tbendereco " \
          "WHERE IdUsuario=%s and InAtivo = 1 ORDER BY 1 DESC"
    val = id_user
    cursor.execute(sql, val)
    address = cursor.fetchall()

    cursor.close();
    conn.close();

    return address

def getAddressUserDefault():
    id_user = 0

    if session.get('IdEndereco'):
        id_adr = session['IdEndereco'];
        address = getAddressSelectUnique(id_adr)
        if address:
            return address

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

    if address:
        session['IdEndereco'] = address[0]

    cursor.close();
    conn.close();

    return address

def getAddressSession():

    address = 0;

    if session.get('IdEndereco'):
        id_adr = session['IdEndereco'];

        return getAddressSelectUnique(id_adr)

    return address

def getAddressSelectUnique(id_adr):

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "CdEndereco,DsCep,IdUsuario,DsLagradouro,DsNumero,DsCidade,DsEstado,DsComplemento,DsBairro " \
          "FROM tbendereco " \
          "WHERE CdEndereco=%s ORDER BY 1 DESC"
    val = id_adr
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

def selectCardItensByEmpresa(IdCarrinho, IdEmpresa):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT pro.IdProduto,pro.DsNome,pro.IdCategoria,ofe.VrProduto,pro.VrDimensao,pro.VrPeso," \
        "pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome,emp.IdEmpresa," \
        "item.QtProduto,item.VrProduto,item.VrTotal,ofe.IdOferta,item.IdCarrinho " \
        "FROM frutas.tbproduto pro inner join frutas.tboferta ofe on pro.IdProduto = ofe.IdProduto " \
        "inner join frutas.tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
        "inner join frutas.tbcarrinhoitens item on item.IdOferta = ofe.IdOferta " \
        "WHERE item.IdCarrinho = %s and emp.IdEmpresa = %s ", (IdCarrinho, IdEmpresa))
    produtos = cursor.fetchall();

    conn.commit()
    conn.close()

    return produtos;


def insertOrder():
    id_user = getUser()
    address = getAddressUserDefault()

    id_card: int
    id_card = session['card'];

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "INSERT INTO tbpedido (IdCarrinho, IdFormaPagamento, DsStatus, CdEndereco) VALUES (%s,%s,%s,%s)"
    val = (id_card, 1, 'INICIADO',address[0])
    cursor.execute(sql, val)
    id_ord = cursor.lastrowid

    conn.commit();

    return id_ord;



def selectOrderByEmpresaAndCard(id_card, id_emp):

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "car.IdCarrinho,SUM(ite.VrTotal),car.IdUsuario,car.VrFrete,car.VrDesconto,SUM(ite.VrTotal) " \
          "FROM tbpedido ped inner join tbcarrinho car on ped.IdCarrinho = car.IdCarrinho " \
          "INNER JOIN tbformapagamento pag on pag.IdFormaPagamento = ped.IdFormaPagamento " \
          "INNER JOIN tbcarrinhoitens ite on ite.IdCarrinho = car.IdCarrinho " \
          "INNER JOIN tboferta ofe on ofe.IdOferta = ite.IdOferta " \
          "WHERE ofe.IdEmpresa = %s and car.IdCarrinho = %s " \
          "GROUP BY car.IdCarrinho,car.IdUsuario,car.VrFrete, car.VrDesconto "

    val = (id_emp,id_card)
    cursor.execute(sql, val)
    order = cursor.fetchone()

    return order

def selectOrderByEmpresa(id_emp):
    id_user = getUser()

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT " \
          "ped.IdPedido,ped.IdFormaPagamento,ped.DsStatus,pag.DsDescricao,SUM(ite.VrTotal) " \
          "FROM tbpedido ped inner join tbcarrinho car on ped.IdCarrinho = car.IdCarrinho " \
          "INNER JOIN tbformapagamento pag on pag.IdFormaPagamento = ped.IdFormaPagamento " \
          "INNER JOIN tbcarrinhoitens ite on ite.IdCarrinho = car.IdCarrinho " \
          "INNER JOIN tboferta ofe on ofe.IdOferta = ite.IdOferta " \
          "WHERE ofe.IdEmpresa = %s " \
          "GROUP BY ped.IdPedido,ped.IdFormaPagamento,ped.DsStatus,pag.DsDescricao " \
          "ORDER BY 1 desc "

    val = id_emp
    cursor.execute(sql, val)
    orders = cursor.fetchall()

    return orders


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
