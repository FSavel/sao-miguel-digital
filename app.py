from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import os
import json
import gspread
from google.oauth2.service_account import Credentials

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

creds = Credentials.from_service_account_info(
    json.loads(creds_json),
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado")

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

    for r in data:
        w.append_row([r.get(h, "") for h in headers])


def is_admin():
    return session.get("admin")


# =========================
# LOGIN ADMIN
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        if (
            request.form["username"] == ADMIN_USER
            and request.form["password"] == ADMIN_PASS
        ):
            session["admin"] = True
            return redirect("/admin")

        erro = "Credenciais inválidas"

    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template(
        "index.html",
        avisos=read("avisos")
    )


# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():
    if not is_admin():
        return redirect("/login")

    financeiro = read("financeiro")

    total_dizimos = 0
    total_ofertorios = 0
    total_outros = 0
    total_despesas = 0   # ✅ ADICIONADO

    for item in financeiro:
        try:
            valor = float(item.get("valor", 0))
            tipo = item.get("tipo", "").lower().strip()

            # =========================
            # ENTRADAS
            # =========================
            if "diz" in tipo:
                total_dizimos += valor

            elif "ofert" in tipo:
                total_ofertorios += valor

            elif tipo == "entrada":
                total_outros += valor

            # =========================
            # DESPESAS
            # =========================
            elif tipo == "despesa":
                total_despesas += valor

            # =========================
            # OUTROS CASOS
            # =========================
            else:
                total_outros += valor

        except:
            pass

    return render_template(
    "admin.html",

    # =========================
    # DADOS PRINCIPAIS
    # =========================
    avisos=read("avisos"),
    leituras=read("leituras"),
    canticos=read("canticos"),
    pedidos=read("pedidos"),
    calendario=read("calendario"),
    acolitos=read("acolitos"),
    leitores=read("leitores"),
    outros_servicos=read("outros_servicos"),

    # =========================
    # CATEQUESE
    # =========================
    fases_catequese=read("catequese_fases"),
    catequizandos=read("catequizandos"),
    catequistas=read("catequistas"),
    materiais=read("material_estudo"),
    quiz=read("quiz"),

    # =========================
    # FINANÇAS
    # =========================
    total_dizimos=total_dizimos,
    total_ofertorios=total_ofertorios,
    total_outros=total_outros,
    total_despesas=total_despesas
)


# =========================
# PÁGINAS PÚBLICAS
# =========================
@app.route("/avisos")
def avisos():
    return render_template(
        "avisos.html",
        avisos=read("avisos")
    )


@app.route("/leituras")
def leituras():
    return render_template(
        "leituras.html",
        leituras=read("leituras")
    )


@app.route("/canticos")
def canticos():
    return render_template(
        "canticos.html",
        canticos=read("canticos")
    )


@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template(
        "pedido_oracao.html",
        pedidos=read("pedidos")
    )


@app.route("/calendario")
def calendario():
    return render_template(
        "calendario.html",
        calendario=read("calendario")
    )


@app.route("/escalas")
def escalas():

    return render_template(
        "escalas.html",
        acolitos=read("acolitos"),
        leitores=read("leitores"),
        outros_servicos=read("outros_servicos")
    )

# =========================
# CATEQUESE
# =========================

@app.route("/listas_nominais")
def listas_nominais():

    fases = read("catequese_fases")
    catequistas = read("catequistas")
    catequizandos = read("catequizandos")

    return render_template(
        "listas_nominais.html",
        fases=fases,
        catequistas=catequistas,
        catequizandos=catequizandos
    )


@app.route("/material_estudo")
def material_estudo():

    materiais = read("material_estudo")

    return render_template(
        "material_estudo.html",
        materiais=materiais
    )


@app.route("/quiz")
def quiz():

    perguntas = read("quiz")

    return render_template(
        "quiz.html",
        perguntas=perguntas
    )


# =========================
# QUIZ RESULTADO
# =========================

@app.route("/quiz_resultado", methods=["POST"])
def quiz_resultado():

    dados = request.json

    data = read("quiz_resultados")

    data.append({
        "nome": dados.get("nome"),
        "pontos": dados.get("pontos"),
        "total": dados.get("total"),
        "percentagem": dados.get("percentagem"),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    save("quiz_resultados", data)

    return {"status": "ok"}
    
@app.route("/financeiro")
def financeiro():

    financeiro = read("financeiro")

    total_entradas = 0
    total_despesas = 0

    for item in financeiro:
        try:
            valor = float(item.get("valor", 0))

            if item.get("tipo") == "entrada":
                total_entradas += valor
            else:
                total_despesas += valor

        except:
            pass

    saldo = total_entradas - total_despesas

    return render_template(
        "financeiro.html",
        financeiro=financeiro,
        total_entradas=total_entradas,
        total_despesas=total_despesas,
        saldo=saldo,
        saldo_bancario=saldo
    )
    

# =========================
# DIZIMISTA
# =========================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():

    erro = None

    if request.method == "POST":

        numero = request.form["numero"]
        password = request.form["password"]

        for d in read("dizimistas"):

            if (
                str(d.get("numero")) == str(numero)
                and str(d.get("password")) == str(password)
            ):

                session["dizimista"] = numero
                return redirect("/dizimista_dashboard")

        erro = "Credenciais inválidas"

    return render_template(
        "dizimista_login.html",
        erro=erro
    )


@app.route("/dizimista_dashboard")
def dizimista_dashboard():

    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]

    user = None

    for d in read("dizimistas"):

        if str(d.get("numero")) == str(numero):
            user = d
            break

    contrib = [
        c for c in read("contribuicoes")
        if str(c.get("numero")) == str(numero)
    ]

    return render_template(
        "dizimista_dashboard.html",
        user=user,
        contribuicoes=contrib
    )


@app.route("/dizimista_logout")
def dizimista_logout():
    session.pop("dizimista", None)
    return redirect("/")


@app.route("/export_extrato_pdf")
def export_extrato_pdf():

    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from flask import send_file
    import tempfile
    from datetime import datetime

    numero = session["dizimista"]

    user = None
    for d in read("dizimistas"):
        if str(d.get("numero")) == str(numero):
            user = d
            break

    contribuicoes = [
        c for c in read("contribuicoes")
        if str(c.get("numero")) == str(numero)
    ]

    # =========================
    # DATA E HORA DO DOWNLOAD
    # =========================
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # =========================
    # NOME DO FICHEIRO (F.Savel)
    # =========================
    nome_completo = user.get("nome", "").strip()

    partes = nome_completo.split()

    if len(partes) >= 2:
        inicial = partes[0][0].upper()
        ultimo = partes[-1].capitalize()
        nome_ficheiro = f"extrato_dizimista_{inicial}.{ultimo}.pdf"
    else:
        nome_ficheiro = "extrato_dizimista.pdf"

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(temp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("Extrato do Dizimista", styles["Title"]))
    elementos.append(Spacer(1, 20))

    if user:
        elementos.append(Paragraph(f"<b>Nome:</b> {user.get('nome','')}", styles["BodyText"]))
        elementos.append(Paragraph(f"<b>Número:</b> {user.get('numero','')}", styles["BodyText"]))
        elementos.append(Paragraph(f"<b>Contacto:</b> {user.get('contacto','N/A')}", styles["BodyText"]))

    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(f"<b>Data e Hora do Download:</b> {agora}", styles["BodyText"]))

    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("Contribuições:", styles["Heading2"]))

    for c in contribuicoes:
        texto = f"Data: {c.get('data','')} | Valor: {c.get('valor','')} MZN"
        elementos.append(Paragraph(texto, styles["BodyText"]))

    doc.build(elementos)

    return send_file(
        temp.name,
        as_attachment=True,
        download_name=nome_ficheiro,
        mimetype="application/pdf"
    )

