from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
import gspread
from google.oauth2.service_account import Credentials

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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

creds_dict = json.loads(creds_json)

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")

# =========================
# UTILITÁRIOS
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

    if not lista:
        return

    headers = list(lista[0].keys())
    ws.append_row(headers)

    for item in lista:
        ws.append_row([item.get(h, "") for h in headers])


def admin_required():
    return session.get("admin")


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
    if not admin_required():
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


# =========================
# 🔥 ADD ROTAS (RESTO FECHADO)
# =========================

# ---------- AVISOS ----------
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("avisos")

    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })

    guardar_sheet("avisos", data)
    return redirect("/admin")


# ---------- LEITURAS ----------
@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("leituras")

    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })

    guardar_sheet("leituras", data)
    return redirect("/admin")


# ---------- CÂNTICOS ----------
@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("canticos")

    data.append({
        "momento": request.form["momento"],
        "cantico": request.form["cantico"],
        "letra": request.form["letra"]
    })

    guardar_sheet("canticos", data)
    return redirect("/admin")


# ---------- ACÓLITOS ----------
@app.route("/add_acolito", methods=["POST"])
def add_acolito():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("acolitos")

    data.append({
        "cruciferario": request.form["cruciferario"],
        "turiferario": request.form["turiferario"],
        "naveteiro": request.form["naveteiro"],
        "cerimoniario": request.form["cerimoniario"],
        "velas": request.form["velas"],
        "missal": request.form["missal"],
        "campainha": request.form["campainha"]
    })

    guardar_sheet("acolitos", data)
    return redirect("/admin")


# ---------- LEITORES ----------
@app.route("/add_leitor", methods=["POST"])
def add_leitor():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("leitores")

    data.append({
        "primeira_pt": request.form["primeira_pt"],
        "primeira_ch": request.form["primeira_ch"],
        "salmo": request.form["salmo"],
        "segunda_pt": request.form["segunda_pt"],
        "segunda_ch": request.form["segunda_ch"],
        "oracao_fieis": request.form["oracao_fieis"]
    })

    guardar_sheet("leitores", data)
    return redirect("/admin")


# ---------- PEDIDOS ----------
@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("pedidos")

    data.append({
        "nome": request.form["nome"],
        "categoria": request.form["categoria"],
        "pedido": request.form["pedido"]
    })

    guardar_sheet("pedidos", data)
    return redirect("/admin")


# ---------- CALENDÁRIO ----------
@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("calendario")

    data.append({
        "evento": request.form["evento"],
        "data": request.form["data"],
        "descricao": request.form["descricao"]
    })

    guardar_sheet("calendario", data)
    return redirect("/admin")


# =========================
# PDF (mantido)
# =========================
@app.route("/export_extrato_pdf")
def export_extrato_pdf():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    dizimistas = ler_sheet("dizimistas")
    contribuicoes = ler_sheet("contribuicoes")

    user = next((d for d in dizimistas if d.get("numero") == numero), None)

    minhas = [c for c in contribuicoes if c.get("numero") == numero]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    altura = A4[1]

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altura - 60, "PARÓQUIA SÃO MIGUEL ARCANJO")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, altura - 80, "Extrato de Contribuições")

    pdf.drawString(50, altura - 100, f"Nome: {user.get('nome','') if user else ''}")
    pdf.drawString(50, altura - 120, f"Número: {numero}")

    pdf.drawString(50, altura - 140,
                   f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = altura - 180
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
