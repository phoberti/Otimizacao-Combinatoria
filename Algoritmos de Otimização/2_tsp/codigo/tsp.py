import os
import random
import time
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")



# tempo total por instancia 
TIME_LIMIT_S = 20.0

# tentativas de reinicio dentro do tempo
MAX_RESTARTS = 10




def ler_instancia(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f if l.strip()]

    n = int(linhas[0])
    mat = []
    for i in range(1, n + 1):
        row = [int(x) for x in linhas[i].split()]
        if len(row) != n:
            raise ValueError("Linha da matriz com tamanho incorreto.")
        mat.append(row)
    return n, mat


def build_adj(n, mat):
    #Lista de adjacencia apenas arestas com peso > 0
    adj = [[] for _ in range(n)]
    for i in range(n):
        row = mat[i]
        for j, w in enumerate(row):
            if i != j and w > 0:
                adj[i].append(j)
    return adj


def check_necessario(n, adj):
    #condicoes   para existir ciclo Hamiltoniano em grafo não direcionado
    # grau >= 2
    low_deg = [i for i in range(n) if len(adj[i]) < 2]

    # conectividade (BFS)
    if n == 0:
        return low_deg, False

    start = 0
    # se start for isolado BFS ja acusa
    vis = [False] * n
    q = deque([start])
    vis[start] = True
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not vis[v]:
                vis[v] = True
                q.append(v)
    connected = all(vis)

    return low_deg, connected


def aresta(mat, a, b):
    return mat[a][b] > 0


def custo_tour(tour, mat):
    total = 0
    n = len(tour)
    for i in range(n):
        a = tour[i]
        b = tour[(i + 1) % n]
        w = mat[a][b]
        if w == 0:
            return None
        total += w
    return total


def salvar_saida_ok(caminho, tour, custo):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("Rota encontrada (1-indexado):\n")
        tour1 = [v + 1 for v in tour] + [tour[0] + 1]
        f.write(" -> ".join(map(str, tour1)) + "\n\n")
        f.write(f"Custo total: {custo}\n")


def salvar_saida_erro(caminho, msg):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("Sem solução encontrada.\n")
        f.write(msg.strip() + "\n")



# Construcao insercao em ciclo (mantem tour  valido)

def encontrar_ciclo_inicial(n, mat, adj, tentativas=20000):
    
    #Acha um ciclo inicial pequeno  triangulo a-b-c-a com arestas existentes
   
    
    for _ in range(tentativas):
        a = random.randrange(n)
        if not adj[a]:
            continue
        b = random.choice(adj[a])
        if not adj[b]:
            continue
        c = random.choice(adj[b])
        if a != b and b != c and c != a and aresta(mat, c, a):
            return [a, b, c]
    return None


def inserir_vertice(tour, x, mat, amostras=80):
   
   # Insere x em alguma aresta (a->b) do tour
   # substitui (a->b) por (a->x) e (x->b)
   # Escolhe posição de menor delta
   # Retorna True se inseriu

    m = len(tour)
    best_pos = None
    best_delta = None

    # amostra posicoes (pra ser rapido)
    tries = min(amostras, m)
    for _ in range(tries):
        i = random.randrange(m)
        a = tour[i]
        b = tour[(i + 1) % m]
        if aresta(mat, a, x) and aresta(mat, x, b):
            delta = mat[a][x] + mat[x][b] - mat[a][b]
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_pos = i + 1

    # = varre tudo se n achou em amostra
    if best_pos is None:
        for i in range(m):
            a = tour[i]
            b = tour[(i + 1) % m]
            if aresta(mat, a, x) and aresta(mat, x, b):
                delta = mat[a][x] + mat[x][b] - mat[a][b]
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best_pos = i + 1

    if best_pos is None:
        return False

    tour.insert(best_pos, x)
    return True


def kick_2opt_valido(tour, mat, tentativas=400):
   
    # tenta aplicar um 2-opt que mantenha validade.
    
    n = len(tour)
    for _ in range(tentativas):
        i = random.randint(0, n - 1)
        k = random.randint(0, n - 1)
        if i == k:
            continue
        if i > k:
            i, k = k, i
        if k - i < 2:
            continue

        a = tour[(i - 1) % n]
        b = tour[i]
        c = tour[k]
        d = tour[(k + 1) % n]

        # novas arestas precisam existir
        if not aresta(mat, a, c):
            continue
        if not aresta(mat, b, d):
            continue

        # aplicar
        tour[i:k+1] = reversed(tour[i:k+1])
        return True
    return False


