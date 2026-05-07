from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "saomiguel2026"

EXCEL_FILE = "paroquia.xlsx"

ADMIN_USER = "padre"
ADMIN_PASS = "1234"


# =========================
# LER SHEET
# =========================
def ler_sheet(nome):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=nome)
        df = df.fillna("")
        return df.to_dict(orient="records")
    except:
        return []


# =========================
# GUARDAR AVISOS
# =========================
def guardar_avisos(lista):
    df = pd.DataFrame(lista)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="avisos", index=False)


# =========================
# GUARDAR LEITURAS
# =========================
def guardar_leituras(lista):
    df = pd.DataFrame(lista)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="leituras", index=False)


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

    avisos = ler_sheet("avisos")
    avisos.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })

    guardar_avisos(avisos)
    return redirect("/admin")


@app.route("/delete_aviso/<int:index>")
def delete_aviso(index):
    if not session.get("admin"):
        return redirect("/login")

    avisos = ler_sheet("avisos")

    if 0 <= index < len(avisos):
        avisos.pop(index)

    guardar_avisos(avisos)
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

    leituras = ler_sheet("leituras")
    leituras.append({
        "tipo": request.form["tipo"],
        "texto": request.form["texto"]
    })

    guardar_leituras(leituras)
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

    canticos = ler_sheet("canticos")
    canticos.append({
        "momento": request.form["momento"],
        "cantico": request.form["cantico"],
        "letra": request.form["letra"]
    })

    df = pd.DataFrame(canticos)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="canticos", index=False)

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

    acolitos = ler_sheet("acolitos")
    acolitos.append({
        "funcao": request.form["funcao"],
        "nome": request.form["nome"]
    })

    df = pd.DataFrame(acolitos)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="acolitos", index=False)

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

    leitores = ler_sheet("leitores")
    leitores.append({
        "funcao": request.form["funcao"],
        "nome": request.form["nome"]
    })

    df = pd.DataFrame(leitores)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="leitores", index=False)

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

    calendario = ler_sheet("calendario")
    calendario.append({
        "evento": request.form["evento"],
        "data": request.form["data"],
        "descricao": request.form["descricao"]
    })

    df = pd.DataFrame(calendario)
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="calendario", index=False)

    return redirect("/admin")


# =========================
# PEDIDO DE ORAÇÃO
# =========================
@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=ler_sheet("pedidos"))


if __name__ == "__main__":
    app.run(debug=True)
