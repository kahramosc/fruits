from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'frutas123'
app.config['MYSQL_DATABASE_DB'] = 'frutas'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/card')
def card():
    return render_template('card.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/details')
def details():
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        id = request.args.get('id')

        cursor.execute(
            "SELECT IdProduto,DsNome,IdCategoria,VrProduto,VrDimensao,VrPeso,DsProduto,NmRaiting,DsPorcao,DsImagem FROM tbproduto WHERE IdProduto=%s",
            id)
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
            "SELECT IdProduto,DsNome,IdCategoria,VrProduto,VrDimensao,VrPeso,DsProduto,NmRaiting,DsPorcao,DsImagem FROM tbproduto")
        produtos = cursor.fetchall();

        return render_template('list.html', produtos=produtos)

    except Exception as e:
        return render_template('erro.html')
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(port=5002)