def construir_tour(n, mat, adj, tempo_limite_s):
  
    #constroe tour valido inserindo todos os vertices em um ciclo
    #Se travar, tenta kicks e  se ainda travar, falha para reiniciar
   
    t0 = time.time()

    tour = encontrar_ciclo_inicial(n, mat, adj)
    if tour is None:
        return None

    in_tour = [False] * n
    for v in tour:
        in_tour[v] = True

    restantes = [v for v in range(n) if not in_tour[v]]
    random.shuffle(restantes)

    falhas = 0
    idx = 0

    # controle de travamento
    while idx < len(restantes):
        if time.time() - t0 > tempo_limite_s:
            return None

        x = restantes[idx]
        ok = inserir_vertice(tour, x, mat, amostras=100)

        if ok:
            in_tour[x] = True
            idx += 1
            falhas = 0
        else:
            falhas += 1
            # tenta kick para mudar pares consecutivos
            if falhas % 10 == 0:
                kick_2opt_valido(tour, mat, tentativas=800)

            # se acumulou muitas falhas seguidas desiste e reinicia
            if falhas > max(40, n // 20):
                return None

            # joga esse vértice pro fim e tenta outro
            restantes.append(restantes.pop(idx))

    # validação final
    if custo_tour(tour, mat) is None:
        return None
    return tour



#  2-opt valido (so se as novas arestas existem)

def melhorar_2opt_valido(tour, mat, time_budget_s=6.0):
    t0 = time.time()
    n = len(tour)
    best_cost = custo_tour(tour, mat)
    if best_cost is None:
        return tour

    sem_melhora = 0
    while time.time() - t0 < time_budget_s:
        i = random.randint(0, n - 1)
        k = random.randint(0, n - 1)
        if i == k:
            continue
        if i > k:
            i, k = k, i
        if k - i < 2:
            continue

        a = tour[(i - 1) % n]
        b = tour[i]
        c = tour[k]
        d = tour[(k + 1) % n]

        # novas arestas precisam existir
        if not aresta(mat, a, c):
            sem_melhora += 1
            continue
        if not aresta(mat, b, d):
            sem_melhora += 1
            continue

        # custo antigo x novo (delta O(1))
        old = mat[a][b] + mat[c][d]
        new = mat[a][c] + mat[b][d]
        if new < old:
            tour[i:k+1] = reversed(tour[i:k+1])
            best_cost -= (old - new)
            sem_melhora = 0
        else:
            sem_melhora += 1

        if sem_melhora > 20000:
            break

    return tour



# Solver principal (com limite de tempo) 

def solve_tsp(n, mat, time_limit_s=20.0):
    adj = build_adj(n, mat)
    low_deg, connected = check_necessario(n, adj)

    # Se falhar em condição ncessaria pode afirmar inviável
    if low_deg:
        return None, f"Instância inviável (necessário): vértices com grau < 2: {len(low_deg)} (ex.: {low_deg[:10]})"
    if not connected:
        return None, "Instância inviável (necessário): grafo desconexo."

    t0 = time.time()
    best = None
    best_cost = None

    restarts = 0
    while time.time() - t0 < time_limit_s and restarts < MAX_RESTARTS:
        restarts += 1

        # dividir tempo construir + melhorar
        remaining = time_limit_s - (time.time() - t0)
        if remaining <= 0:
            break

        build_budget = max(1.0, remaining * 0.55)
        improve_budget = max(1.0, remaining * 0.35)

        tour = construir_tour(n, mat, adj, tempo_limite_s=build_budget)
        if tour is None:
            continue

        tour = melhorar_2opt_valido(tour, mat, time_budget_s=improve_budget)
        c = custo_tour(tour, mat)
        if c is None:
            continue

        if best is None or c < best_cost:
            best = tour[:]
            best_cost = c

        # se ja achou algo não precisa gastar tudo
        if (time.time() - t0) > time_limit_s * 0.85:
            break

    if best is None:
        return None, "Não foi possível encontrar um ciclo Hamiltoniano dentro do limite de tempo. (Pode não existir.)"

    return best, None



if __name__ == "__main__":
    os.makedirs(PASTA_SAIDAS, exist_ok=True)

    nome_arquivo = "Entrada 1500.txt"  
    caminho_entrada = os.path.join(PASTA_ENTRADAS, nome_arquivo)
    n, mat = ler_instancia(caminho_entrada)

    tour, erro = solve_tsp(n, mat, time_limit_s=TIME_LIMIT_S)

    out = os.path.join(PASTA_SAIDAS, f"2_tsp_{nome_arquivo.replace('.txt','')}_saida.txt")

    if tour is None:
        print("[ERRO]", erro)
        salvar_saida_erro(out, erro)
    else:
        custo = custo_tour(tour, mat)
        salvar_saida_ok(out, tour, custo)
        print(f"[OK] {nome_arquivo}")
        print(f"Custo total: {custo}")
        print(f"Saída: {out}")
