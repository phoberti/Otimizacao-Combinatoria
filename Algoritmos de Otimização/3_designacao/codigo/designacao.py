import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")


# 
# Leitura da instancia
def ler_instancia(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        nums = []
        for ln in f:
            ln = ln.strip()
            if ln:
                nums.extend(map(int, ln.split()))

    idx = 0
    NP = nums[idx]; idx += 1
    NM = nums[idx]; idx += 1

    cost = [nums[idx + i*NM : idx + (i+1)*NM] for i in range(NP)]
    idx += NP * NM

    hours = [nums[idx + i*NM : idx + (i+1)*NM] for i in range(NP)]
    idx += NP * NM

    cap = nums[idx : idx + NP]

    return NP, NM, cost, hours, cap



# Utilidades

def custo_total(assign, cost):
    return sum(cost[assign[m]][m] for m in range(len(assign)))


def calcular_load(assign, NP, hours):
    load = [0] * NP
    for m, p in enumerate(assign):
        load[p] += hours[p][m]
    return load



# Construção + Reparo 

def construir_barato(NP, NM, cost):
    return [min(range(NP), key=lambda p: cost[p][m]) for m in range(NM)]


def reparar(assign, NP, NM, cost, hours, cap):
    load = calcular_load(assign, NP, hours)

    while True:
        violadores = [p for p in range(NP) if load[p] > cap[p]]
        if not violadores:
            return assign, load

        p = max(violadores, key=lambda x: load[x] - cap[x])

        melhor = None
        for m in range(NM):
            if assign[m] != p:
                continue
            for q in range(NP):
                if q == p:
                    continue
                if load[q] + hours[q][m] <= cap[q]:
                    delta = cost[q][m] - cost[p][m]
                    cand = (delta, m, q)
                    if melhor is None or cand < melhor:
                        melhor = cand

        if melhor is None:
            return None

        _, m, q = melhor
        assign[m] = q
        load[p] -= hours[p][m]
        load[q] += hours[q][m]



# Busca Local

def busca_local(NP, NM, cost, hours, cap, reinicios=40):
    melhor = None
    melhor_custo = None
    melhor_load = None

    for _ in range(reinicios):
        assign = construir_barato(NP, NM, cost)

        # perturbação leve
        for _ in range(NM // 4):
            assign[random.randrange(NM)] = random.randrange(NP)

        base = reparar(assign, NP, NM, cost, hours, cap)
        if base is None:
            continue

        assign, load = base
        c = custo_total(assign, cost)

        if melhor is None or c < melhor_custo:
            melhor = assign[:]
            melhor_load = load[:]
            melhor_custo = c

    return melhor, melhor_load, melhor_custo



# Saída

def salvar_saida(caminho, assign, load, cap, cost):
    with open(caminho, "w", encoding="utf-8") as f:
        for m, p in enumerate(assign, 1):
            f.write(f"Módulo {m} -> Programador {p+1}\n")
        f.write(f"\nCusto total: {custo_total(assign, cost)}\n\n")
        for i in range(len(cap)):
            f.write(f"P{i+1}: {load[i]} / {cap[i]}\n")



if __name__ == "__main__":
    os.makedirs(PASTA_SAIDAS, exist_ok=True)

    nome_arquivo = "PDG4.txt"
    caminho = os.path.join(PASTA_ENTRADAS, nome_arquivo)

    NP, NM, cost, hours, cap = ler_instancia(caminho)

    assign, load, total = busca_local(NP, NM, cost, hours, cap)

    if assign is None:
        print("[ERRO] Nenhuma solução viável encontrada.")
    else:
        out = os.path.join(PASTA_SAIDAS, f"3_designacao_{nome_arquivo.replace('.txt','')}_saida.txt")
        salvar_saida(out, assign, load, cap, cost)
        print("[OK]", nome_arquivo)
        print("Custo total:", total)
        print("Saída:", out)
