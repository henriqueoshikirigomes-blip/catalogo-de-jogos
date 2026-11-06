import os
import sqlite3
from flask import Flask, render_template_string, request, jsonify

# ==============================================================================
# 1. GESTÃO DO BANCO DE DADOS (SQLite)
# ==============================================================================

DB_NAME = "jogos.db"

def conectar_bd():
    """Conecta ao banco de dados e cria a tabela caso não exista."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            plataforma TEXT NOT NULL,
            genero TEXT NOT NULL,
            concluido INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn

# ==============================================================================
# 2. SISTEMA EM TERMINAL (CLI - PROMPT DE COMANDO)
# ==============================================================================

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def cli_cadastrar_jogo():
    limpar_tela()
    print("=== CADASTRO DE JOGO ===")
    titulo = input("Título do jogo: ").strip()
    plataforma = input("Plataforma (ex: PC, PS5, Switch): ").strip()
    genero = input("Gênero (ex: RPG, Ação, Indie): ").strip()
    
    concluido_in = input("Já foi concluído? (s/n): ").strip().lower()
    concluido = 1 if concluido_in == 's' else 0

    if not titulo or not plataforma or not genero:
        print("\n[!] Todos os campos são obrigatórios.")
        input("\nPressione ENTER para voltar ao menu...")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jogos (titulo, plataforma, genero, concluido) VALUES (?, ?, ?, ?)",
        (titulo, plataforma, genero, concluido)
    )
    conn.commit()
    conn.close()
    
    print("\nJogo cadastrado com sucesso!")
    input("\nPressione ENTER para voltar ao menu...")

def cli_listar_jogos():
    limpar_tela()
    print("=== LISTA DE JOGOS CADASTRADOS ===")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma, genero, concluido FROM jogos")
    jogos = cursor.fetchall()
    conn.close()

    if not jogos:
        print("Nenhum jogo cadastrado ainda.")
    else:
        for j in jogos:
            status = "Concluído" if j['concluido'] == 1 else "Em andamento"
            print(f"ID: {j['id']} | Título: {j['titulo']} | Plataforma: {j['plataforma']} | Gênero: {j['genero']} | Status: {status}")
    
    input("\nPressione ENTER para voltar ao menu...")

def cli_pesquisar_jogos():
    limpar_tela()
    print("=== PESQUISAR JOGOS ===")
    termo = input("Digite o título ou parte dele: ").strip()
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma, genero, concluido FROM jogos WHERE titulo LIKE ?", (f"%{termo}%",))
    resultados = cursor.fetchall()
    conn.close()

    print("\n--- Resultados Encontrados ---")
    if not resultados:
        print("Nenhum jogo encontrado com esse termo.")
    else:
        for j in resultados:
            status = "Concluído" if j['concluido'] == 1 else "Em andamento"
            print(f"ID: {j['id']} | Título: {j['titulo']} | Plataforma: {j['plataforma']} | Gênero: {j['genero']} | Status: {status}")
            
    input("\nPressione ENTER para voltar ao menu...")

def cli_marcar_concluido():
    limpar_tela()
    print("=== MARCAR JOGO COMO CONCLUÍDO ===")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, plataforma FROM jogos WHERE concluido = 0")
    pendentes = cursor.fetchall()

    if not pendentes:
        print("Não há jogos pendentes para concluir.")
        conn.close()
        input("\nPressione ENTER para voltar ao menu...")
        return

    for j in pendentes:
        print(f"ID: {j['id']} | {j['titulo']} ({j['plataforma']})")
        
    try:
        jogo_id = int(input("\nDigite o ID do jogo que deseja marcar como concluído: "))
        cursor.execute("UPDATE jogos SET concluido = 1 WHERE id = ?", (jogo_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print("\nStatus atualizado para CONCLUÍDO com sucesso!")
        else:
            print("\nID não encontrado.")
    except ValueError:
        print("\nEntrada inválida! Digite apenas números.")
    
    conn.close()
    input("\nPressione ENTER para voltar ao menu...")

def cli_gerar_estatisticas():
    limpar_tela()
    print("=== ESTATÍSTICAS DO CATÁLOGO ===")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jogos")
    total = cursor.fetchone()[0]

    if total == 0:
        print("Cadastre alguns jogos primeiro para gerar estatísticas.")
    else:
        cursor.execute("SELECT COUNT(*) FROM jogos WHERE concluido = 1")
        concluidos = cursor.fetchone()[0]
        pendentes = total - concluidos
        porcentagem = (concluidos / total) * 100

        cursor.execute("SELECT genero, COUNT(*) as qtd FROM jogos GROUP BY genero")
        generos = cursor.fetchall()
        
        print(f"Total de jogos cadastrados: {total}")
        print(f"Jogos concluídos: {concluidos} ({porcentagem:.1f}%)")
        print(f"Jogos pendentes: {pendentes}")
        print("\nDistribuição por Gênero:")
        for gen in generos:
            print(f"  - {gen['genero']}: {gen['qtd']} jogo(s)")

    conn.close()
    input("\nPressione ENTER para voltar ao menu...")

def executar_cli():
    while True:
        limpar_tela()
        print("==============================")
        print("    CATÁLOGO DE JOGOS (CLI)    ")
        print("==============================")
        print("1. Cadastrar Jogo")
        print("2. Listar Todos os Jogos")
        print("3. Pesquisar Jogo")
        print("4. Marcar Jogo como Concluído")
        print("5. Gerar Estatísticas")
        print("6. Voltar ao Menu Principal")
        print("==============================")
        
        opcao = input("Escolha uma opção (1-6): ").strip()
        
        if opcao == '1':
            cli_cadastrar_jogo()
        elif opcao == '2':
            cli_listar_jogos()
        elif opcao == '3':
            cli_pesquisar_jogos()
        elif opcao == '4':
            cli_marcar_concluido()
        elif opcao == '5':
            cli_gerar_estatisticas()
        elif opcao == '6':
            break

# ==============================================================================
# 3. SISTEMA WEB (FLASK + HTML EMBUTIDO)
# ==============================================================================

app = Flask(__name__)

HTML_WEB = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Jogos Python Web</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #0f0c1b; color: #e2e8f0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #00f2fe; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0,242,254,0.3); }
        h2 { color: #4facfe; margin-bottom: 15px; }
        .card { background-color: #181528; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #2a2440; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .form-group { display: flex; gap: 10px; flex-wrap: wrap; }
        input, button { padding: 12px; border-radius: 6px; border: 1px solid #362f54; background: #0f0c1b; color: #fff; outline: none; }
        input:focus { border-color: #00f2fe; }
        input[type="text"] { flex: 1; }
        button { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: #0f0c1b; font-weight: bold; cursor: pointer; border: none; transition: transform 0.2s, opacity 0.2s; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        .grid-jogos { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }
        .jogo-item { background: #0f0c1b; padding: 15px; border-radius: 8px; border-left: 5px solid #ff0055; transition: transform 0.2s; }
        .jogo-item:hover { transform: translateY(-2px); }
        .jogo-item.concluido { border-left-color: #00f2fe; }
        .jogo-item h3 { color: #fff; margin-bottom: 8px; }
        .jogo-item p { color: #a0aec0; font-size: 0.9em; margin-bottom: 4px; }
        .jogo-item button { margin-top: 10px; width: 100%; padding: 8px; font-size: 0.85em; }
        .stats-box { display: flex; justify-content: space-around; text-align: center; }
        .stat-item { background: #0f0c1b; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; border: 1px solid #2a2440; }
        .stat-item p { color: #a0aec0; }
        .stat-item span { font-size: 1.8em; color: #00f2fe; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <h1>🎮Catálogo de Jogos🎮</h1>
    <div class="card">
        <h2>Cadastrar Jogo</h2>
        <form id="form-cadastrar" class="form-group">
            <input type="text" id="titulo" placeholder="Título" required>
            <input type="text" id="plataforma" placeholder="Plataforma" required>
            <input type="text" id="genero" placeholder="Gênero" required>
            <button type="submit">Cadastrar</button>
        </form>
    </div>
    <div class="card">
        <h2>Estatísticas</h2>
        <div class="stats-box">
            <div class="stat-item"><p>Total</p><span id="stat-total">0</span></div>
            <div class="stat-item"><p>Concluídos</p><span id="stat-concluidos">0</span></div>
            <div class="stat-item"><p>Pendentes</p><span id="stat-pendentes">0</span></div>
        </div>
    </div>
    <div class="card">
        <h2>Meus Jogos</h2>
        <input type="text" id="pesquisa" placeholder="Pesquisar..." style="width: 100%; margin-bottom: 10px;" oninput="carregarJogos()">
        <div id="grid-jogos" class="grid-jogos"></div>
    </div>
</div>
<script>
    async function carregarJogos() {
        const termo = document.getElementById('pesquisa').value;
        const res = await fetch(`/api/jogos?pesquisa=${encodeURIComponent(termo)}`);
        const jogos = await res.json();
        
        const grid = document.getElementById('grid-jogos');
        grid.innerHTML = '';
        jogos.forEach(j => {
            const item = document.createElement('div');
            item.className = `jogo-item ${j.concluido ? 'concluido' : ''}`;
            item.innerHTML = `
                <h3>${j.titulo}</h3>
                <p>Plataforma: ${j.plataforma}</p>
                <p>Gênero: ${j.genero}</p>
                <p>Status: ${j.concluido ? 'Concluído' : 'Pendente'}</p>
                <button onclick="alternarStatus(${j.id})">${j.concluido ? 'Marcar Pendente' : 'Marcar Concluído'}</button>
            `;
            grid.appendChild(item);
        });
        carregarEstatisticas();
    }
    async function carregarEstatisticas() {
        const res = await fetch('/api/estatisticas');
        const stats = await res.json();
        document.getElementById('stat-total').innerText = stats.total;
        document.getElementById('stat-concluidos').innerText = stats.concluidos;
        document.getElementById('stat-pendentes').innerText = stats.pendentes;
    }
    document.getElementById('form-cadastrar').addEventListener('submit', async (e) => {
        e.preventDefault();
        const titulo = document.getElementById('titulo').value;
        const plataforma = document.getElementById('plataforma').value;
        const genero = document.getElementById('genero').value;
        await fetch('/api/jogos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, plataforma, genero })
        });
        document.getElementById('form-cadastrar').reset();
        carregarJogos();
    });
    async function alternarStatus(id) {
        await fetch(`/api/jogos/${id}/status`, { method: 'PUT' });
        carregarJogos();
    }
    carregarJogos();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_WEB)

@app.route('/api/jogos', methods=['GET'])
def api_listar_jogos():
    termo = request.args.get('pesquisa', '')
    conn = conectar_bd()
    cursor = conn.cursor()
    if termo:
        cursor.execute("SELECT * FROM jogos WHERE titulo LIKE ?", (f"%{termo}%",))
    else:
        cursor.execute("SELECT * FROM jogos")
    jogos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(jogos)

@app.route('/api/jogos', methods=['POST'])
def api_cadastrar_jogo():
    dados = request.get_json()
    titulo = dados.get('titulo')
    plataforma = dados.get('plataforma')
    genero = dados.get('genero')
    if not titulo or not plataforma or not genero:
        return jsonify({'erro': 'Dados incompletos'}), 400

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jogos (titulo, plataforma, genero, concluido) VALUES (?, ?, ?, 0)",
        (titulo, plataforma, genero)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Jogo cadastrado com sucesso!'}), 201

@app.route('/api/jogos/<int:jogo_id>/status', methods=['PUT'])
def api_alterar_status(jogo_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE jogos SET concluido = NOT concluido WHERE id = ?", (jogo_id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Status alterado com sucesso!'})

@app.route('/api/estatisticas', methods=['GET'])
def api_estatisticas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jogos")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jogos WHERE concluido = 1")
    concluidos = cursor.fetchone()[0]
    pendentes = total - concluidos

    cursor.execute("SELECT genero, COUNT(*) as qtd FROM jogos GROUP BY genero")
    generos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({
        'total': total,
        'concluidos': concluidos,
        'pendentes': pendentes,
        'generos': generos
    })

def executar_web():
    limpar_tela()
    print("==========================================")
    print(" INICIANDO SERVIDOR WEB (FLASK)...        ")
    print(" Acesse no navegador: http://127.0.0.1:5000")
    print(" Pressione CTRL+C no terminal para parar. ")
    print("==========================================")
    app.run(debug=True, use_reloader=False)

# ==============================================================================
# 4. MENU PRINCIPAL
# ==============================================================================

if __name__ == '__main__':
    conectar_bd()
    while True:
        limpar_tela()
        print("==========================================")
        print("      SISTEMA DE CATÁLOGO DE JOGOS        ")
        print("==========================================")
        print("1. Executar versão Terminal (Prompt/CLI)")
        print("2. Executar versão Aplicação WEB (Flask)")
        print("3. Sair")
        print("==========================================")
        
        escolha = input("Escolha uma opção (1-3): ").strip()
        
        if escolha == '1':
            executar_cli()
        elif escolha == '2':
            executar_web()
        elif escolha == '3':
            print("\nEncerrando sistema...")
            break