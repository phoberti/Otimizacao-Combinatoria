import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")


def ler_instancia(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f if l.strip()]

    capacidade = int(linhas[0])
    n = int(linhas[1])
    itens = [int(x) for x in linhas[2].split()]

    if len(itens) != n:
        raise ValueError("Quantidade de itens diferente do informado")

    return capacidade, itens


def first_fit(capacidade, itens):
    bins = []

    for item in itens:
        colocado = False
        for b in bins:
            if sum(b) + item <= capacidade:
                b.append(item)
                colocado = True
                break
        if not colocado:
            bins.append([item])

    return bins


def pior_solucao(itens):
    return [[item] for item in itens]


def gerar_vizinho(bins, capacidade):
    novo = [b[:] for b in bins]

    # escolhe bin e item
    b_idx = random.randrange(len(novo))
    item_idx = random.randrange(len(novo[b_idx]))
    item = novo[b_idx].pop(item_idx)

    # remove bin vazio
    if len(novo[b_idx]) == 0:
        novo.pop(b_idx)

    # tenta colocar em outro bin
    random.shuffle(novo)
    colocado = False
    for b in novo:
        if sum(b) + item <= capacidade:
            b.append(item)
            colocado = True
            break

    if not colocado:
        novo.append([item])

    return novo


def busca_local(bins_inicial, capacidade, max_iter=50000):
    melhor = bins_inicial
    melhor_custo = len(melhor)

    atual = bins_inicial
    sem_melhora = 0

    for _ in range(max_iter):
        viz = gerar_vizinho(atual, capacidade)
        c = len(viz)

        if c < melhor_custo:
            melhor = viz
            melhor_custo = c
            atual = viz
            sem_melhora = 0
        else:
            sem_melhora += 1

        if sem_melhora > 5000:
            break

    return melhor


def salvar_saida(caminho, bins, capacidade):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"Número de recipientes: {len(bins)}\n\n")
        for i, b in enumerate(bins, 1):
            f.write(f"Recipiente {i}: {b} | soma = {sum(b)}\n")
        f.write(f"\nCapacidade dos recipientes: {capacidade}\n")


if __name__ == "__main__":
    os.makedirs(PASTA_SAIDAS, exist_ok=True)

    
    nome_arquivo = "PEU5.txt"  

    caminho_entrada = os.path.join(PASTA_ENTRADAS, nome_arquivo)
    capacidade, itens = ler_instancia(caminho_entrada)

    # escolha solução inicial
    bins0 = first_fit(capacidade, itens)
    # bins0 = pior_solucao(itens)

    melhor = busca_local(bins0, capacidade)

    nome_base = nome_arquivo.replace(".txt", "")
    caminho_saida = os.path.join(PASTA_SAIDAS, f"4_empacotamento_{nome_base}_saida.txt")

    salvar_saida(caminho_saida, melhor, capacidade)

    print(f"[OK] {nome_arquivo}")
    print(f"Recipientes usados: {len(melhor)}")
    print(f"Saída: {caminho_saida}")
