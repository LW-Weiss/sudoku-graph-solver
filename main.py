import time
from graph import SudokuGraph
from solvers import NaiveBacktrackingSolver, BacktrackingCounter
from generator import PuzzleGenerator
from utils import imprimir_grid, validar_grid_inicial, adicionar_sudoku_nsxns



import time
from graph import SudokuGraph
from solvers import NaiveBacktrackingSolver, SmartBacktrackingSolver, BacktrackingCounter
from generator import PuzzleGenerator
from utils import imprimir_grid, validar_grid_inicial

def caso_gerar_sudoku():
    print("\n=== MODO: GERAR NOVO SUDOKU ===")
    N_VALOR = 3 # Sudoku 9x9
    
    # 1. Instanciação
    print("Instanciando componentes...")
    graph = SudokuGraph(n=N_VALOR)
    
    # Usamos o Smart para gerar a solução base
    solver = SmartBacktrackingSolver() 
    # Usamos o Counter (baseado no Naive) para garantir unicidade na poda
    counter = BacktrackingCounter()     
    
    generator = PuzzleGenerator(solver, counter)
    
    # 2. Execução
    print("Gerando puzzle (isso pode levar alguns segundos durante a poda)...")
    start_time = time.time()
    
    puzzle, solucao = generator.gerar_puzzle(N_VALOR)
    
    end_time = time.time()
    
    # 3. Resultados
    print(f"\n--- Puzzle Gerado (em {end_time - start_time:.4f}s) ---")
    imprimir_grid(puzzle, N_VALOR)
    
    print("\n--- Solução do Puzzle ---")
    imprimir_grid(solucao, N_VALOR)
    
    # 4. Estatísticas
    pistas = sum(row.count(0) for row in puzzle)
    pistas_restantes = (N_VALOR**4) - pistas
    print(f"\nEstatísticas: {pistas_restantes} pistas restantes.")


def caso_resolver_existente():
    print("\n=== MODO: RESOLVER SUDOKU EXISTENTE ===")
    N_VALOR = 3
    
    # Sudoku de exemplo, onde 0 representa células vazias
    sudoku_dificil = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 0, 8, 5],
        [0, 0, 1, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 5, 0, 7, 0, 0, 0],
        [0, 0, 4, 0, 0, 0, 1, 0, 0],
        [0, 9, 0, 0, 0, 0, 0, 0, 0],
        [5, 0, 0, 0, 0, 0, 0, 7, 3],
        [0, 0, 2, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 4, 0, 0, 0, 9]
    ]

    print("Tabuleiro de Entrada:")
    imprimir_grid(sudoku_dificil, N_VALOR)
    
    # 1. Instanciação
    graph = SudokuGraph(n=N_VALOR)
    
    # Aqui podemos escolher entre Naive ou Smart.
    # O Smart é recomendado para resolver instâncias difíceis.
    solver = SmartBacktrackingSolver() 
    
    # 2. Validação
    print("\nValidando consistência inicial...")
    if not validar_grid_inicial(sudoku_dificil, graph):
        print("O tabuleiro fornecido é inválido (tem conflitos iniciais)!")
        return

    # 3. Resolução
    print("Resolvendo...")
    start_time = time.time()
    
    sucesso = solver.solve(sudoku_dificil, graph)
    
    end_time = time.time()
    
    # 4. Resultados
    if sucesso:
        print(f"\n--- Solução Encontrada (em {end_time - start_time:.4f}s) ---")
        imprimir_grid(sudoku_dificil, N_VALOR)
    else:
        print("\nNão foi possível encontrar uma solução para este tabuleiro.")


# --- Bloco Principal ---
if __name__ == "__main__":
    while True:
        print("\n" + "="*30)
        print("   PROJETO SUDOKU & GRAFOS")
        print("="*30)
        print("1. Gerar um novo Sudoku")
        print("2. Resolver um Sudoku existente (Hard)")
        print("0. Sair")
        
        escolha = input("\nEscolha uma opção: ")
        
        if escolha == "1":
            caso_gerar_sudoku()
        elif escolha == "2":
            caso_resolver_existente()
        elif escolha == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")