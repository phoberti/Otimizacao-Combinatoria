import os
import random
import math
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")



# Leitura

def parse_float_pt(s: str) -> float:
    # aceita "12,34" ou "12.34"
    s = s.strip().replace(",", ".")
    return float(s)


def ler_instancia(caminho):
  
  #  Formato:
  #    linha 1: N 
  #    linha 2: M 
  #    linha 3: K 
  #    linha 4: coordenadas X)
  #    linha 5: coordenadas Y)
  #

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f if l.strip()]

    if len(linhas) < 5:
        raise ValueError("Arquivo com menos de 5 linhas úteis.")

    n = int(linhas[0])
    m = int(linhas[1])
    k = int(linhas[2])

    xs = [parse_float_pt(x) for x in linhas[3].split()]
    ys = [parse_float_pt(y) for y in linhas[4].split()]

    if len(xs) != n or len(ys) != n:
        raise ValueError("Quantidade de coordenadas diferente de N.")

    return n, m, k, xs, ys



# Distncias

def dist(i, j, xs, ys):
    dx = xs[i] - xs[j]
    dy = ys[i] - ys[j]
    return math.hypot(dx, dy)


def precompute_dists(n, xs, ys):
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = dist(i, j, xs, ys)
            d[i][j] = w
            d[j][i] = w
    return d



# Checagens 

def checagem_rapida(n, m, k):
    # cada nó precisa de pelo menos 1 conexão => soma graus >= n => arestas >= ceil(n/2)
    min_m = (n + 1) // 2
    # grau máximo k => soma graus <= n*k => arestas <= floor(n*k/2)
    max_m = (n * k) // 2
    if m < min_m:
        return False, f"M muito pequeno: precisa M >= ceil(N/2) = {min_m} para todos terem grau>=1."
    if m > max_m:
        return False, f"M muito grande: precisa M <= floor(N*K/2) = {max_m} para respeitar grau<=K."
    if k < 1:
        return False, "K precisa ser >= 1."
    return True, ""



# Representação
# edges: set de tuplas (a,b) com a<b
# deg: lista graus
# custo: soma distâncias




def norm_edge(a, b):
    if a == b:
        return None
    return (a, b) if a < b else (b, a)


def custo_total(edges, D):
    return sum(D[a][b] for (a, b) in edges)


def pode_adicionar_edge(a, b, edges, deg, k):
    e = norm_edge(a, b)
    if e is None:
        return False
    if e in edges:
        return False
    if deg[a] >= k or deg[b] >= k:
        return False
    return True


def adicionar_edge(a, b, edges, deg, D):
    e = norm_edge(a, b)
    edges.add(e)
    deg[a] += 1
    deg[b] += 1
    return D[e[0]][e[1]]


def pode_remover_edge(e, deg):
    a, b = e
    # se um componente tem só 1 conexão, ela não pode ser removida
    if deg[a] <= 1 or deg[b] <= 1:
        return False
    return True


def remover_edge(e, edges, deg, D):
    a, b = e
    edges.remove(e)
    deg[a] -= 1
    deg[b] -= 1
    return D[a][b]




# Solução inicial viável

def construir_inicial(n, m, k, D, tentativas=50):
   
   # constroi solução viavel:
   # 1) garante deg>=1 para todos (conectando nós "zerados" ao melhor possível)
   # 2) completa até M com arestas aleatórias/boas respeitando K
   
    vertices = list(range(n))

    # lista de arestas candidatas ordenadas por distância (para guloso)
    candidatos = []
    for i in range(n):
        for j in range(i + 1, n):
            candidatos.append((D[i][j], i, j))
    candidatos.sort(key=lambda x: x[0])

    for _ in range(tentativas):
        edges = set()
        deg = [0] * n
        custo = 0.0

        # 1) garantir deg>=1
        # Passo A: tenta "casar" nos zerados com arestas baratas
        zerados = set(vertices)

        # percorre arestas da menor para maior e conecta se ajudar
        for w, i, j in candidatos:
            if len(zerados) == 0:
                break
            if (i in zerados) or (j in zerados):
                if deg[i] < k and deg[j] < k:
                    e = (i, j)
                    if e not in edges:
                        edges.add(e)
                        deg[i] += 1
                        deg[j] += 1
                        custo += w
                        zerados.discard(i)
                        zerados.discard(j)
            if len(edges) >= m:
                break

        # se ainda tem zerados conecta cada um ao melhor pssivel
        if len(zerados) > 0:
            ok = True
            for v in list(zerados):
                # achar melhor u com deg[u] < k e aresta não repetida
                achou = False
                for w, i, j in candidatos:
                    if i == v:
                        u = j
                    elif j == v:
                        u = i
                    else:
                        continue
                    if deg[v] < k and deg[u] < k:
                        e = norm_edge(v, u)
                        if e not in edges:
                            edges.add(e)
                            deg[v] += 1
                            deg[u] += 1
                            custo += w
                            achou = True
                            break
                if not achou:
                    ok = False
                    break
            if not ok:
                continue

        #  completar até M
        if len(edges) > m:
            #  se passou reinicia
            continue

        # tenta adicionar arestas das mais curtas primeiro
        for w, i, j in candidatos:
            if len(edges) == m:
                break
            if pode_adicionar_edge(i, j, edges, deg, k):
                edges.add((i, j))
                deg[i] += 1
                deg[j] += 1
                custo += w

        if len(edges) == m and all(dg >= 1 for dg in deg):
            return edges, deg, custo

    return None