# =========================
# ACÓLITOS
# =========================
@app.route("/add_acolito", methods=["POST"])
def add_acolito():

    data = read("acolitos")
    data.append(request.form.to_dict())

    save("acolitos", data)

    return redirect("/admin")


@app.route("/delete_acolito/<int:i>")
def delete_acolito(i):

    data = read("acolitos")

    if i < len(data):
        data.pop(i)
        save("acolitos", data)

    return redirect("/admin")


@app.route("/edit_acolito/<int:i>", methods=["GET", "POST"])
def edit_acolito(i):

    data = read("acolitos")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("acolitos", data)

        return redirect("/admin")

    return render_template(
        "edit_acolito.html",
        acolito=data[i],
        index=i
    )


# =========================
# LEITORES
# =========================
@app.route("/add_leitor", methods=["POST"])
def add_leitor():

    data = read("leitores")
    data.append(request.form.to_dict())

    save("leitores", data)

    return redirect("/admin")


@app.route("/delete_leitor/<int:i>")
def delete_leitor(i):

    data = read("leitores")

    if i < len(data):
        data.pop(i)
        save("leitores", data)

    return redirect("/admin")


@app.route("/edit_leitor/<int:i>", methods=["GET", "POST"])
def edit_leitor(i):

    data = read("leitores")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("leitores", data)

        return redirect("/admin")

    return render_template(
        "edit_leitor.html",
        leitor=data[i],
        index=i
    )


# =========================
# AVISOS
# =========================
@app.route("/add_aviso", methods=["POST"])
def add_aviso():

    data = read("avisos")

    data.append({
        "titulo": request.form["titulo"],
        "descricao": request.form["descricao"]
    })

    save("avisos", data)

    return redirect("/admin")


