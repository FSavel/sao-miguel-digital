from flask import Flask, render_template, request, redirect, session, send_file
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "saomiguel2026"

# ======================================================
# 📊 GOOGLE SHEETS CONFIGURAÇÃO
# ======================================================
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

# ======================================================
# 🔧 HELPERS (UTILITÁRIOS SHEETS)
# ======================================================
def get_worksheet(nome):
    try:
        return sheet.worksheet(nome)
    except:
        return sheet.add_worksheet(title=nome, rows="1000", cols="20")


def ler_sheet(nome):
    try:
        return get_worksheet(nome).get_all_records()
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


# ======================================================
# 🔐 CONTROLO ADMIN
# ======================================================
def admin_ok():
    return session.get("admin")


ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


# ======================================================
# 🏠 HOME
# ======================================================
@app.route("/")
def index():
    return render_template("index.html", avisos=ler_sheet("avisos"))


# ======================================================
# 🔑 LOGIN ADMIN
# ======================================================
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


# ======================================================
# 🧭 DASHBOARD ADMIN
# ======================================================
@app.route("/admin")
def admin():
    if not admin_ok():
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
# 🌐 PÁGINAS PÚBLICAS
# ======================================================
@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=ler_sheet("avisos"))


@app.route("/leituras")
def leituras():
    return render_template("leituras.html", leituras=ler_sheet("leituras"))


@app.route("/canticos")
def canticos():
    return render_template("canticos.html", canticos=ler_sheet("canticos"))


@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=ler_sheet("calendario"))


@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=ler_sheet("pedidos"))


@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=ler_sheet("acolitos"),
        leitores=ler_sheet("leitores")
    )


# ======================================================
# 💰 FINANCEIRO (ADICIONADO - RESOLVE ERRO 500)
# ======================================================
@app.route("/financeiro")
def financeiro():
    if not admin_ok():
        return redirect("/login")

    return render_template("financeiro.html")


# ======================================================
# ➕ ADD ROTAS (CRIAR DADOS)
# ======================================================
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("avisos")
    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })
    guardar_sheet("avisos", data)
    return redirect("/admin")


@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("leituras")
    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })
    guardar_sheet("leituras", data)
    return redirect("/admin")


@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("canticos")
    data.append({
        "momento": request.form["momento"],
        "cantico": request.form["cantico"],
        "letra": request.form["letra"]
    })
    guardar_sheet("canticos", data)
    return redirect("/admin")


@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("pedidos")
    data.append(request.form.to_dict())
    guardar_sheet("pedidos", data)
    return redirect("/admin")


@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("calendario")
    data.append(request.form.to_dict())
    guardar_sheet("calendario", data)
    return redirect("/admin")


# ======================================================
# ✏️ EDIT ROTAS
# ======================================================
@app.route("/edit_aviso/<int:i>", methods=["GET", "POST"])
def edit_aviso(i):
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("avisos")

    if request.method == "POST":
        data[i]["titulo"] = request.form["titulo"]
        data[i]["descricao"] = request.form["descricao"]
        guardar_sheet("avisos", data)
        return redirect("/admin")

    return render_template("edit_aviso.html", aviso=data[i], index=i)


@app.route("/edit_leitura/<int:i>", methods=["GET", "POST"])
def edit_leitura(i):
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("leituras")

    if request.method == "POST":
        data[i]["tipo"] = request.form["tipo"]
        data[i]["texto"] = request.form["texto"]
        guardar_sheet("leituras", data)
        return redirect("/admin")

    return render_template("edit_leitura.html", leitura=data[i], index=i)


@app.route("/edit_cantico/<int:i>", methods=["GET", "POST"])
def edit_cantico(i):
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("canticos")

    if request.method == "POST":
        data[i]["momento"] = request.form["momento"]
        data[i]["cantico"] = request.form["cantico"]
        data[i]["letra"] = request.form["letra"]
        guardar_sheet("canticos", data)
        return redirect("/admin")

    return render_template("edit_cantico.html", cantico=data[i], index=i)


@app.route("/edit_pedido/<int:i>", methods=["GET", "POST"])
def edit_pedido(i):
    if not admin_ok():
        return redirect("/login")

    data = ler_sheet("pedidos")

    if request.method == "POST":
        data[i]["nome"] = request.form["nome"]
        data[i]["categoria"] = request.form["categoria"]
        data[i]["pedido"] = request.form["pedido"]
        guardar_sheet("pedidos", data)
        return redirect("/admin")

    return render_template("edit_pedido.html", pedido=data[i], index=i)


# ======================================================
# 🗑 DELETE ROTAS
# ======================================================
@app.route("/delete_aviso/<int:i>")
def delete_aviso(i):
    if admin_ok():
        data = ler_sheet("avisos")
        if 0 <= i < len(data):
            data.pop(i)
            guardar_sheet("avisos", data)
    return redirect("/admin")


@app.route("/delete_leitura/<int:i>")
def delete_leitura(i):
    if admin_ok():
        data = ler_sheet("leituras")
        if 0 <= i < len(data):
            data.pop(i)
            guardar_sheet("leituras", data)
    return redirect("/admin")


@app.route("/delete_cantico/<int:i>")
def delete_cantico(i):
    if admin_ok():
        data = ler_sheet("canticos")
        if 0 <= i < len(data):
            data.pop(i)
            guardar_sheet("canticos", data)
    return redirect("/admin")


@app.route("/delete_pedido/<int:i>")
def delete_pedido(i):
    if admin_ok():
        data = ler_sheet("pedidos")
        if 0 <= i < len(data):
            data.pop(i)
            guardar_sheet("pedidos", data)
    return redirect("/admin")


# ======================================================
# 🚀 RUN (RENDER READY)
# ======================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
