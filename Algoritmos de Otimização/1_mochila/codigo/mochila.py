import os
import random

#  caminhos projeto  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADAS = os.path.join(BASE_DIR, "..", "entradas")
PASTA_SAIDAS = os.path.join(BASE_DIR, "..", "saidas")


def ler_instancia(caminho: str):
    #Le o arquivo no formato
    #linha1 capacidade
    #linha2 beneficio
    #linha3 custos
    
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [ln.strip() for ln in f if ln.strip()]

    capacidade = int(linhas[0])

    beneficios = [int(x) for x in linhas[1].split()]
    custos = [int(x) for x in linhas[2].split()]

    if len(beneficios) != len(custos):
        raise ValueError("Quantidade de benefícios != quantidade de custos")

    return capacidade, beneficios, custos


def avalia(sol, beneficios, custos):
    #Retorna beneficio_total e custo_total
    bt = 0
    ct = 0
    for i, b in enumerate(sol):
        if b:
            bt += beneficios[i]
            ct += custos[i]
    return bt, ct


def reparar(sol, capacidade, beneficios, custos):
    #Se estourar a capacidade remove itens ate ficar viavel
    #heuristica remove primeiro o pior 'benefício por custo' entre os selecionados
    
    bt, ct = avalia(sol, beneficios, custos)
    if ct <= capacidade:
        return sol

    # lista itens selecionados com "densidade" b/c
    selecionados = []
    for i, bit in enumerate(sol):
        if bit:
            if custos[i] == 0:
                dens = float("inf")  # nunca remover um item de custo zero se foi escolhido
            else:
                dens = beneficios[i] / custos[i]
            selecionados.append((dens, i))

    # remove os de menor densidade primeiro
    selecionados.sort()  # menor densidade no começo

    k = 0
    while ct > capacidade and k < len(selecionados):
        _, i = selecionados[k]
        if sol[i] == 1:
            sol[i] = 0
            bt, ct = avalia(sol, beneficios, custos)
        k += 1

    return sol


def solucao_inicial_aleatoria(n, capacidade, beneficios, custos):
    sol = [random.randint(0, 1) for _ in range(n)]
    sol = reparar(sol, capacidade, beneficios, custos)
    return sol


def vizinho_flip(sol):
    #Inverte 1 bit aleatorio
    n = len(sol)
    v = sol[:]
    i = random.randrange(n)
    v[i] = 1 - v[i]
    return v


def busca_local(capacidade, beneficios, custos, max_iter=200000, reinicios=30):
    n = len(beneficios)

    melhor = None
    melhor_benef = -1
    melhor_custo = None

    for _r in range(reinicios):
        sol = solucao_inicial_aleatoria(n, capacidade, beneficios, custos)
        b, c = avalia(sol, beneficios, custos)

        if b > melhor_benef:
            melhor, melhor_benef, melhor_custo = sol[:], b, c

        # hill climbing com reparo
        sem_melhora = 0
        for _ in range(max_iter):
            v = vizinho_flip(sol)
            v = reparar(v, capacidade, beneficios, custos)
            vb, vc = avalia(v, beneficios, custos)

            if vb > b:  
                sol = v
                b, c = vb, vc
                sem_melhora = 0

                if b > melhor_benef:
                    melhor, melhor_benef, melhor_custo = sol[:], b, c
            else:
                sem_melhora += 1

            # criterio de convergência 
            if sem_melhora > 5000:
                break

    return melhor, melhor_benef, melhor_custo


def salvar_saida(caminho_saida, sol, melhor_benef, melhor_custo, capacidade):
    itens = [str(i + 1) for i, bit in enumerate(sol) if bit == 1]  # 1-indexado

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("Itens selecionados (1-indexado):\n")
        f.write(" ".join(itens) + "\n\n")
        f.write(f"Benefício total: {melhor_benef}\n")
        f.write(f"Custo total: {melhor_custo}\n")
        f.write(f"Capacidade: {capacidade}\n")


if __name__ == "__main__":
    os.makedirs(PASTA_SAIDAS, exist_ok=True)

    
    nome_arquivo = "Mochila1000.txt"  

    caminho_entrada = os.path.join(PASTA_ENTRADAS, nome_arquivo)
    capacidade, beneficios, custos = ler_instancia(caminho_entrada)

    sol, b, c = busca_local(
        capacidade, beneficios, custos,
        max_iter=200000,
        reinicios=30
    )

    nome_base = nome_arquivo.replace(".txt", "")
    caminho_saida = os.path.join(PASTA_SAIDAS, f"1_mochila_{nome_base}_saida.txt")

    salvar_saida(caminho_saida, sol, b, c, capacidade)

    print(f"[OK] {nome_arquivo}")
    print(f"Benefício = {b} | Custo = {c} | Capacidade = {capacidade}")
    print(f"Saída: {caminho_saida}")
