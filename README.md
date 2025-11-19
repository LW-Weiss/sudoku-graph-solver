# Análise, Resolução e Geração de Sudokus via Teoria dos Grafos

Este repositório contém a implementação prática dos algoritmos descritos no trabalho de Matemática Discreta sobre modelagem de Sudoku utilizando grafos.

## Sobre o Projeto

O objetivo deste trabalho é demonstrar como a **Teoria dos Grafos** (especificamente o problema de coloração de vértices) pode ser utilizada para:
1. Modelar as restrições do Sudoku.
2. Resolver instâncias de forma eficiente usando **Smart Backtracking**.
3. Gerar novos tabuleiros válidos com garantia de unicidade de solução.

## Funcionalidades Implementadas

- **Modelagem de Grafo:** Representação do tabuleiro $N \times N$ como um grafo não-direcionado $G=(V,E)$.
- **Naive Backtracking:** Algoritmo de força bruta para resolução do sudoku.
- **Smart Backtracking (MRV):** Algoritmo otimizado com heurística *Minimum Remaining Values* e *Forward Checking* para resolução rápida.
- **Gerador de Puzzles:** Algoritmo subtrativo que remove pistas mantendo a unicidade da solução.

## Estrutura dos Arquivos

- `main.py`: Ponto de entrada. Oferece um menu para gerar ou resolver Sudokus.
- `graph.py`: Implementação da topologia do grafo (Listas de Adjacência).
- `solvers.py`: Implementação dos algoritmos de resolução e verificação.
- `generator.py`: Lógica de geração e poda de tabuleiros.
- `interfaces.py`: Classes abstratas para garantir o desacoplamento do código.
- `utils.py`: Funções auxiliares de impressão e validação.

## Como Executar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/LW-Weiss/sudoku-graph-solver.git](https://github.com/LW-Weiss/sudoku-graph-solver.git)
   cd sudoku-graph-solver
