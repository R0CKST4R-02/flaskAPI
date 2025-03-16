from flask import Flask, render_template, jsonify, request, redirect, url_for, session
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
        email = request.form.get("useremail")
        password = request.form.get("userpassword")

        user_ref = db.collection("usuarios")
        user_email = user_ref.where("email", "==", email).get()
        
        if not user_email:
            return "usuario nao encontrado"
        
        user = user_email[0]
        user_data = user.to_dict()
        user_cod = user_data['password']

        # Verifica se a requisição veio do app móvel
        is_mobile = request.headers.get("App-Origin") == "KivyMD"

        if email == email and password == user_cod:
            session['user_email'] = email  # Salva o login na sessão

            if is_mobile:
                return jsonify({"success": True, "user": email, "token": "abcdef123456"})  
            
            return redirect(url_for('index'))

        else:
            if is_mobile:
                return jsonify({"success": False, "message": "Email ou senha incorretos"}), 401
            return render_template("login.html", msg="Email ou senha incorretos")  # Mostra erro no HTML

    return render_template("login.html")  # Exibe a página de login para usuários web

@app.route("/log-off")
def log_off():
    session.pop('user_id', None)
    return redirect(url_for("login"))

@app.route("/deletar/<user_id>")
def deletar(user_id):
    usuario_ref = db.collection("usuarios").document(user_id)
    usuario_ref.delete()
    return redirect(url_for("index"))

@app.route("/actualizar/<user_id>", methods=["GET", "POST"])
def actualizar(user_id):
    usuario_ref = db.collection("usuarios").document(user_id)
    usuario = usuario_ref.get()                                                                   
    usuario_id = user_id  

    if not usuario.exists:
        return f"Erro: o usuário {user_id} não foi encontrado"
    
    if request.method == "POST":
        nome = request.form.get('nome')
        contacto = request.form.get('contacto')
        password = request.form.get('password')
        data_nasc = request.form.get('data_nasc')
        email = request.form.get('email')

        dados_para_atualizar = {}

        if nome:
            dados_para_atualizar['nome'] = nome
        if email:
            dados_para_atualizar['email'] = email
        if password:
            dados_para_atualizar['password'] = password
        if data_nasc:
            dados_para_atualizar['data_nasc'] = data_nasc
        if contacto:
            dados_para_atualizar['contacto'] = contacto

        if dados_para_atualizar:
            usuario_ref.update(dados_para_atualizar)
            return redirect(url_for('index'))
        
        msg = "Nenhum dado atualizado"
        return render_template('index.html', msg=msg)

    return render_template('actualizar.html', users=usuario.to_dict(), user_id=usuario_id )

if __name__== "__main__":
    app.run(debug=True)