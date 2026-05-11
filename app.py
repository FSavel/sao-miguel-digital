from flask import Flask, render_template, request, redirect, session
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# =========================
# APP INIT
# =========================
app = Flask(__name__)
app.secret_key = "saomiguel2026"

# =========================
# GOOGLE SHEETS
# =========================
SHEET_ID = "1AZaKlDN1rVg5hbFKh69YffISFt5TcnyVArJFOWhBoeA"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    raise Exception("GOOGLE_CREDENTIALS não encontrada")

creds = Credentials.from_service_account_info(
    json.loads(creds_json),
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")

# =========================
# HELPERS
# =========================
def ws(name):
    try:
        return sheet.worksheet(name)
    except:
        return sheet.add_worksheet(title=name, rows="1000", cols="20")

def read(name):
    try:
        return ws(name).get_all_records()
    except:
        return []

def save(name, data):
    w = ws(name)
    w.clear()

    if not data:
        return

    headers = list(data[0].keys())
    w.append_row(headers)

    for r in data:
        w.append_row([r.get(h, "") for h in headers])

def is_admin():
    return session.get("admin")


# =========================
# LOGIN ADMIN
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        erro = "Credenciais inválidas"

    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html", avisos=read("avisos"))


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    if not is_admin():
        return redirect("/login")

    return render_template(
        "admin.html",
        avisos=read("avisos"),
        leituras=read("leituras"),
        canticos=read("canticos"),
        pedidos=read("pedidos"),
        calendario=read("calendario"),
        acolitos=read("acolitos"),
        leitores=read("leitores")
    )


# =========================
# PÁGINAS PÚBLICAS
# =========================
@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=read("avisos"))

@app.route("/leituras")
def leituras():
    return render_template("leituras.html", leituras=read("leituras"))

@app.route("/canticos")
def canticos():
    return render_template("canticos.html", canticos=read("canticos"))

@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=read("pedidos"))

@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=read("calendario"))

@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=read("acolitos"),
        leitores=read("leitores")
    )

@app.route("/financeiro")
def financeiro():
    return render_template("financeiro.html")


# =========================
# DIZIMISTA (FIX COMPLETO)
# =========================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None

    if request.method == "POST":
        numero = request.form["numero"]
        password = request.form["password"]

        for d in read("dizimistas"):
            if str(d.get("numero")) == str(numero) and str(d.get("password")) == str(password):
                session["dizimista"] = numero
                return redirect("/dizimista_dashboard")

        erro = "Credenciais inválidas"

    return render_template("dizimista_login.html", erro=erro)


@app.route("/dizimista_dashboard")
def dizimista_dashboard():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    user = None
    for d in read("dizimistas"):
        if str(d.get("numero")) == str(numero):
            user = d
            break

    contrib = [
        c for c in read("contribuicoes")
        if str(c.get("numero")) == str(numero)
    ]

    return render_template(
        "dizimista_dashboard.html",
        user=user,
        contribuicoes=contrib
    )


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")


# =========================
# CRUD AVISOS
# =========================
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    data = read("avisos")
    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })
    save("avisos", data)
    return redirect("/admin")


@app.route("/delete_aviso/<int:i>")
def delete_aviso(i):
    data = read("avisos")
    if i < len(data):
        data.pop(i)
        save("avisos", data)
    return redirect("/admin")


@app.route("/edit_aviso/<int:i>", methods=["GET", "POST"])
def edit_aviso(i):
    data = read("avisos")

    if request.method == "POST":
        data[i] = {
            "titulo": request.form["titulo"],
            "descricao": request.form["descricao"]
        }
        save("avisos", data)
        return redirect("/admin")

    return render_template("edit_aviso.html", aviso=data[i], index=i)


# =========================
# CRUD LEITURAS
# =========================
@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    data = read("leituras")
    data.append(request.form.to_dict())
    save("leituras", data)
    return redirect("/admin")


@app.route("/delete_leitura/<int:i>")
def delete_leitura(i):
    data = read("leituras")
    if i < len(data):
        data.pop(i)
        save("leituras", data)
    return redirect("/admin")


@app.route("/edit_leitura/<int:i>", methods=["GET", "POST"])
def edit_leitura(i):
    data = read("leituras")

    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("leituras", data)
        return redirect("/admin")

    return render_template("edit_leitura.html", leitura=data[i], index=i)


# =========================
# CRUD CÂNTICOS
# =========================
@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    data = read("canticos")
    data.append(request.form.to_dict())
    save("canticos", data)
    return redirect("/admin")


@app.route("/delete_cantico/<int:i>")
def delete_cantico(i):
    data = read("canticos")
    if i < len(data):
        data.pop(i)
        save("canticos", data)
    return redirect("/admin")


@app.route("/edit_cantico/<int:i>", methods=["GET", "POST"])
def edit_cantico(i):
    data = read("canticos")

    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("canticos", data)
        return redirect("/admin")

    return render_template("edit_cantico.html", cantico=data[i], index=i)


# =========================
# CRUD PEDIDOS
# =========================
@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    data = read("pedidos")
    data.append(request.form.to_dict())
    save("pedidos", data)
    return redirect("/admin")


@app.route("/delete_pedido/<int:i>")
def delete_pedido(i):
    data = read("pedidos")
    if i < len(data):
        data.pop(i)
        save("pedidos", data)
    return redirect("/admin")


@app.route("/edit_pedido/<int:i>", methods=["GET", "POST"])
def edit_pedido(i):
    data = read("pedidos")

    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("pedidos", data)
        return redirect("/admin")

    return render_template("edit_pedido.html", pedido=data[i], index=i)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
