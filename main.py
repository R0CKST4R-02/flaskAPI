from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
from flask_session import Session

app = Flask(__name__)
app.secret_key = "3z3qui3lfr4ncisc0"

# Inicializa o Firebase Admin SDK com as credenciais baixadas
cred = credentials.Certificate('flaskPI/flaskpi-firebase-adminsdk-fbsvc-22084c00a0.json')
firebase_admin.initialize_app(cred)

# Inicializa o Firestore
db = firestore.client()

@app.route("/")
def index():
    usuarios_ref = db.collection("usuarios")
    usuarios = usuarios_ref.stream()

    users = []
    for user in usuarios:
        user_data = user.to_dict()  
        user_data["id"] = user.id   
        users.append(user_data)
    
    return render_template('index.html', usuarios=users)


@app.route("/adicionar", methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['useremail']
        data_nasc = request.form['userdata']
        contacto = request.form['usercontacto']
        password = request.form['userpassword']

        db.collection("usuarios").add({
            'nome': nome,
            'email': email,
            'data_nasc': data_nasc,
            'contacto': contacto,
            'password': password
        })
        return redirect(url_for('index'))
    return render_template('adicionar.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['useremail']
        session['user_email'] = email
        return redirect(url_for('index', user=session['user_email']))

    return render_template("login.html")

@app.route("/log-off")
def log_off():
    session.pop('user_id', None)
    return redirect(url_for("login"))

@app.route("/deletar/<user_id>")
def deletar(user_id):
    usuario_ref = db.collection("usuarios").document(user_id)
    usuario_ref.delete()
    return redirect(url_for("index"))


if __name__=="__main__":
    app.run(debug=True)