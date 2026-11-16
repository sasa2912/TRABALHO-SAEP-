import os
import sqlite3
from crypto_utils import encrypt_cpf, hash_user_password

DB_PATH = os.path.join(os.path.dirname(__file__), "saep_db.sqlite")

def get_connection():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def query_db(query, args=(), one=False):
    """Executa uma consulta SELECT no banco de dados e retorna dicionários."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
    finally:
        conn.close()

def execute_db(query, args=()):
    """Executa comandos INSERT, UPDATE ou DELETE e comita a transação."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        rowcount = cur.rowcount
        cur.close()
        return last_id if last_id else rowcount
    finally:
        conn.close()

def init_db():
    """Inicializa as tabelas e dados no banco de dados SQLite se não existirem."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        cargo TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tutor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        telefone TEXT NOT NULL,
        email TEXT NOT NULL,
        endereco TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tutor_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        especie TEXT NOT NULL,
        raca TEXT NOT NULL,
        data_nascimento TEXT NOT NULL,
        peso REAL NOT NULL,
        observacoes TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tutor_id) REFERENCES tutor (id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agendamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        data_agendamento TEXT NOT NULL,
        hora_agendamento TEXT NOT NULL,
        tipo_servico TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Agendado',
        observacoes TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pet_id) REFERENCES pet (id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) as total FROM usuario")
    if cur.fetchone()[0] == 0:
       
        usuarios = [
            ("Dra. Camila Silveira", "camila.vet@clinica.com", hash_user_password("admin123"), "Médica Veterinária"),
            ("Dr. Roberto Albuquerque", "roberto.vet@clinica.com", hash_user_password("admin123"), "Médico Veterinário"),
            ("Ana Paula Souza", "recepcao@clinica.com", hash_user_password("recepcao123"), "Recepcionista")
        ]
        cur.executemany("INSERT INTO usuario (nome, email, senha, cargo) VALUES (?, ?, ?, ?)", usuarios)

    
        tutores = [
            ("Mariana Fernandes Costa", encrypt_cpf("123.456.789-01"), "(11) 98765-4321", "mariana.costa@email.com", "Rua das Flores, 120 - Jardins, São Paulo/SP"),
            ("Carlos Eduardo Santos", encrypt_cpf("234.567.890-12"), "(11) 97654-3210", "carlos.santos@email.com", "Av. Paulista, 1500, Apto 82 - Bela Vista, São Paulo/SP"),
            ("Beatriz Lima Oliveira", encrypt_cpf("345.678.901-23"), "(11) 96543-2109", "beatriz.oliveira@email.com", "Rua dos Pinheiros, 450 - Pinheiros, São Paulo/SP"),
            ("Rodrigo Mendes Rocha", encrypt_cpf("456.789.012-34"), "(11) 95432-1098", "rodrigo.rocha@email.com", "Rua Augusta, 980 - Consolação, São Paulo/SP")
        ]
        cur.executemany("INSERT INTO tutor (nome, cpf, telefone, email, endereco) VALUES (?, ?, ?, ?, ?)", tutores)

        pets = [
            (1, "Thor", "Canina", "Golden Retriever", "2021-04-10", 32.50, "Dócil e brincalhão. Alergia leve a pulgas, acompanhamento dermatológico."),
            (1, "Luna", "Felina", "Siamês", "2022-08-15", 4.20, "Muito calma. Carteira de vacinação rigorosamente em dia."),
            (2, "Bob", "Canina", "Poodle Toy", "2020-01-20", 5.80, "Cardiopata leve, necessita acompanhamento periódico e exames regulares."),
            (3, "Mel", "Felina", "Persa", "2023-02-11", 3.90, "Pelagem longa, cuidados oftalmológicos preventivos diários."),
            (4, "Pipoca", "Ave", "Calopsita", "2022-11-05", 0.09, "Necessita de corte periódico preventivo das penas das asas.")
        ]
        cur.executemany("INSERT INTO pet (tutor_id, nome, especie, raca, data_nascimento, peso, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)", pets)

        agendamentos = [
            (1, "2026-11-20", "09:00", "Consulta Clínica Geral", "Confirmado", "Check-up semestral completo e pesagem de rotina."),
            (2, "2026-11-20", "10:30", "Vacinação Antirrábica e V5", "Agendado", "Reforço anual de vacinas quádrupla e antirrábica."),
            (3, "2026-11-21", "14:00", "Exame Cardiológico / Ecodoppler", "Confirmado", "Avaliação periódica com cardiologista veterinário."),
            (4, "2026-11-22", "11:00", "Limpeza de Tártaro / Profilaxia", "Agendado", "Procedimento odontológico com anestesia inalatória."),
            (5, "2026-11-23", "16:00", "Consulta Especializada de Aves", "Agendado", "Aparar penas e verificar saúde geral das penas e bico.")
        ]
        cur.executemany("INSERT INTO agendamento (pet_id, data_agendamento, hora_agendamento, tipo_servico, status, observacoes) VALUES (?, ?, ?, ?, ?, ?)", agendamentos)

        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados SQLite inicializado com sucesso!")
