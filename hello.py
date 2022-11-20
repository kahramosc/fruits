import logging
import os
import app
from flask import Flask, render_template
from flask_ask import Ask, session, question, statement, context
from flaskext.mysql import MySQL

mysql = MySQL()
hello = Flask(__name__)

# MySQL configurations
hello.config['MYSQL_DATABASE_USER'] = 'frutas'
hello.config['MYSQL_DATABASE_PASSWORD'] = 'frutas123'
hello.config['MYSQL_DATABASE_DB'] = 'frutas'
hello.config['MYSQL_DATABASE_HOST'] = 'frutas.mysql.dbaas.com.br'
mysql.init_app(hello)

hello = Flask(__name__)
ask = Ask(hello, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


def getUserAlexa():
    ds_userId = context.System.user.userId
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "select DsNome,IdUsuario FROM tbusuario WHERE IdAlexa = %s"
    val = (ds_userId)
    cursor.execute(sql, val)
    id_user = cursor.fetchone()
    conn.close()
    return id_user


def getUserCestaAlexa():
    user = getUserAlexa();

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "select IdCesta,IdUsuario,DsNome FROM tbcestapersonalizada WHERE IdUsuario = %s"
    val = (user[1])
    cursor.execute(sql, val)
    cestas = cursor.fetchall()
    conn.close()
    return cestas


def getCestaAlexa(idCesta):
    id_user = getUserAlexa();

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "select ces.IdCesta,ces.IdUsuario,ces.DsNome,pro.DsNome,pces.QtProduto,pro.IdProduto FROM tbcestapersonalizada ces inner join tbprodutoscesta pces on ces.IdCesta=pces.IdCesta inner join tbproduto pro on pro.IdProduto=pces.IdProduto WHERE ces.DsNome = %s"
    val = (idCesta)
    cursor.execute(sql, val)
    produtos = cursor.fetchall()
    conn.close()
    return produtos


@ask.launch
def launch():

    user = getUserAlexa()
    session.attributes['IdUsuario'] = user[1]

    speech_text = 'Bem vindo a Feira Livre ' + user[
        0] + ', vamos fazer um pedido? Para listar suas cestas personalizadas, fale minhas cestas.'

    getOrCreateCard();

    return question(speech_text).reprompt(speech_text).simple_card('Comprar', speech_text)


@ask.intent("CestaIntent")
def cestasList():

    cestas = getUserCestaAlexa();

    headline_msg = 'Você não tem nenhuma cesta cadastrada, cadastre o site da feira livre.';
    if cestas:
        headline_msg = 'Você tem ' + str(len(cestas)) + " cadastradas.";
        for cesta in cestas:
            headline_msg = headline_msg + ' ' + cesta[2] + ','

    headline_msg = headline_msg+ ' para ver cesta, diga ver cesta é o nome, ou comprar e o nome da cesta.'
    return question(headline_msg)


@ask.intent("VerCestaIntent", mapping={'cesta_name': 'CestaName'})
def share_headlines(cesta_name):

    cestas = getCestaAlexa(cesta_name);

    headline_msg = ""
    if len(cestas) == 0:
        headline_msg = 'Sua Cesta Não' + cesta_name + ' tem ' + str(len(cestas)) + ' Produtos';
    else:
        headline_msg = 'Sua Cesta ' + cesta_name + ' tem ' + str(len(cestas)) + ' Produtos, são eles';
        for cesta in cestas:
            headline_msg = headline_msg + ' ' + str(cesta[4]) + ' Itens de ' + str(cesta[3])
    headline_msg = headline_msg + ' para comprar, diga comprar e o nome da cesta.'
    return question(headline_msg)


@ask.intent("PromoIntent")
def promo():

    user_id = context.System.user.userId

    # headline_msg = 'Produtos {}'.format(headlines)
    headline_msg = 'Hoje temos muitos produtos na promoção, banana por 10 reais.'
    return question(headline_msg)

@ask.intent("StatusIntent")
def share_headlines():
    id_user = getUserAlexa();

    orders = app.selectOrderByUserIdLast(id_user[1]);
    try:
        headline_msg = 'Seu Pedido número '+str(orders[0])+' está com status '+str(orders[1])+', chegará em até 45 minutos.'
    except Exception as e:
        headline_msg = 'Você não tem nenhum pedido em andamento!'

    return question(headline_msg)


@ask.intent("ConfirmoIntent")
def confirmo():

    id_user = getUserAlexa();

    id_user_id = id_user[1]

    address = app.getAddressUserDefaultIdUser(id_user_id)

    id_card = getOrCreateCard()

    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "INSERT INTO tbpedido (IdCarrinho, IdFormaPagamento, DsStatus, CdEndereco) VALUES (%s,%s,%s,%s)"
    val = (id_card, 1, 'INICIADO', address[0])
    cursor.execute(sql, val)
    id_ord = cursor.lastrowid

    conn.commit();

    app.efectiveOrder(id_ord);

    orders = app.selectOrderByUserId(id_user_id);

    session.attributes['card'] = '';

    headline_msg = 'Pedido confirmado ! Número '+ str(orders[0][0])+' Obrigado, em breve o mesmo será entregue em seu endereço, para consultar o status, diga status compra.'
    return question(headline_msg)

@ask.intent("NConfirmoIntent")
def confirmo():

    headline_msg = 'Pedido cancelado'
    return statement(headline_msg)

@ask.intent('BuySkillItemIntent', mapping={'product_name': 'ProductName'})
def buy_intent(product_name):

    itens = getCestaAlexa(product_name)
    #ces.IdCesta,ces.IdUsuario,ces.DsNome,pro.DsNome,pces.QtProduto

    for item in itens:
       produtoOferta = getMelhorOferta(item[5])#pro.IdProduto
       insertCard(produtoOferta[0], item[4],produtoOferta[1])

    app.updateCard(getOrCreateCard());

    id_card = app.selectCard(getOrCreateCard());

    valor = str(id_card[1])
    minutos = "45" #todo
    fornecedor = "1" #todo
    headline_msg = 'Sua Cesta ' + product_name+' será montada utilizando '+fornecedor+' fornecedor, o valor ficou '+valor+', será entregue em até '+minutos+' minutos, diga confirmo ou cancelar?'
    return question(headline_msg).reprompt(headline_msg).simple_card('Comprar', headline_msg)


def getMelhorOferta(idProduto):
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT ofe.IdOferta,ofe.VrProduto,pro.IdProduto,pro.DsNome,pro.IdCategoria,pro.VrDimensao,pro.VrPeso,pro.DsProduto,pro.NmRaiting,pro.DsPorcao,pro.DsImagem,emp.DsNome " \
            "FROM tbproduto pro inner join tboferta ofe on pro.IdProduto = ofe.IdProduto " \
            "inner join tbempresa emp on ofe.IdEmpresa = emp.IdEmpresa  " \
            "WHERE pro.IdProduto=%s order by ofe.VrProduto desc",
            (idProduto))

        produtoOferta = cursor.fetchone()

        return produtoOferta

    except Exception as e:
        return render_template('erro.html')
    finally:
        cursor.close()
        conn.close()

