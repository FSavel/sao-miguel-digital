from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json
import random
import tempfile
from functools import wraps
import gspread
from google.oauth2.service_account import Credentials

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
creds = Credentials.from_service_account_info(
    json.loads(creds_json),
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

print("✅ Google Sheets ligado com sucesso!")

# =========================
# HELPERS & DECORATORS
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
    
    # Correção: Se a lista estiver vazia, limpamos a folha para permitir exclusão total
    if not data:
        w.clear()
        return

    headers = list(data[0].keys())
    rows = [headers]
    for r in data:
        rows.append([r.get(h, "") for h in headers])

    w.clear()
    w.update("A1", rows)

def is_admin():
    return session.get("admin")

# Decorador para proteger rotas administrativas
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# =========================
# LOGIN / LOGOUT ADMIN
# =========================
ADMIN_USER = "Padre"
ADMIN_PASS = "1234"

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        if (
            request.form.get("username") == ADMIN_USER
            and request.form.get("password") == ADMIN_PASS
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
# PÁGINAS PÚBLICAS
# =========================
@app.route("/")
def index():
    return render_template("index.html", avisos=read("avisos"))

@app.route("/avisos")
def avisos():
    return render_template("avisos.html", avisos=read("avisos"))

@app.route("/leituras")
def leituras():
    return render_template("leituras.html", leituras=read("leituras"))

@app.route("/canticos")
def canticos():
    return render_template("canticos.html", canticos=read("canticos"))

@app.route("/pedido_oracao")
def pedido_oracao():
    return render_template("pedido_oracao.html", pedidos=read("pedidos"))

@app.route("/calendario")
def calendario():
    return render_template("calendario.html", calendario=read("calendario"))

@app.route("/escalas")
def escalas():
    # Carrega os dados
    acolitos_dados = read("acolitos")
    
    # Normaliza: garante que 'missa' seja sempre string para o filtro funcionar
    for a in acolitos_dados:
        a['missa'] = str(a.get('missa', '')).strip()
    
    return render_template(
        "escalas.html",
        acolitos=acolitos_dados,
        leitores=read("leitores"),
        outros_servicos=read("outros_servicos")
    )

# =========================
# PAINEL ADMIN
# =========================
@app.route("/admin")
@admin_required
def admin():
    financeiro = read("financeiro")
    total_dizimos = 0
    total_ofertorios = 0
    total_outros = 0
    total_despesas = 0

    for item in financeiro:
        try:
            valor = float(item.get("valor", 0))
            tipo = str(item.get("tipo", "")).lower().strip()

            if "diz" in tipo:
                total_dizimos += valor
            elif "ofert" in tipo:
                total_ofertorios += valor
            elif tipo == "entrada":
                total_outros += valor
            elif tipo == "despesa":
                total_despesas += valor
            else:
                total_outros += valor
        except:
            pass

    return render_template(
        "admin.html",
        avisos=read("avisos"),
        leituras=read("leituras"),
        canticos=read("canticos"),
        pedidos=read("pedidos"),
        calendario=read("calendario"),
        acolitos=read("acolitos"),
        leitores=read("leitores"),
        outros_servicos=read("outros_servicos"),
        fases_catequese=read("catequese_fases"),
        catequizandos=read("catequizandos"),
        catequistas=read("catequistas"),
        materiais=read("material_estudo"),
        quiz=read("quiz"),
        total_dizimos=total_dizimos,
        total_ofertorios=total_ofertorios,
        total_outros=total_outros,
        total_despesas=total_despesas
    )

# =========================
# GESTÃO DE ACÓLITOS (ADMIN)
# =========================
@app.route("/add_acolito", methods=["POST"])
@admin_required
def add_acolito():
    data = read("acolitos")
    data.append(request.form.to_dict())
    save("acolitos", data)
    return redirect("/admin")

@app.route("/delete_acolito/<int:i>")
@admin_required
def delete_acolito(i):
    data = read("acolitos")
    if 0 <= i < len(data):
        data.pop(i)
        save("acolitos", data)
    return redirect("/admin")

@app.route("/edit_acolito/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_acolito(i):
    data = read("acolitos")
    if not (0 <= i < len(data)):
        return redirect("/admin")
    
    if request.method == "POST":
        # Captura a missa diretamente do campo oculto do formulário
        nova_data = request.form.to_dict()
        data[i] = nova_data
        save("acolitos", data)
        return redirect("/admin")
    
    # Se for GET, pega o parâmetro da URL para exibir no formulário
    missa = request.args.get("missa", data[i].get("missa", "1"))
    return render_template("edit_acolito.html", acolito=data[i], index=i, missa=missa)

# =========================
# GESTÃO DE LEITORES (ADMIN)
# =========================
@app.route("/add_leitor", methods=["POST"])
@admin_required
def add_leitor():
    data = read("leitores")
    data.append(request.form.to_dict())
    save("leitores", data)
    return redirect("/admin")

@app.route("/delete_leitor/<int:i>")
@admin_required
def delete_leitor(i):
    data = read("leitores")
    if 0 <= i < len(data):
        data.pop(i)
        save("leitores", data)
    return redirect("/admin")

@app.route("/edit_leitor/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_leitor(i):
    data = read("leitores")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("leitores", data)
        return redirect("/admin")
        
    # Se for GET, pega o parâmetro da URL ou o que já está na planilha
    missa = request.args.get("missa", data[i].get("missa", "1"))
    return render_template("edit_leitor.html", leitor=data[i], index=i, missa=missa)

# =========================
# GESTÃO DE AVISOS (ADMIN)
# =========================
@app.route("/add_aviso", methods=["POST"])
@admin_required
def add_aviso():
    data = read("avisos")
    data.append({
        "titulo": request.form.get("titulo", ""),
        "descricao": request.form.get("descricao", "")
    })
    save("avisos", data)
    return redirect("/admin")

@app.route("/delete_aviso/<int:i>")
@admin_required
def delete_aviso(i):
    data = read("avisos")
    if 0 <= i < len(data):
        data.pop(i)
        save("avisos", data)
    return redirect("/admin")

@app.route("/edit_aviso/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_aviso(i):
    data = read("avisos")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = {
            "titulo": request.form.get("titulo", ""),
            "descricao": request.form.get("descricao", "")
        }
        save("avisos", data)
        return redirect("/admin")
        
    return render_template("edit_aviso.html", aviso=data[i], index=i)

# =========================
# GESTÃO DE LEITURAS (ADMIN)
# =========================
@app.route("/add_leitura", methods=["POST"])
@admin_required
def add_leitura():
    data = read("leituras")
    data.append(request.form.to_dict())
    save("leituras", data)
    return redirect("/admin")

@app.route("/delete_leitura/<int:i>")
@admin_required
def delete_leitura(i):
    data = read("leituras")
    if 0 <= i < len(data):
        data.pop(i)
        save("leituras", data)
    return redirect("/admin")

@app.route("/edit_leitura/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_leitura(i):
    data = read("leituras")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("leituras", data)
        return redirect("/admin")
        
    return render_template("edit_leitura.html", leitura=data[i], index=i)

# =========================
# GESTÃO DE CÂNTICOS (ADMIN)
# =========================
@app.route("/add_cantico", methods=["POST"])
@admin_required
def add_cantico():
    data = read("canticos")
    data.append(request.form.to_dict())
    save("canticos", data)
    return redirect("/admin")

@app.route("/delete_cantico/<int:i>")
@admin_required
def delete_cantico(i):
    data = read("canticos")
    if 0 <= i < len(data):
        data.pop(i)
        save("canticos", data)
    return redirect("/admin")

@app.route("/edit_cantico/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_cantico(i):
    data = read("canticos")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("canticos", data)
        return redirect("/admin")
        
    return render_template("edit_cantico.html", cantico=data[i], index=i)

# =========================
# GESTÃO DE PEDIDOS (ADMIN)
# =========================
@app.route("/add_pedido", methods=["POST"])
def add_pedido():
    # Aberto ao público para submeter intenções
    data = read("pedidos")
    data.append(request.form.to_dict())
    save("pedidos", data)
    return redirect("/pedido_oracao")

@app.route("/delete_pedido/<int:i>")
@admin_required
def delete_pedido(i):
    data = read("pedidos")
    if 0 <= i < len(data):
        data.pop(i)
        save("pedidos", data)
    return redirect("/admin")

@app.route("/edit_pedido/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_pedido(i):
    data = read("pedidos")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("pedidos", data)
        return redirect("/admin")
        
    return render_template("edit_pedido.html", pedido=data[i], index=i)

# =========================
# GESTÃO DE CALENDÁRIO (ADMIN)
# =========================
@app.route("/add_calendario", methods=["POST"])
@admin_required
def add_calendario():
    data = read("calendario")
    data.append(request.form.to_dict())
    save("calendario", data)
    return redirect("/admin")

@app.route("/delete_calendario/<int:i>")
@admin_required
def delete_calendario(i):
    data = read("calendario")
    if 0 <= i < len(data):
        data.pop(i)
        save("calendario", data)
    return redirect("/admin")

@app.route("/edit_calendario/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_calendario(i):
    data = read("calendario")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("calendario", data)
        return redirect("/admin")
        
    # Correção: Roda agora para o template de edição correto
    return render_template("edit_calendario.html", evento=data[i], index=i)

# =========================
# GESTÃO FINANCEIRA (ADMIN)
# =========================
@app.route("/add_financeiro", methods=["POST"])
@admin_required
def add_financeiro():
    data = read("financeiro")
    data.append(request.form.to_dict())
    save("financeiro", data)
    return redirect("/financeiro")

@app.route("/financeiro")
def financeiro():
    financeiro_dados = read("financeiro")
    total_entradas = 0
    total_despesas = 0

    for item in financeiro_dados:
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
        financeiro=financeiro_dados,
        total_entradas=total_entradas,
        total_despesas=total_despesas,
        saldo=saldo,
        saldo_bancario=saldo
    )

# =========================
# GESTÃO OUTROS SERVIÇOS
# =========================
@app.route("/add_outro_servico", methods=["POST"])
@admin_required
def add_outro_servico():
    data = read("outros_servicos")
    data.append(request.form.to_dict())
    save("outros_servicos", data)
    return redirect("/admin")

@app.route("/delete_outro_servico/<int:i>")
@admin_required
def delete_outro_servico(i):
    data = read("outros_servicos")
    if 0 <= i < len(data):
        data.pop(i)
        save("outros_servicos", data)
    return redirect("/admin")

@app.route("/edit_outro_servico/<int:i>", methods=["GET", "POST"])
@admin_required
def edit_outro_servico(i):
    data = read("outros_servicos")
    if not (0 <= i < len(data)):
        return redirect("/admin")
        
    if request.method == "POST":
        data[i] = request.form.to_dict()
        save("outros_servicos", data)
        return redirect("/admin")
        
    return render_template("edit_outro_servico.html", servico=data[i], index=i)

# =========================
# CATEQUESE E QUIZ
# =========================
@app.route("/listas_nominais")
def listas_nominais():
    return render_template(
        "listas_nominais.html",
        fases=read("catequese_fases"),
        catequistas=read("catequistas"),
        catequizandos=read("catequizandos")
    )

@app.route("/material_estudo")
def material_estudo():
    return render_template("material_estudo.html", materiais=read("material_estudo"))

@app.route("/quiz")
def quiz():
    perguntas = read("quiz")
    for p in perguntas:
        p["pergunta"] = str(p.get("pergunta", "")).strip()
        p["opcao1"] = str(p.get("opcao1", "")).strip()
        p["opcao2"] = str(p.get("opcao2", "")).strip()
        p["opcao3"] = str(p.get("opcao3", "")).strip()
        p["resposta_correta"] = str(p.get("resposta_correta", "")).strip()
        p["explicacao"] = str(p.get("explicacao", "")).strip()

    random.shuffle(perguntas)
    perguntas = perguntas[:20]
    return render_template("quiz.html", perguntas=perguntas)

@app.route("/quiz_resultado", methods=["POST"])
def quiz_resultado():
    dados = json.loads(request.form["data"])
    data = read("quiz_resultados")

    nome = dados.get("nome")
    pontos = dados.get("pontos")
    total = dados.get("total")
    percentagem = dados.get("percentagem")

    data.append({
        "nome": nome,
        "pontos": pontos,
        "total": total,
        "percentagem": percentagem,
        "data": datetime.now(ZoneInfo("Africa/Maputo")).strftime("%d/%m/%Y %H:%M")
    })
    save("quiz_resultados", data)

    return render_template(
        "quiz_resultado.html",
        nome=nome,
        pontos=pontos,
        total=total,
        percentagem=percentagem
    )

# =========================
# REDES SOCIAIS
# =========================
@app.route("/redes_sociais")
def redes_sociais():
    return render_template("redes_sociais.html")

# =========================
# DIZIMISTAS (PORTAL PÚBLICO)
# =========================
@app.route("/dizimista_login", methods=["GET", "POST"])
def dizimista_login():
    erro = None
    if request.method == "POST":
        numero = request.form.get("numero")
        password = request.form.get("password")

        for d in read("dizimistas"):
            if (
                str(d.get("numero")) == str(numero)
                and str(d.get("password")) == str(password)
            ):
                session["dizimista"] = numero
                return redirect("/dizimista_dashboard")
        erro = "Credenciais inválidas"
        
    return render_template("dizimista_login.html", erro=erro)

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

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    numero = session["dizimista"]
    data = read("dizimistas")
    user = None
    index = None

    for i, d in enumerate(data):
        if str(d.get("numero")) == str(numero):
            user = d
            index = i
            break

    if not user:
        return redirect("/dizimista_logout")

    erro = None
    sucesso = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        contacto = request.form.get("contacto", "").strip()
        email = request.form.get("email", "").strip()

        password_actual = request.form.get("password_actual", "").strip()
        nova_password = request.form.get("nova_password", "").strip()
        confirmar_password = request.form.get("confirmar_password", "").strip()

        user["nome"] = nome
        user["contacto"] = contacto
        user["email"] = email

        if password_actual or nova_password or confirmar_password:
            if str(user.get("password")) != password_actual:
                erro = "Password actual incorrecta."
                return render_template("editar_perfil.html", user=user, erro=erro)

            if nova_password != confirmar_password:
                erro = "As novas passwords não coincidem."
                return render_template("editar_perfil.html", user=user, erro=erro)

            if len(nova_password) < 4:
                erro = "A nova password deve ter pelo menos 4 caracteres."
                return render_template("editar_perfil.html", user=user, erro=erro)

            user["password"] = nova_password

        data[index] = user
        save("dizimistas", data)
        sucesso = "Perfil actualizado com sucesso."

    return render_template(
        "editar_perfil.html",
        user=user,
        erro=erro,
        sucesso=sucesso
    )

@app.route("/export_extrato_pdf")
def export_extrato_pdf():
    if not session.get("dizimista"):
        return redirect("/dizimista_login")

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4

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

    agora = datetime.now(ZoneInfo("Africa/Maputo")).strftime("%d/%m/%Y %H:%M:%S")
    nome_completo = user.get("nome", "").strip() if user else ""
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

@app.route('/sw.js')
def serve_service_worker():
    return app.send_static_file('sw.js')
    
# =========================
# RUN APPLICATION
# =========================
if __name__ == "__main__":
    app.run(debug=True)