# Vizinhança 
# remove uma conexão aleatória removivel e troca por outra nova



def gerar_vizinho(edges, deg, custo, n, m, k, D, max_tentativas=2000):
    edges_list = list(edges)

    # tenta achar uma aresta removível
    for _ in range(max_tentativas):
        e_rem = random.choice(edges_list)
        if not pode_remover_edge(e_rem, deg):
            continue

        a_old, b_old = e_rem

        # remove temporariamente
        new_edges = set(edges)
        new_deg = deg[:]
        new_custo = custo - D[a_old][b_old]
        remover_edge(e_rem, new_edges, new_deg, D)

        # tenta adicionar nova aresta válida
        for _ in range(max_tentativas):
            a = random.randrange(n)
            b = random.randrange(n)
            if a == b:
                continue

            # regra: pelo menos um componente diferente dos dois anteriores
            # (não pode ser exatamente a mesma dupla; e não pode usar os mesmos dois ao mesmo tempo)
      
            if (a == a_old and b == b_old) or (a == b_old and b == a_old):
                continue

            if pode_adicionar_edge(a, b, new_edges, new_deg, k):
                adicionar_edge(a, b, new_edges, new_deg, D)
                new_custo += D[min(a, b)][max(a, b)]
                # garante ainda deg>=1 (já garantido pois só removemos removível)
                return new_edges, new_deg, new_custo

        # se não conseguiu adicionar, tenta outra aresta para remover
    return None



# Busca local com tempo limite + reinícios


def busca_local(n, m, k, D, time_limit_s=12.0, reinicios=30):
    t0 = time.time()

    melhor = None
    melhor_custo = float("inf")

    for _r in range(reinicios):
        if time.time() - t0 > time_limit_s:
            break

        init = construir_inicial(n, m, k, D, tentativas=30)
        if init is None:
            continue
        edges, deg, custo = init

        # hill-climbing com  aceitação de piora
        T = 0.5  # temperatura inicial
        sem_melhora = 0

        while time.time() - t0 <= time_limit_s:
            viz = gerar_vizinho(edges, deg, custo, n, m, k, D, max_tentativas=2000)
            if viz is None:
                break

            e2, d2, c2 = viz
            delta = c2 - custo

            aceita = False
            if delta < 0:
                aceita = True
            else:
                # aceita piora pequena com probabilidade
               
                prob = math.exp(-delta / max(1e-9, T))
                if random.random() < prob:
                    aceita = True

            if aceita:
                edges, deg, custo = e2, d2, c2

            # resfriamento leve
            T *= 0.9995

            if custo < melhor_custo:
                melhor = (edges, deg, custo)
                melhor_custo = custo
                sem_melhora = 0
            else:
                sem_melhora += 1
                if sem_melhora > 8000:
                    break

    return melhor



# Saída


def salvar_saida(caminho_saida, edges, custo):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("Conexões (1-indexado):\n")
        # ordena por (a,b)
        for a, b in sorted(edges):
            f.write(f"{a+1} {b+1}\n")
        f.write(f"\nSoma total das distâncias: {custo:.6f}\n")



if __name__ == "__main__":
    os.makedirs(PASTA_SAIDAS, exist_ok=True)

  
    nome_arquivo = "Circuito5.txt"

    caminho_entrada = os.path.join(PASTA_ENTRADAS, nome_arquivo)
    n, m, k, xs, ys = ler_instancia(caminho_entrada)

    ok, msg = checagem_rapida(n, m, k)
    if not ok:
        print("[ERRO]", msg)
        raise SystemExit(1)

    D = precompute_dists(n, xs, ys)

    sol = busca_local(n, m, k, D, time_limit_s=15.0, reinicios=40)

    if sol is None:
        print("[ERRO] Não foi possível construir solução viável (restrições muito apertadas?).")
        raise SystemExit(1)

    edges, deg, custo = sol

    # checagem final
    if len(edges) != m or any(dg < 1 or dg > k for dg in deg):
        print("[ERRO] Solução inválida gerada (bug).")
        raise SystemExit(1)

    out = os.path.join(PASTA_SAIDAS, f"5_circuitos_{nome_arquivo.replace('.txt','')}_saida.txt")
    salvar_saida(out, edges, custo)

    print(f"[OK] {nome_arquivo}")
    print(f"Distância total: {custo:.6f}")
    print(f"Saída: {out}")
