import copy
import random
from interfaces import ISolver, ISolutionCounter
from graph import SudokuGraph

class PuzzleGenerator:
    """
    Responsável por gerar novos puzzles de Sudoku.
    Usa a Injeção de Dependência para desacoplar-se dos algoritmos
    específicos de resolução e contagem.
    """

    def __init__(self, solver: ISolver, counter: ISolutionCounter):
        """
        Inicializa o gerador com as 'ferramentas' necessárias.

        Args:
            solver: Um objeto que implementa ISolver (para criar a solução inicial).
            counter: Um objeto que implementa ISolutionCounter (para verificar a unicidade).
        """
        self.solver = solver
        self.counter = counter

    def gerar_puzzle(self, n: int) -> tuple[list[list[int]], list[list[int]]]:
        """
        Gera um novo puzzle de Sudoku com garantia de solução única.

        Args:
            n: O tamanho do bloco (ex: 3 para 9x9).

        Returns:
            Uma tupla contendo (puzzle, solucao)
        """
        
        # --- Passo 1: Criar a base (Grid e Grafo) ---
        graph = SudokuGraph(n=n)
        grid_vazio = [[0] * graph.tamanho for _ in range(graph.tamanho)]
        
        # --- Passo 2: Gerar uma solução completa [CORRIGIDO] ---
        print("Gerando solução base aleatória...")
        
        # 2a. Introduzir Aleatoriedade: Preencher a primeira linha aleatoriamente
        # Isso garante que o solver gere um tabuleiro diferente a cada execução
        primeira_linha = list(range(1, graph.tamanho + 1))
        random.shuffle(primeira_linha)
        
        for c in range(graph.tamanho):
            grid_vazio[0][c] = primeira_linha[c]
            
        # 2b. Resolver o resto
        # Verificamos se o solver teve sucesso (embora seja quase garantido aqui)
        if not self.solver.solve(grid_vazio, graph):
            raise Exception("Erro: Não foi possível gerar um tabuleiro base.")

        solucao_completa = copy.deepcopy(grid_vazio)
        
        # Este é o grid que vamos "cavar" para criar o puzzle
        puzzle_grid = copy.deepcopy(solucao_completa)
        
        # --- Passo 3: Preparar a Remoção (Poda) ---
        # Cria uma lista de todos os vértices (0 a 80) e a embaralha
        vertices = list(range(graph.num_vertices))
        random.shuffle(vertices)
        
        print(f"Iniciando a 'cavação' de {len(vertices)} células...")
        
        # --- Passo 4: Loop de Remoção e Verificação ---
        for v in vertices:
            (linha, col) = graph.vertice_para_grid(v)
            
            # Guarda o valor caso precisemos desfazer
            valor_removido = puzzle_grid[linha][col]
            
            # Pula se a célula já foi removida (ex: em um puzzle simétrico)
            if valor_removido == 0:
                continue

            # 4a. Tenta remover a pista
            puzzle_grid[linha][col] = 0
            
            # 4b. Verifica a Unicidade
            # É CRUCIAL usar uma cópia, pois o contador modifica o grid!
            grid_para_teste = copy.deepcopy(puzzle_grid)
            
            num_solucoes = self.counter.count_solutions(grid_para_teste, graph)
            
            # 4c. Decide
            if num_solucoes > 1:
                # Se tiver mais de uma solução, a remoção foi inválida.
                # Desfaz a remoção (coloca o número de volta).
                puzzle_grid[linha][col] = valor_removido
            # else:
                # Se num_solucoes == 1, a remoção foi válida! 
                # Deixa a célula como 0 e continua o loop.
        
        print("Geração concluída.")
        return (puzzle_grid, solucao_completa)