@ask.intent("NoIntent")
def no_intent():

    bye_text = 'estão está bem xauxau'
    return statement(bye_text)


@ask.intent('HelloWorldIntent')
def hello_world():

    speech_text = 'Olá mundo Diogo'
    return statement(speech_text).simple_card('Agendar', speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():

    help_text = render_template('help')
    return question(help_text).reprompt(help_text)

@ask.intent('AMAZON.StopIntent')
def help():

    help_text = 'Obrigado por acessar a Feira Livre!'
    return question(help_text).reprompt(help_text)



@ask.intent('AMAZON.FallbackIntent')
def Fallback():

    help_text = 'Opisss... vamos tentar de novo.'
    return question(help_text).reprompt(help_text)


@ask.session_ended
def session_ended():
    return "{}", 200

def getOrCreateCard():
    id_user = getUserAlexa()

    id_card: int

    try:
        id_card = session.attributes['card'];
    except:
        session.attributes['card']='';


    if session.attributes['card']:
        id_card = session.attributes['card'];
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO tbcarrinho (VrTotal, IdUsuario, VrFrete, VrDesconto, VrSubTotal) VALUES (%s,%s,%s,%s,%s)"
        val = (0, id_user[1], 0, 0, 0)
        cursor.execute(sql, val)
        id_card = cursor.lastrowid
        session.attributes['card'] = id_card;
        conn.commit();

    return id_card;


def insertCard(id_ofer,qt_product,vr_product):

    id_card = getOrCreateCard()

    app.insertCardItens(id_card, id_ofer, qt_product, vr_product)



if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            hello.config['ASK_VERIFY_REQUESTS'] = False
    hello.run(debug=True)