@app.route("/delete_aviso/<int:i>")
def delete_aviso(i):

    data = read("avisos")

    if i < len(data):
        data.pop(i)
        save("avisos", data)

    return redirect("/admin")


@app.route("/edit_aviso/<int:i>", methods=["GET", "POST"])
def edit_aviso(i):

    data = read("avisos")

    if request.method == "POST":

        data[i] = {
            "titulo": request.form["titulo"],
            "descricao": request.form["descricao"]
        }

        save("avisos", data)

        return redirect("/admin")

    return render_template(
        "edit_aviso.html",
        aviso=data[i],
        index=i
    )


# =========================
# LEITURAS
# =========================
@app.route("/add_leitura", methods=["POST"])
def add_leitura():

    data = read("leituras")

    data.append(request.form.to_dict())

    save("leituras", data)

    return redirect("/admin")


@app.route("/delete_leitura/<int:i>")
def delete_leitura(i):

    data = read("leituras")

    if i < len(data):
        data.pop(i)
        save("leituras", data)

    return redirect("/admin")


@app.route("/edit_leitura/<int:i>", methods=["GET", "POST"])
def edit_leitura(i):

    data = read("leituras")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("leituras", data)

        return redirect("/admin")

    return render_template(
        "edit_leitura.html",
        leitura=data[i],
        index=i
    )


# =========================
# CÂNTICOS
# =========================
@app.route("/add_cantico", methods=["POST"])
def add_cantico():

    data = read("canticos")

    data.append(request.form.to_dict())

    save("canticos", data)

    return redirect("/admin")


@app.route("/delete_cantico/<int:i>")
def delete_cantico(i):

    data = read("canticos")

    if i < len(data):
        data.pop(i)
        save("canticos", data)

    return redirect("/admin")


@app.route("/edit_cantico/<int:i>", methods=["GET", "POST"])
def edit_cantico(i):

    data = read("canticos")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("canticos", data)

        return redirect("/admin")

    return render_template(
        "edit_cantico.html",
        cantico=data[i],
        index=i
    )


# =========================
# PEDIDOS
# =========================
@app.route("/add_pedido", methods=["POST"])
def add_pedido():

    data = read("pedidos")

    data.append(request.form.to_dict())

    save("pedidos", data)

    return redirect("/admin")


@app.route("/delete_pedido/<int:i>")
def delete_pedido(i):

    data = read("pedidos")

    if i < len(data):
        data.pop(i)
        save("pedidos", data)

    return redirect("/admin")


@app.route("/edit_pedido/<int:i>", methods=["GET", "POST"])
def edit_pedido(i):

    data = read("pedidos")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("pedidos", data)

        return redirect("/admin")

    return render_template(
        "edit_pedido.html",
        pedido=data[i],
        index=i
    )


# =========================
# CALENDÁRIO
# =========================
@app.route("/add_calendario", methods=["POST"])
def add_calendario():

    data = read("calendario")

    data.append(request.form.to_dict())

    save("calendario", data)

    return redirect("/admin")


@app.route("/delete_calendario/<int:i>")
def delete_calendario(i):

    data = read("calendario")

    if i < len(data):
        data.pop(i)
        save("calendario", data)

    return redirect("/admin")


@app.route("/edit_calendario/<int:i>", methods=["GET", "POST"])
def edit_calendario(i):

    data = read("calendario")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("calendario", data)

        return redirect("/admin")

    return render_template(
        "calendario.html",
        calendario=data
    )


# =========================
# FINANCEIRO
# =========================
@app.route("/add_financeiro", methods=["POST"])
def add_financeiro():

    if not is_admin():
        return redirect("/login")

    data = read("financeiro")

    data.append(request.form.to_dict())

    save("financeiro", data)

    return redirect("/financeiro")


# =========================
# OUTROS SERVIÇOS
# =========================

@app.route("/add_outro_servico", methods=["POST"])
def add_outro_servico():

    data = read("outros_servicos")

    data.append(request.form.to_dict())

    save("outros_servicos", data)

    return redirect("/admin")


@app.route("/delete_outro_servico/<int:i>")
def delete_outro_servico(i):

    data = read("outros_servicos")

    if i < len(data):
        data.pop(i)
        save("outros_servicos", data)

    return redirect("/admin")


@app.route("/edit_outro_servico/<int:i>", methods=["GET", "POST"])
def edit_outro_servico(i):

    data = read("outros_servicos")

    if request.method == "POST":

        data[i] = request.form.to_dict()

        save("outros_servicos", data)

        return redirect("/admin")

    return render_template(
        "edit_outro_servico.html",
        servico=data[i],
        index=i
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
