from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "saomiguel2026"

EXCEL_FILE = "paroquia.xlsx"

ADMIN_USER = "padre"
ADMIN_PASS = "1234"


# =========================
# UTILITÁRIO GERAL
# =========================
def ler_sheet(nome):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=nome)
        df = df.fillna("")
        return df.to_dict(orient="records")
    except:
        return []


def guardar_sheet(nome, lista):
    df = pd.DataFrame(lista)

    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name=nome, index=False)


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


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# =========================
# PÁGINA INICIAL
# =========================
@app.route("/")
def index():
    return render_template("index.html")


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
@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=ler_sheet("avisos"))


@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("avisos")

    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })

    guardar_sheet("avisos", data)
    return redirect("/admin")


@app.route("/delete_aviso/<int:index>")
def delete_aviso(index):
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("avisos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("avisos", data)
    return redirect("/admin")


# =========================
# LEITURAS
# =========================
@app.route("/leituras")
def leituras():
    return render_template("leituras.html", leituras=ler_sheet("leituras"))


@app.route("/add_leitura", methods=["POST"])
def add_leitura():
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("leituras")

    data.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })

    guardar_sheet("leituras", data)
    return redirect("/admin")


@app.route("/delete_leitura/<int:index>")
def delete_leitura(index):
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("leituras")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("leituras", data)
    return redirect("/admin")


# =========================
# CÂNTICOS
# =========================
@app.route("/canticos")
def canticos():
    return render_template("canticos.html", canticos=ler_sheet("canticos"))


@app.route("/add_cantico", methods=["POST"])
def add_cantico():
    if not session.get("admin"):
        return redirect("/login")

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
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("canticos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("canticos", data)
    return redirect("/admin")


# =========================
# ACÓLITOS
# =========================
@app.route("/acolitos")
def acolitos():
    return render_template("acolitos.html", acolitos=ler_sheet("acolitos"))


@app.route("/add_acolito", methods=["POST"])
def add_acolito():
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("acolitos")

    data.append({
        "funcao": request.form["funcao"],
        "nome": request.form["nome"]
    })

    guardar_sheet("acolitos", data)
    return redirect("/admin")


@app.route("/delete_acolito/<int:index>")
def delete_acolito(index):
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("acolitos")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("acolitos", data)
    return redirect("/admin")


# =========================
# LEITORES
# =========================
@app.route("/leitores")
def leitores():
    return render_template("leitores.html", leitores=ler_sheet("leitores"))


@app.route("/add_leitor", methods=["POST"])
def add_leitor():
    if not session.get("admin"):
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


@app.route("/delete_leitor/<int:index>")
def delete_leitor(index):
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("leitores")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("leitores", data)
    return redirect("/admin")


# =========================
# CALENDÁRIO
# =========================
@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=ler_sheet("calendario"))


@app.route("/add_calendario", methods=["POST"])
def add_calendario():
    if not session.get("admin"):
        return redirect("/login")

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
    if not session.get("admin"):
        return redirect("/login")

    data = ler_sheet("calendario")

    if 0 <= index < len(data):
        data.pop(index)

    guardar_sheet("calendario", data)
    return redirect("/admin")


# =========================
# PEDIDOS DE ORAÇÃO
# =========================
@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=ler_sheet("pedidos"))


@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    if not session.get("admin"):
        return redirect("/login")

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
    if not session.get("admin"):
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
