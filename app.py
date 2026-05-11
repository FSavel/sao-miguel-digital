from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
import gspread
from google.oauth2.service_account import Credentials

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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
    raise Exception("GOOGLE_CREDENTIALS não encontrada no Render")

creds_dict = json.loads(creds_json)

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")

# =========================
# HELPERS
# =========================
def get_ws(name):
    try:
        return sheet.worksheet(name)
    except:
        return sheet.add_worksheet(title=name, rows="1000", cols="20")


def read(name):
    try:
        return get_ws(name).get_all_records()
    except:
        return []


def save(name, data):
    ws = get_ws(name)
    ws.clear()

    if not data:
        return

    headers = list(data[0].keys())
    ws.append_row(headers)

    for row in data:
        ws.append_row([row.get(h, "") for h in headers])


def admin_ok():
    return session.get("admin")


# =========================
# ADMIN LOGIN
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html", avisos=read("avisos"))


# =========================
# LOGIN ADMIN
# =========================
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
    session.pop("admin", None)
    return redirect("/")


# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():
    if not admin_ok():
        return redirect("/login")

    return render_template(
        "admin.html",
        avisos=read("avisos"),
        leituras=read("leituras"),
        canticos=read("canticos"),
        acolitos=read("acolitos"),
        leitores=read("leitores"),
        calendario=read("calendario"),
        pedidos=read("pedidos")
    )


# =========================
# ESCALAS (FIX DO 404)
# =========================
@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=read("acolitos"),
        leitores=read("leitores")
    )


# =========================
# DIZIMISTA (FIX DO 404 CRÍTICO)
# =========================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None

    if request.method == "POST":
        numero = request.form["numero"]
        password = request.form["password"]

        diz = read("dizimistas")

        for d in diz:
            if str(d.get("numero")) == str(numero) and str(d.get("password")) == str(password):
                session["dizimista"] = numero
                return redirect("/dizimista_dashboard")

        erro = "Dados inválidos"

    return render_template("dizimista_login.html", erro=erro)


@app.route("/dizimista_dashboard")
def dizimista_dashboard():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    diz = read("dizimistas")
    cont = read("contribuicoes")

    user = next((d for d in diz if str(d.get("numero")) == str(numero)), None)

    minhas = [c for c in cont if str(c.get("numero")) == str(numero)]

    return render_template(
        "dizimista_dashboard.html",
        user=user,
        contribuicoes=minhas
    )


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")


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


@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=read("calendario"))


@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=read("pedidos"))


@app.route("/financeiro")
def financeiro():
    return render_template("financeiro.html")


# =========================
# AVISOS CRUD
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
# LEITURAS CRUD
# =========================
@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    data = read("leituras")
    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })
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
        data[i] = {
            "tipo": request.form["tipo"],
            "texto": request.form["texto"]
        }
        save("leituras", data)
        return redirect("/admin")

    return render_template("edit_leitura.html", leitura=data[i], index=i)


# =========================
# CÂNTICOS CRUD
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
# PEDIDOS CRUD
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
