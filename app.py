from flask import Flask, render_template, request, redirect, session
import os
import json
import gspread

app = Flask(__name__)
app.secret_key = "saomiguel2026"

ADMIN_USER = "Padre"
ADMIN_PASS = "1234"

# =========================
# GOOGLE SHEETS CONFIG
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)

gc = gspread.service_account_from_dict(creds_dict)

SHEET_ID = "1AZaKlDN1rVg5hbFKh69YffISFt5TcnyVArJFOWhBoeA"
sheet = gc.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")


# =========================
# UTILITÁRIO SHEETS
# =========================

def ler_sheet(nome):
    try:
        ws = sheet.worksheet(nome)
        data = ws.get_all_records()
        return data
    except:
        return []


def guardar_sheet(nome, data):
    ws = sheet.worksheet(nome)
    ws.clear()

    if len(data) > 0:
        ws.update([list(data[0].keys())] + [list(i.values()) for i in data])


# =========================
# HOME (BANNER ROTATIVO)
# =========================
@app.route("/")
def index():
    avisos = ler_sheet("avisos")

    # últimos 5 avisos para rotação
    avisos_rotativos = avisos[-5:] if len(avisos) > 5 else avisos

    return render_template(
        "index.html",
        avisos=avisos,
        avisos_rotativos=avisos_rotativos
    )


# =========================
# LOGIN
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


# =========================
# AVISOS
# =========================
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


# =========================
# LEITURAS
# =========================
@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    data = ler_sheet("leituras")

    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })

    guardar_sheet("leituras", data)
    return redirect("/admin")


@app.route("/delete_leitura/<int:index>")
def delete_leitura(index):
    data = ler_sheet("leituras")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("leituras", data)
    return redirect("/admin")


# =========================
# CÂNTICOS
# =========================
@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    data = ler_sheet("canticos")

    data.append({
        "momento": request.form["momento"],
        "cantico": request.form["cantico"],
        "letra": request.form["letra"]
    })

    guardar_sheet("canticos", data)
    return redirect("/admin")


@app.route("/delete_cantico/<int:index>")
def delete_cantico(index):
    data = ler_sheet("canticos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("canticos", data)
    return redirect("/admin")


# =========================
# ACÓLITOS
# =========================
@app.route("/add_acolito", methods=["POST"])
def add_acolito():
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


@app.route("/delete_acolito/<int:index>")
def delete_acolito(index):
    data = ler_sheet("acolitos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("acolitos", data)
    return redirect("/admin")


# =========================
# LEITORES
# =========================
@app.route("/add_leitor", methods=["POST"])
def add_leitor():
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


@app.route("/delete_leitor/<int:index>")
def delete_leitor(index):
    data = ler_sheet("leitores")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("leitores", data)
    return redirect("/admin")


# =========================
# CALENDÁRIO
# =========================
@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    data = ler_sheet("calendario")

    data.append({
        "evento": request.form["evento"],
        "data": request.form["data"],
        "descricao": request.form["descricao"]
    })

    guardar_sheet("calendario", data)
    return redirect("/admin")


@app.route("/delete_calendario/<int:index>")
def delete_calendario(index):
    data = ler_sheet("calendario")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("calendario", data)
    return redirect("/admin")


# =========================
# PEDIDOS
# =========================
@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    data = ler_sheet("pedidos")

    data.append({
        "nome": request.form["nome"],
        "categoria": request.form["categoria"],
        "pedido": request.form["pedido"]
    })

    guardar_sheet("pedidos", data)
    return redirect("/admin")


@app.route("/delete_pedido/<int:index>")
def delete_pedido(index):
    data = ler_sheet("pedidos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("pedidos", data)
    return redirect("/admin")


# =========================
# ESCALAS
# =========================
@app.route("/escalas")
def escalas():
    return render_template(
        "escalas.html",
        acolitos=ler_sheet("acolitos"),
        leitores=ler_sheet("leitores")
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
