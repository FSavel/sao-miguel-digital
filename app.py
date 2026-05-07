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
# ADMIN
# =========================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    avisos = ler_sheet("avisos")
    return render_template("admin.html", avisos=avisos)


# =========================
# ADICIONAR AVISO
# =========================
@app.route("/add_aviso", methods=["POST"])
def add_aviso():
    if not session.get("admin"):
        return redirect("/login")

    titulo = request.form["titulo"]
    descricao = request.form["descricao"]

    avisos = ler_sheet("avisos")
    avisos.append({"titulo": titulo, "descricao": descricao})

    guardar_avisos(avisos)

    return redirect("/admin")


# =========================
# APAGAR AVISO
# =========================
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
# PÁGINA INICIAL
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# AVISOS PÚBLICO
# =========================
@app.route("/avisos")
def avisos():
    dados = ler_sheet("avisos")
    return render_template("avisos.html", avisos=dados)


if __name__ == "__main__":
    app.run(debug=True)