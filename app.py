from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "saomiguel2026"

EXCEL_FILE = "paroquia.xlsx"

ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


# =========================
# UTILITÁRIO
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
# HOME (ATUALIZADO ✔)
# =========================
@app.route("/")
def index():
    return render_template(
        "index.html",
        avisos=ler_sheet("avisos")
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
# PÁGINAS PÚBLICAS
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
