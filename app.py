from flask import Flask, render_template, request, redirect, session
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "saomiguel2026"

# =========================
# GOOGLE SHEETS CONFIG
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

creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")

# =========================
# UTILITÁRIO GOOGLE SHEETS
# =========================
def get_worksheet(nome):
    try:
        return sheet.worksheet(nome)
    except:
        return sheet.add_worksheet(title=nome, rows="1000", cols="20")


def ler_sheet(nome):
    try:
        ws = get_worksheet(nome)
        return ws.get_all_records()
    except:
        return []


def guardar_sheet(nome, lista):
    ws = get_worksheet(nome)
    ws.clear()

    if len(lista) == 0:
        return

    headers = list(lista[0].keys())
    ws.append_row(headers)

    for item in lista:
        ws.append_row([item.get(h, "") for h in headers])


# =========================
# APP
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


@app.route("/")
def index():
    return render_template("index.html", avisos=ler_sheet("avisos"))


# =========================
# LOGIN ADMIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        else:
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
    if not session.get("admin"):
        return redirect("/login")

    return render_template(
        "admin.html",
        avisos=ler_sheet("avisos"),
        leituras=ler_sheet("leituras"),
        canticos=ler_sheet("canticos"),
        acolitos=ler_sheet("acolitos"),
        leitores=ler_sheet("leitores"),
        calendario=ler_sheet("calendario"),
        pedidos=ler_sheet("pedidos")
    )


# ======================================================
# 🔷 MÓDULO DIZIMISTA (NOVO - ADICIONADO)
# ======================================================

@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None

    if request.method == "POST":
        numero = request.form["numero"]
        password = request.form["password"]

        dizimistas = ler_sheet("dizimistas")

        user = None
        for d in dizimistas:
            if str(d.get("numero")) == str(numero) and d.get("password") == password:
                user = d
                break

        if user:
            session["dizimista"] = numero
            return redirect("/dizimista_dashboard")
        else:
            erro = "Número ou palavra-passe inválidos"

    return render_template("dizimista_login.html", erro=erro)


@app.route("/dizimista_dashboard")
def dizimista_dashboard():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    dizimistas = ler_sheet("dizimistas")
    contribuicoes = ler_sheet("contribuicoes")

    user = None
    for d in dizimistas:
        if str(d.get("numero")) == str(numero):
            user = d
            break

    minhas = [
        c for c in contribuicoes if str(c.get("numero")) == str(numero)
    ]

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
# PÁGINAS
# =========================
@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=ler_sheet("avisos"))

@app.route("/leituras")
def leituras():
    return render_template("leituras.html", leituras=ler_sheet("leituras"))

@app.route("/canticos")
def canticos():
    return render_template("canticos.html", canticos=ler_sheet("canticos"))

@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=ler_sheet("pedidos"))

@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=ler_sheet("calendario"))

@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=ler_sheet("acolitos"),
        leitores=ler_sheet("leitores")
    )


# =========================
# (RESTO DO TEU CÓDIGO - SEM ALTERAÇÕES)
# =========================
# AVISOS
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    data = ler_sheet("avisos")
    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })
    guardar_sheet("avisos", data)
    return redirect("/admin")


@app.route("/delete_aviso/<int:index>")
def delete_aviso(index):
    data = ler_sheet("avisos")
    if 0 <= index < len(data):
        data.pop(index)
    guardar_sheet("avisos", data)
    return redirect("/admin")


# (TODAS AS TUAS OUTRAS ROTAS FICAM IGUAIS)
# =========================

if __name__ == "__main__":
    app.run(debug=True)
