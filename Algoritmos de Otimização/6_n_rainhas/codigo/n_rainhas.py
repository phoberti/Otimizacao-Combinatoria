import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")




def ler_instancia(caminho: str):
    with open(caminho, "r", encoding="utf-8") as f:
        nums = []
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            # pega todos os inteiros na linha (separados por espaco
            partes = linha.split()
            for p in partes:
                nums.append(int(p))

    n = nums[0]
    pos = nums[1:1+n]
    if len(pos) != n:
        raise ValueError(f"Esperava {n} posições, mas achei {len(pos)} no arquivo {caminho}")
    return n, pos  # pos é 1-indexado 
def conflitos_total(pos):
    # pos: lista tamanho n pos[i] = linha da coluna i 
    n = len(pos)
    c = 0
    for i in range(n):
        for j in range(i+1, n):
            if pos[i] == pos[j]:
                c += 1
            elif abs(pos[i] - pos[j]) == abs(i - j):
                c += 1
    return c

def colunas_em_conflito(pos):
    n = len(pos)
    confl = []
    for i in range(n):
        ri = pos[i]
        ok = True
        for j in range(n):
            if i == j:
                continue
            rj = pos[j]
            if ri == rj or abs(ri - rj) == abs(i - j):
                ok = False
                break
        if not ok:
            confl.append(i)
    return confl

def conflitos_se_colocar(pos, col, linha):
    # quantos conflitos a rainha em (col, linha) teria com as outras
    n = len(pos)
    c = 0
    for j in range(n):
        if j == col:
            continue
        rj = pos[j]
        if linha == rj or abs(linha - rj) == abs(col - j):
            c += 1
    return c

def min_conflicts(pos_inicial, max_passos=200000, reinicios=30):
    n = len(pos_inicial)

    melhor = pos_inicial[:]
    melhor_custo = conflitos_total(melhor)

    for _ in range(reinicios):
        pos = pos_inicial[:]  # começa do arquivo
        custo = conflitos_total(pos)

        # se quiser “embaralhar” um pouco antes de começar pra qndo for arquivo ruim
        
        for _k in range(n // 2):
            col = random.randrange(n)
            pos[col] = random.randint(1, n)

        for _passo in range(max_passos):
            custo = conflitos_total(pos)
            if custo == 0:
                return pos, 0

            confl_cols = colunas_em_conflito(pos)
            if not confl_cols:
                #  custo>0 mas não detectou conflito 
                break

            col = random.choice(confl_cols)

            # acha a melhor linha para essa coluna
            melhor_linhas = []
            best = None
            for linha in range(1, n+1):
                c = conflitos_se_colocar(pos, col, linha)
                if best is None or c < best:
                    best = c
                    melhor_linhas = [linha]
                elif c == best:
                    melhor_linhas.append(linha)

            pos[col] = random.choice(melhor_linhas)

        # guarda melhor tentativa
        custo_final = conflitos_total(pos)
        if custo_final < melhor_custo:
            melhor_custo = custo_final
            melhor = pos[:]

        # reinício: solução aleatória total
        pos_inicial = [random.randint(1, n) for _ in range(n)]

    return melhor, melhor_custo

def salvar_saida(caminho_saida, pos, custo):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("Solução final:\n")
        for i, linha in enumerate(pos, start=1):
            f.write(f"Coluna {i} -> Linha {linha}\n")
        f.write(f"\nNúmero de conflitos: {custo}\n")

if __name__ == "__main__":
    nome_arquivo = "100.txt"  

    caminho_entrada = os.path.join(PASTA_ENTRADAS, nome_arquivo)
    nome_base = nome_arquivo.replace(".txt", "")
    caminho_saida = os.path.join(
        PASTA_SAIDAS,
        f"6_nrainhas_{nome_base}_saida.txt"
    )

    os.makedirs(PASTA_SAIDAS, exist_ok=True)

    n, pos0 = ler_instancia(caminho_entrada)

    sol, custo = min_conflicts(
        pos0,
        max_passos=300000,
        reinicios=40
    )

    salvar_saida(caminho_saida, sol, custo)

    print(f"[OK] {nome_arquivo} -> conflitos = {custo}")
    print(f"Saída gerada em: {caminho_saida}")

