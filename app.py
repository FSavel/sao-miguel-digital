from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# =========================
# PDF
# =========================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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
# 🔷 DIZIMISTA
# ======================================================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None

    if request.method == "POST":
        numero = str(request.form["numero"]).strip()
        password = str(request.form["password"]).strip()

        dizimistas = ler_sheet("dizimistas")

        user = None

        for d in dizimistas:
            if str(d.get("numero", "")).strip() == numero and str(d.get("password", "")).strip() == password:
                user = d
                break

        if user:
            session["dizimista"] = numero
            return redirect("/dizimista_dashboard")
        else:
            erro = "Número ou palavra-passe inválidos"

    return render_template("dizimista_login.html", erro=erro)


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")


@app.route("/dizimista_dashboard")
def dizimista_dashboard():

    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = str(session["dizimista"]).strip()

    dizimistas = ler_sheet("dizimistas")
    contribuicoes = ler_sheet("contribuicoes")

    user = None

    for d in dizimistas:
        if str(d.get("numero", "")).strip() == numero:
            user = d
            break

    minhas = [
        c for c in contribuicoes
        if str(c.get("numero", "")).strip() == numero
    ]

    return render_template(
        "dizimista_dashboard.html",
        user=user,
        contribuicoes=minhas
    )


# =========================
# PDF EXPORT
# =========================
@app.route("/export_extrato_pdf")
def export_extrato_pdf():

    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = str(session["dizimista"]).strip()

    dizimistas = ler_sheet("dizimistas")
    contribuicoes = ler_sheet("contribuicoes")

    user = None

    for d in dizimistas:
        if str(d.get("numero", "")).strip() == numero:
            user = d
            break

    minhas = [
        c for c in contribuicoes
        if str(c.get("numero", "")).strip() == numero
    ]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    largura, altura = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altura - 60, "PARÓQUIA SÃO MIGUEL ARCANJO")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, altura - 80, "Extrato de Contribuições")

    pdf.drawString(50, altura - 100, f"Nome: {user.get('nome','')}")
    pdf.drawString(50, altura - 120, f"Número: {numero}")
    pdf.drawString(50, altura - 140, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = altura - 180
    total = 0

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "DATA")
    pdf.drawString(150, y, "VALOR")
    pdf.drawString(250, y, "DESCRIÇÃO")

    y -= 20
    pdf.setFont("Helvetica", 10)

    for c in minhas:
        data = c.get("data", "")
        valor = float(c.get("valor", 0))
        desc = c.get("descricao", "")

        pdf.drawString(50, y, str(data))
        pdf.drawString(150, y, f"{valor} MZN")
        pdf.drawString(250, y, str(desc))

        total += valor
        y -= 20

        if y < 80:
            pdf.showPage()
            y = altura - 60

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 20, f"TOTAL: {total} MZN")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y - 50, "Obrigado pela sua contribuição 🙏")

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="extrato.pdf", mimetype="application/pdf")


# =========================
# =========================
# 🔥 ROTAS DE EDIÇÃO RESTAURADAS
# =========================
# =========================

def admin_required():
    return session.get("admin")


# ---------- AVISOS ----------
@app.route("/edit_aviso/<int:index>", methods=["GET", "POST"])
def edit_aviso(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("avisos")

    if index < 0 or index >= len(data):
        return redirect("/admin")

    if request.method == "POST":
        data[index]["titulo"] = request.form["titulo"]
        data[index]["descricao"] = request.form["descricao"]
        guardar_sheet("avisos", data)
        return redirect("/admin")

    return render_template("edit_aviso.html", aviso=data[index], index=index)


@app.route("/delete_aviso/<int:index>")
def delete_aviso(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("avisos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("avisos", data)
    return redirect("/admin")


# ---------- LEITURAS ----------
@app.route("/edit_leitura/<int:index>", methods=["GET", "POST"])
def edit_leitura(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("leituras")

    if request.method == "POST":
        data[index]["tipo"] = request.form["tipo"]
        data[index]["texto"] = request.form["texto"]
        guardar_sheet("leituras", data)
        return redirect("/admin")

    return render_template("edit_leitura.html", leitura=data[index], index=index)


@app.route("/delete_leitura/<int:index>")
def delete_leitura(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("leituras")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("leituras", data)
    return redirect("/admin")


# ---------- CÂNTICOS ----------
@app.route("/edit_cantico/<int:index>", methods=["GET", "POST"])
def edit_cantico(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("canticos")

    if request.method == "POST":
        data[index]["momento"] = request.form["momento"]
        data[index]["cantico"] = request.form["cantico"]
        data[index]["letra"] = request.form["letra"]
        guardar_sheet("canticos", data)
        return redirect("/admin")

    return render_template("edit_cantico.html", cantico=data[index], index=index)


@app.route("/delete_cantico/<int:index>")
def delete_cantico(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("canticos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("canticos", data)
    return redirect("/admin")


# ---------- PEDIDOS ----------
@app.route("/edit_pedido/<int:index>", methods=["GET", "POST"])
def edit_pedido(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("pedidos")

    if request.method == "POST":
        data[index]["nome"] = request.form["nome"]
        data[index]["categoria"] = request.form["categoria"]
        data[index]["pedido"] = request.form["pedido"]
        guardar_sheet("pedidos", data)
        return redirect("/admin")

    return render_template("edit_pedido.html", pedido=data[index], index=index)


@app.route("/delete_pedido/<int:index>")
def delete_pedido(index):
    if not admin_required():
        return redirect("/login")

    data = ler_sheet("pedidos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("pedidos", data)
    return redirect("/admin")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
