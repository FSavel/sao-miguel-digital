from flask import Flask, render_template, request, redirect, session
import os
import json
import gspread
from google.oauth2.service_account import Credentials

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
creds = Credentials.from_service_account_info(
    json.loads(creds_json),
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado")

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
# DIZIMISTA LOGIN (ADICIONADO)
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


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")
# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html", avisos=read("avisos"))


# =========================
# ADMIN
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
# PÁGINAS
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
# ESCALAS - ACÓLITOS (FIX CRÍTICO)
# =========================
@app.route("/add_acolito", methods=["POST"])
def add_acolito():
    data = read("acolitos")
    data.append(request.form.to_dict())
    save("acolitos", data)
    return redirect("/admin")


@app.route("/delete_acolito/<int:i>")
def delete_acolito(i):
    data = read("acolitos")
    if i < len(data):
        data.pop(i)
        save("acolitos", data)
    return redirect("/admin")


# =========================
# ESCALAS - LEITORES (FIX CRÍTICO)
# =========================
@app.route("/add_leitor", methods=["POST"])
def add_leitor():
    data = read("leitores")
    data.append(request.form.to_dict())
    save("leitores", data)
    return redirect("/admin")


@app.route("/delete_leitor/<int:i>")
def delete_leitor(i):
    data = read("leitores")
    if i < len(data):
        data.pop(i)
        save("leitores", data)
    return redirect("/admin")


# =========================
# CRUD RESTO (MANTIDO)
# =========================
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    data = read("avisos")
    data.append(request.form.to_dict())
    save("avisos", data)
    return redirect("/admin")
