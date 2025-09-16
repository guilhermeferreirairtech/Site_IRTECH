from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib , os

from flask import Flask, render_template, send_from_directory

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_DIR = os.path.join(BASE_DIR, "scr")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,       # caminho ABSOLUTO para /scr
    static_url_path="/static",      # URL pública
    template_folder=TEMPLATES_DIR
)

# DEBUG: verifique se o arquivo existe do ponto de vista do Flask
print("STATIC_DIR:", STATIC_DIR)
print("Logo existe?", os.path.exists(os.path.join(STATIC_DIR, "Imagens", "IR-Tech-Logo.png")))
app.secret_key = "segredo_super_secreto"


# Função para criar banco de dados se não existir
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Página inicial (login/cadastro/alterar senha)
@app.route("/")
def index():
    return render_template("Areadoclienteteste1.html")

# Rota para cadastro
@app.route("/cadastro", methods=["POST"])
def cadastro():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = hash_senha(request.form["senha"])

    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        flash("Cadastro realizado com sucesso!", "success")
    except sqlite3.IntegrityError:
        flash("Email já cadastrado!", "error")
    conn.close()

    return redirect(url_for("index"))

# Rota para login
@app.route("/login", methods=["POST"])
def login(): 
    email = request.form["email"]
    senha = hash_senha(request.form["senha"])

    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    user = c.fetchone()
    conn.close()

    if user:
        session["user"] = user[1]  # salva nome do usuário na sessão
        flash(f"Bem-vindo, {user[1]}!", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Email ou senha incorretos!", "error")
        return redirect(url_for("index"))

# Rota para alterar senha
@app.route("/alterar_senha", methods=["POST"])
def alterar_senha():
    email = request.form["email"]
    nova_senha = hash_senha(request.form["nova_senha"])

    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE usuarios SET senha=? WHERE email=?", (nova_senha, email))
    if c.rowcount == 0:
        flash("Email não encontrado!", "error")
    else:
        conn.commit()
        flash("Senha alterada com sucesso!", "success")
    conn.close()

    return redirect(url_for("index"))

# Dashboard (página protegida após login)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("Areadoclienteteste.html", usuario=session["user"])
    else:
        flash("Você precisa estar logado para acessar essa página.", "error")
        return redirect(url_for("index"))

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Você saiu da conta.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
