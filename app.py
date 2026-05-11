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

    for row in data:
        w.append_row([row.get(h, "") for h in headers])


def admin_ok():
    return session.get("admin") is True


# =========================
# LOGIN ADMIN
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


@app.route("/")
def index():
    return render_template("index.html", avisos=read("avisos"))


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u == ADMIN_USER and p == ADMIN_PASS:
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
# 🔥 ROTAS PÚBLICAS (FIX 404)
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


@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=read("acolitos"),
        leitores=read("leitores")
    )


@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=read("calendario"))


@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html")


@app.route("/financeiro")
def financeiro():
    return render_template("financeiro.html")


# =========================
# DIZIMISTA
# =========================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None

    if request.method == "POST":
        numero = request.form["numero"]
        password = request.form["password"]

        data = read("dizimistas")

        user = next(
            (d for d in data if str(d.get("numero")) == numero and str(d.get("password")) == password),
            None
        )

        if user:
            session["dizimista"] = numero
            return redirect("/dizimista_dashboard")
        else:
            erro = "Credenciais inválidas"

    return render_template("dizimista_login.html", erro=erro)


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")


@app.route("/dizimista_dashboard")
def dizimista_dashboard():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    diz = read("dizimistas")
    cont = read("contribuicoes")

    user = next((d for d in diz if str(d.get("numero")) == numero), None)

    minhas = [c for c in cont if str(c.get("numero")) == numero]

    return render_template(
        "dizimista_dashboard.html",
        user=user,
        contribuicoes=minhas
    )


# =========================
# PDF
# =========================
@app.route("/export_extrato_pdf")
def export_extrato_pdf():

    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    diz = read("dizimistas")
    cont = read("contribuicoes")

    user = next((d for d in diz if str(d.get("numero")) == numero), None)
    minhas = [c for c in cont if str(c.get("numero")) == numero]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    h = A4[1]

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, h - 60, "PARÓQUIA SÃO MIGUEL ARCANJO")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, h - 80, "Extrato de Contribuições")

    pdf.drawString(50, h - 100, f"Nome: {user.get('nome','') if user else ''}")
    pdf.drawString(50, h - 120, f"Número: {numero}")
    pdf.drawString(50, h - 140, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = h - 180
    total = 0

    for c in minhas:
        pdf.drawString(50, y, str(c.get("data", "")))
        pdf.drawString(150, y, f"{c.get('valor',0)} MZN")
        pdf.drawString(250, y, str(c.get("descricao", "")))
        total += float(c.get("valor", 0))
        y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 20, f"TOTAL: {total} MZN")

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="extrato.pdf", mimetype="application/pdf")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
