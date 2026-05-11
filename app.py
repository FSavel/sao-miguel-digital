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
# ADMIN CREDENTIALS
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
# LOGIN
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
# ADMIN DASHBOARD
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


# ======================================================
# 🔥 ROTAS PÚBLICAS (CORRIGEM OS 404)
# ======================================================

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
# ADD ROTAS
# =========================

@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    if not admin_ok():
        return redirect("/login")

    data = read("avisos")
    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })
    save("avisos", data)
    return redirect("/admin")


@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    if not admin_ok():
        return redirect("/login")

    data = read("leituras")
    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })
    save("leituras", data)
    return redirect("/admin")


@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    if not admin_ok():
        return redirect("/login")

    data = read("canticos")
    data.append({
        "momento": request.form["momento"],
        "cantico": request.form["cantico"],
        "letra": request.form["letra"]
    })
    save("canticos", data)
    return redirect("/admin")


@app.route("/add_acolito", methods=["POST"])
def add_acolito():
    if not admin_ok():
        return redirect("/login")

    data = read("acolitos")
    data.append(request.form.to_dict())
    save("acolitos", data)
    return redirect("/admin")


@app.route("/add_leitor", methods=["POST"])
def add_leitor():
    if not admin_ok():
        return redirect("/login")

    data = read("leitores")
    data.append(request.form.to_dict())
    save("leitores", data)
    return redirect("/admin")


@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    if not admin_ok():
        return redirect("/login")

    data = read("pedidos")
    data.append(request.form.to_dict())
    save("pedidos", data)
    return redirect("/admin")


@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    if not admin_ok():
        return redirect("/login")

    data = read("calendario")
    data.append(request.form.to_dict())
    save("calendario", data)
    return redirect("/admin")


# =========================
# EDIT ROTAS
# =========================

@app.route("/edit_aviso/<int:i>", methods=["GET", "POST"])
def edit_aviso(i):
    if not admin_ok():
        return redirect("/login")

    data = read("avisos")

    if request.method == "POST":
        data[i]["titulo"] = request.form["titulo"]
        data[i]["descricao"] = request.form["descricao"]
        save("avisos", data)
        return redirect("/admin")

    return render_template("edit_aviso.html", aviso=data[i], index=i)


@app.route("/edit_leitura/<int:i>", methods=["GET", "POST"])
def edit_leitura(i):
    if not admin_ok():
        return redirect("/login")

    data = read("leituras")

    if request.method == "POST":
        data[i]["tipo"] = request.form["tipo"]
        data[i]["texto"] = request.form["texto"]
        save("leituras", data)
        return redirect("/admin")

    return render_template("edit_leitura.html", leitura=data[i], index=i)


@app.route("/edit_cantico/<int:i>", methods=["GET", "POST"])
def edit_cantico(i):
    if not admin_ok():
        return redirect("/login")

    data = read("canticos")

    if request.method == "POST":
        data[i]["momento"] = request.form["momento"]
        data[i]["cantico"] = request.form["cantico"]
        data[i]["letra"] = request.form["letra"]
        save("canticos", data)
        return redirect("/admin")

    return render_template("edit_cantico.html", cantico=data[i], index=i)


@app.route("/edit_pedido/<int:i>", methods=["GET", "POST"])
def edit_pedido(i):
    if not admin_ok():
        return redirect("/login")

    data = read("pedidos")

    if request.method == "POST":
        data[i]["nome"] = request.form["nome"]
        data[i]["categoria"] = request.form["categoria"]
        data[i]["pedido"] = request.form["pedido"]
        save("pedidos", data)
        return redirect("/admin")

    return render_template("edit_pedido.html", pedido=data[i], index=i)


# =========================
# DELETE ROTAS
# =========================

@app.route("/delete_aviso/<int:i>")
def delete_aviso(i):
    if admin_ok():
        data = read("avisos")
        data.pop(i)
        save("avisos", data)
    return redirect("/admin")


@app.route("/delete_leitura/<int:i>")
def delete_leitura(i):
    if admin_ok():
        data = read("leituras")
        data.pop(i)
        save("leituras", data)
    return redirect("/admin")


@app.route("/delete_cantico/<int:i>")
def delete_cantico(i):
    if admin_ok():
        data = read("canticos")
        data.pop(i)
        save("canticos", data)
    return redirect("/admin")


@app.route("/delete_pedido/<int:i>")
def delete_pedido(i):
    if admin_ok():
        data = read("pedidos")
        data.pop(i)
        save("pedidos", data)
    return redirect("/admin")


# =========================
# PDF DIZIMISTA
# =========================
@app.route("/export_extrato_pdf")
def export_pdf():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    diz = read("dizimistas")
    cont = read("contribuicoes")

    user = next((d for d in diz if d.get("numero") == numero), None)
    minhas = [c for c in cont if c.get("numero") == numero]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    h = A4[1]

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, h - 60, "PARÓQUIA SÃO MIGUEL ARCANJO")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, h - 80, "Extrato de Contribuições")

    pdf.drawString(50, h - 100, f"Nome: {user.get('nome','') if user else ''}")
    pdf.drawString(50, h - 120, f"Número: {numero}")

    pdf.drawString(50, h - 140, f"Data: {datetime.now()}")

    y = h - 180
    total = 0

    for c in minhas:
        pdf.drawString(50, y, str(c.get("data", "")))
        pdf.drawString(150, y, str(c.get("valor", "")))
        pdf.drawString(250, y, str(c.get("descricao", "")))
        total += float(c.get("valor", 0))
        y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 20, f"TOTAL: {total} MZN")

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, download_name="extrato.pdf", as_attachment=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
