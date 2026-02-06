# Otimização Combinatória – Problemas Clássicos 

Este repositório contém a implementação de diferentes problemas clássicos de Otimização Combinatória desenvolvidos como parte da disciplina.

Cada problema foi implementado manualmente, sem utilização de bibliotecas prontas de otimização, respeitando as regras do trabalho.


## Problemas Implementados

### 1. Mochila Binária
Objetivo: Selecionar um subconjunto de itens que maximize o benefício total sem ultrapassar a capacidade da mochila.

Entrada:
- Capacidade da mochila
- Lista de benefícios
- Lista de custos

Saída:
- Itens selecionados
- Benefício total obtido



### 2. Problema do Caixeiro Viajante (TSP)
Objetivo: Encontrar a rota de menor custo que visite todas as cidades e retorne à origem.

Entrada:
- Número de vértices
- Matriz de adjacência ponderada (grafo não direcionado)

Saída:
- Rota encontrada
- Custo total do percurso



### 3. Problema de Designação Generalizada
Objetivo: Atribuir módulos a programadores minimizando o custo total, respeitando as restrições de carga horária.

Entrada:
- Número de programadores
- Número de módulos
- Matriz de custos
- Matriz de carga horária
- Disponibilidade de horas por programador

Saída:
- Designação final
- Custo total da solução



### 4. Empacotamento Unidimensional
Objetivo: Minimizar o número de recipientes necessários para acomodar todos os itens.

Entrada:
- Capacidade do recipiente
- Número de itens
- Tamanho de cada item

Saída:
- Distribuição dos itens
- Número mínimo de recipientes utilizados



### 5. Conexão de Circuitos
Objetivo: Encontrar a melhor combinação de conexões entre componentes minimizando o comprimento total dos cabos, respeitando restrições de grau mínimo e máximo.

Entrada:
- Número de componentes
- Número total de conexões
- Grau máximo permitido
- Coordenadas dos componentes

Saída:
- Conjunto de conexões
- Soma total das distâncias



### 6. Problema das N-Rainhas
Objetivo: Encontrar uma configuração onde nenhuma rainha ataque outra.

Entrada:
- Número de rainhas
- Posição inicial de cada rainha

Saída:
- Configuração válida final



## Estrutura do Repositório

Cada problema possui:
- Pasta de entradas
- Pasta de saídas
- Pasta com evidências de execução
- Código fonte da implementação



## Linguagem Utilizada

Implementado em: Python 



## Observações

- Nenhum método pronto de otimização foi utilizado.
- As implementações seguem as regras estabelecidas no enunciado.
- Os critérios de parada variam conforme o problema.


## Autor

Pedro Henrique de Oliveira Berti
