import os
import time
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g
)
from database import query_db, execute_db, init_db
from crypto_utils import (
    encrypt_cpf, decrypt_cpf, mask_cpf, format_cpf,
    verify_user_password
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clinica-vet-saep-secret-key-2026")
app.permanent_session_lifetime = timedelta(minutes=30)  # Sessão com tempo de expiração de 30 minutos

init_db()

@app.before_request
def check_session_timeout():
    """Valida a expiração da sessão por inatividade (tempo de expiração)."""
   
    public_endpoints = ["login", "static"]
    if request.endpoint and any(request.endpoint.startswith(p) for p in public_endpoints):
        return

    if "user_id" not in session:
        return redirect(url_for("login"))

    now = time.time()
    last_activity = session.get("last_activity")
    if last_activity and (now - last_activity > 1800):  # 30 minutos
        session.clear()
        flash("Sua sessão expirou por tempo de inatividade. Faça login novamente.", "warning")
        return redirect(url_for("login"))

    session["last_activity"] = now

    g.user_name = session.get("user_name")
    g.user_email = session.get("user_email")
    g.user_role = session.get("user_role")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not email or not senha:
            flash("Falha na autenticação: Por favor, preencha todos os campos obrigatórios.", "danger")
            return render_template("login.html", email=email)


        user = query_db("SELECT * FROM usuario WHERE email = ?", [email], one=True)

        if not user or not verify_user_password(user["senha"], senha):
            flash("Falha na autenticação: E-mail ou senha incorretos. Verifique suas credenciais e tente novamente.", "danger")
            return render_template("login.html", email=email)

        session.permanent = True
        session["user_id"] = user["id"]
        session["user_name"] = user["nome"]
        session["user_email"] = user["email"]
        session["user_role"] = user["cargo"]
        session["last_activity"] = time.time()

        flash(f"Login realizado com sucesso! Bem-vindo(a), {user['nome']}.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Finaliza a sessão do usuário de maneira segura."""
    user_name = session.get("user_name", "Usuário")
    session.clear()
    flash(f"Até logo, {user_name}! Você saiu do sistema com segurança.", "info")
    return redirect(url_for("login"))

@app.route("/")
def dashboard():
    """
    Exibe a tela principal com:
    - Nome do usuário logado
    - Acesso a todos os demais recursos (Tutores, Pets, Agendamentos)
    - Maneira clara de sair do sistema
    """

    tot_tutores = query_db("SELECT COUNT(*) as total FROM tutor", one=True)["total"]
    tot_pets = query_db("SELECT COUNT(*) as total FROM pet", one=True)["total"]
    tot_agendamentos = query_db("SELECT COUNT(*) as total FROM agendamento", one=True)["total"]

    proximos = query_db("""
        SELECT a.id, a.data_agendamento, a.hora_agendamento, a.tipo_servico, a.status,
               p.nome AS pet_nome, t.nome AS tutor_nome
        FROM agendamento a
        JOIN pet p ON a.pet_id = p.id
        JOIN tutor t ON p.tutor_id = t.id
        ORDER BY a.data_agendamento ASC, a.hora_agendamento ASC
        LIMIT 5
    """)

    return render_template(
        "index.html",
        tot_tutores=tot_tutores,
        tot_pets=tot_pets,
        tot_agendamentos=tot_agendamentos,
        proximos=proximos
    )

@app.route("/tutores")
def tutores():
    """
    Exibe a listagem de tutores com:
    - Recurso de busca por termo com confirmação
    - Atualização dinâmica da listagem de registros correspondentes
    - Edição de tutores já cadastrados
    - Exibição segura e descriptografia controlada de CPF (LGPD)
    """
    termo = request.args.get("q", "").strip()

    todos_tutores = query_db("""
        SELECT t.*, COUNT(p.id) AS total_pets
        FROM tutor t
        LEFT JOIN pet p ON p.tutor_id = t.id
        GROUP BY t.id
        ORDER BY t.nome ASC
    """)

    lista_processada = []
    for t in todos_tutores:
        cpf_dec = decrypt_cpf(t["cpf"])
        t_dict = dict(t)
        t_dict["cpf_decrypted"] = cpf_dec
        t_dict["cpf_masked"] = mask_cpf(cpf_dec)
        lista_processada.append(t_dict)

    if termo:
        termo_lower = termo.lower()
        termo_digits = "".join(c for c in termo if c.isdigit())

        filtrados = []
        for t in lista_processada:

            if (termo_lower in t["nome"].lower() or
                termo_lower in t["email"].lower() or
                termo in t["telefone"] or
                termo in t["cpf_decrypted"] or
                (termo_digits and termo_digits in "".join(c for c in t["cpf_decrypted"] if c.isdigit()))):
                filtrados.append(t)
        resultado = filtrados
    else:
        resultado = lista_processada

    return render_template("tutores.html", tutores=resultado, termo_busca=termo)

@app.route("/tutores/novo", methods=["GET", "POST"])
def tutor_novo():
    """Cadastra um novo tutor com CPF criptografado no banco."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()
        endereco = request.form.get("endereco", "").strip()

        if not nome or not cpf or not telefone or not email:
            flash("Preencha todos os campos obrigatórios do tutor.", "danger")
            return render_template("tutor_form.html", acao="Cadastrar", tutor=request.form)

        cpf_criptografado = encrypt_cpf(cpf)

        execute_db("""
            INSERT INTO tutor (nome, cpf, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
        """, [nome, cpf_criptografado, telefone, email, endereco])

        flash(f"Tutor '{nome}' cadastrado com sucesso! CPF armazenado sob proteção criptográfica.", "success")
        return redirect(url_for("tutores"))

    return render_template("tutor_form.html", acao="Cadastrar", tutor=None)

@app.route("/tutores/<int:id>/editar", methods=["GET", "POST"])
def tutor_editar(id):
    """Permite editar os dados de um tutor já cadastrado, salvando no banco de dados."""
    tutor = query_db("SELECT * FROM tutor WHERE id = ?", [id], one=True)
    if not tutor:
        flash("Tutor não encontrado.", "danger")
        return redirect(url_for("tutores"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()
        endereco = request.form.get("endereco", "").strip()

        if not nome or not cpf or not telefone or not email:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("tutor_form.html", acao="Editar", tutor=request.form)

    
        cpf_criptografado = encrypt_cpf(cpf)

        execute_db("""
            UPDATE tutor
            SET nome = ?, cpf = ?, telefone = ?, email = ?, endereco = ?
            WHERE id = ?
        """, [nome, cpf_criptografado, telefone, email, endereco, id])

        flash(f"Dados do tutor '{nome}' alterados e salvos com sucesso no banco de dados!", "success")
        return redirect(url_for("tutores"))

    tutor_dict = dict(tutor)
    tutor_dict["cpf"] = decrypt_cpf(tutor["cpf"])

    return render_template("tutor_form.html", acao="Editar", tutor=tutor_dict)


@app.route("/pets")
def pets():
    """Listagem de pets cadastrados com seus respectivos tutores."""
    lista_pets = query_db("""
        SELECT p.*, t.nome AS tutor_nome, t.telefone AS tutor_telefone
        FROM pet p
        JOIN tutor t ON p.tutor_id = t.id
        ORDER BY p.nome ASC
    """)
    return render_template("pets.html", pets=lista_pets)

@app.route("/pets/novo", methods=["GET", "POST"])
def pet_novo():
    """
    Cadastra um novo pet.
    Regra de negócio: Ao cadastrar um novo pet, o usuário DEVE associá-lo a um tutor.
    """
    tutores = query_db("SELECT id, nome FROM tutor ORDER BY nome ASC")

    if request.method == "POST":
        tutor_id = request.form.get("tutor_id", "").strip()
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        peso = request.form.get("peso", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

       
        if not tutor_id:
            flash("Regra de negócio violada: O pet DEVE ser obrigatoriamente associado a um tutor.", "danger")
            return render_template("pet_form.html", acao="Cadastrar", pet=request.form, tutores=tutores)

        if not nome or not especie or not raca or not data_nascimento or not peso:
            flash("Preencha todos os campos obrigatórios do pet.", "danger")
            return render_template("pet_form.html", acao="Cadastrar", pet=request.form, tutores=tutores)

        try:
            peso_float = float(peso.replace(",", "."))
        except ValueError:
            flash("Informe um valor numérico válido para o peso do pet.", "danger")
            return render_template("pet_form.html", acao="Cadastrar", pet=request.form, tutores=tutores)

        execute_db("""
            INSERT INTO pet (tutor_id, nome, especie, raca, data_nascimento, peso, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [tutor_id, nome, especie, raca, data_nascimento, peso_float, observacoes])

        flash(f"Pet '{nome}' cadastrado e associado com sucesso ao tutor selecionado!", "success")
        return redirect(url_for("pets"))

    return render_template("pet_form.html", acao="Cadastrar", pet=None, tutores=tutores)

@app.route("/pets/<int:id>/editar", methods=["GET", "POST"])
def pet_editar(id):
    """Edita os dados de um pet já cadastrado."""
    pet = query_db("SELECT * FROM pet WHERE id = ?", [id], one=True)
    if not pet:
        flash("Pet não encontrado.", "danger")
        return redirect(url_for("pets"))

    tutores = query_db("SELECT id, nome FROM tutor ORDER BY nome ASC")

    if request.method == "POST":
        tutor_id = request.form.get("tutor_id", "").strip()
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        peso = request.form.get("peso", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not tutor_id or not nome or not especie or not raca or not data_nascimento or not peso:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("pet_form.html", acao="Editar", pet=request.form, tutores=tutores)

        try:
            peso_float = float(peso.replace(",", "."))
        except ValueError:
            flash("Peso inválido.", "danger")
            return render_template("pet_form.html", acao="Editar", pet=request.form, tutores=tutores)

        execute_db("""
            UPDATE pet
            SET tutor_id = ?, nome = ?, especie = ?, raca = ?, data_nascimento = ?, peso = ?, observacoes = ?
            WHERE id = ?
        """, [tutor_id, nome, especie, raca, data_nascimento, peso_float, observacoes, id])

        flash(f"Dados do pet '{nome}' atualizados com sucesso no banco de dados!", "success")
        return redirect(url_for("pets"))

    return render_template("pet_form.html", acao="Editar", pet=dict(pet), tutores=tutores)

@app.route("/agendamentos")
def agendamentos():
    """
    Exibe a listagem dos agendamentos cadastrados ORDENADOS POR DIA DE AGENDAMENTO,
    trazendo TODOS os dados do tutor e do pet.
    Permite atualizar a data de um agendamento já cadastrado.
    """
    
    registros = query_db("""
        SELECT
            a.id AS agendamento_id,
            a.data_agendamento,
            a.hora_agendamento,
            a.tipo_servico,
            a.status,
            a.observacoes AS agendamento_obs,
            p.id AS pet_id,
            p.nome AS pet_nome,
            p.especie AS pet_especie,
            p.raca AS pet_raca,
            p.data_nascimento AS pet_data_nascimento,
            p.peso AS pet_peso,
            p.observacoes AS pet_obs,
            t.id AS tutor_id,
            t.nome AS tutor_nome,
            t.cpf AS tutor_cpf,
            t.telefone AS tutor_telefone,
            t.email AS tutor_email,
            t.endereco AS tutor_endereco
        FROM agendamento a
        JOIN pet p ON a.pet_id = p.id
        JOIN tutor t ON p.tutor_id = t.id
        ORDER BY a.data_agendamento ASC, a.hora_agendamento ASC
    """)

 
    agendamentos_processados = []
    for r in registros:
        item = dict(r)
        cpf_dec = decrypt_cpf(item["tutor_cpf"])
        item["tutor_cpf_decrypted"] = cpf_dec
        item["tutor_cpf_masked"] = mask_cpf(cpf_dec)
        agendamentos_processados.append(item)

    return render_template("agendamentos.html", agendamentos=agendamentos_processados)

@app.route("/agendamentos/<int:id>/atualizar-data", methods=["POST"])
def agendamento_atualizar_data(id):
    """
    Regra de negócio: Permite atualizar a data de um agendamento já cadastrado,
    salvando a alteração no banco de dados.
    """
    nova_data = request.form.get("nova_data", "").strip()
    nova_hora = request.form.get("nova_hora", "").strip()

    if not nova_data:
        flash("Por favor, selecione uma data válida para a remarcação.", "danger")
        return redirect(url_for("agendamentos"))

   
    agendamento = query_db("SELECT * FROM agendamento WHERE id = ?", [id], one=True)
    if not agendamento:
        flash("Agendamento não encontrado.", "danger")
        return redirect(url_for("agendamentos"))

    hora_final = nova_hora if nova_hora else agendamento["hora_agendamento"]

    execute_db("""
        UPDATE agendamento
        SET data_agendamento = ?, hora_agendamento = ?
        WHERE id = ?
    """, [nova_data, hora_final, id])

    flash(f"Data do agendamento #{id} atualizada com sucesso para {nova_data} às {hora_final}!", "success")
    return redirect(url_for("agendamentos"))

@app.route("/agendamentos/novo", methods=["GET", "POST"])
def agendamento_novo():
    """Cadastra um novo agendamento com seleção de pet e tutor."""
    pets = query_db("""
        SELECT p.id, p.nome, p.especie, p.raca, t.nome AS tutor_nome
        FROM pet p
        JOIN tutor t ON p.tutor_id = t.id
        ORDER BY t.nome ASC, p.nome ASC
    """)

    if request.method == "POST":
        pet_id = request.form.get("pet_id", "").strip()
        data_agendamento = request.form.get("data_agendamento", "").strip()
        hora_agendamento = request.form.get("hora_agendamento", "").strip()
        tipo_servico = request.form.get("tipo_servico", "").strip()
        status = request.form.get("status", "Agendado").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not pet_id or not data_agendamento or not hora_agendamento or not tipo_servico:
            flash("Preencha todos os campos obrigatórios para o agendamento.", "danger")
            return render_template("agendamento_form.html", acao="Cadastrar", agendamento=request.form, pets=pets)

        execute_db("""
            INSERT INTO agendamento (pet_id, data_agendamento, hora_agendamento, tipo_servico, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [pet_id, data_agendamento, hora_agendamento, tipo_servico, status, observacoes])

        flash("Novo agendamento cadastrado e salvo com sucesso no banco de dados!", "success")
        return redirect(url_for("agendamentos"))

    return render_template("agendamento_form.html", acao="Cadastrar", agendamento=None, pets=pets)

@app.route("/agendamentos/<int:id>/editar", methods=["GET", "POST"])
def agendamento_editar(id):
    """Edita todos os campos de um agendamento existente."""
    agendamento = query_db("SELECT * FROM agendamento WHERE id = ?", [id], one=True)
    if not agendamento:
        flash("Agendamento não encontrado.", "danger")
        return redirect(url_for("agendamentos"))

    pets = query_db("""
        SELECT p.id, p.nome, p.especie, p.raca, t.nome AS tutor_nome
        FROM pet p
        JOIN tutor t ON p.tutor_id = t.id
        ORDER BY t.nome ASC, p.nome ASC
    """)

    if request.method == "POST":
        pet_id = request.form.get("pet_id", "").strip()
        data_agendamento = request.form.get("data_agendamento", "").strip()
        hora_agendamento = request.form.get("hora_agendamento", "").strip()
        tipo_servico = request.form.get("tipo_servico", "").strip()
        status = request.form.get("status", "Agendado").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not pet_id or not data_agendamento or not hora_agendamento or not tipo_servico:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("agendamento_form.html", acao="Editar", agendamento=request.form, pets=pets)

        execute_db("""
            UPDATE agendamento
            SET pet_id = ?, data_agendamento = ?, hora_agendamento = ?, tipo_servico = ?, status = ?, observacoes = ?
            WHERE id = ?
        """, [pet_id, data_agendamento, hora_agendamento, tipo_servico, status, observacoes, id])

        flash(f"Agendamento #{id} atualizado com sucesso no banco de dados!", "success")
        return redirect(url_for("agendamentos"))

    return render_template("agendamento_form.html", acao="Editar", agendamento=dict(agendamento), pets=pets)

if __name__ == "__main__":
    print("==================================================================")
    print(" Sistema de Gestão da Clínica Veterinária (SAEP) em execução!    ")
    print(" Acesse no seu navegador: http://127.0.0.1:5000                   ")
    print(" Credenciais de teste:                                            ")
    print("   E-mail: camila.vet@clinica.com  | Senha: admin123              ")
    print("   E-mail: recepcao@clinica.com    | Senha: recepcao123           ")
    print("==================================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
