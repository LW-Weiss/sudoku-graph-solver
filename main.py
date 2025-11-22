import time
from graph import SudokuGraph
from solvers import NaiveBacktrackingSolver, SmartBacktrackingSolver, BacktrackingCounter
from generator import PuzzleGenerator
from utils import imprimir_grid, validar_grid_inicial, adicionar_sudoku_nsxns

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
    
    try:
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
        
    except Exception as e:
        print(f"\nErro ao gerar puzzle: {e}")


def caso_resolver_existente():
    print("\n=== MODO: RESOLVER SUDOKU EXISTENTE (HARDCODED) ===")
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
    
    resolver_generico(sudoku_dificil, N_VALOR)


def caso_adicionar_manual():
    print("\n=== MODO: ADICIONAR SUDOKU MANUALMENTE ===")
    try:
        n_str = input("Digite a ordem do Sudoku (ex: 3 para 9x9, 2 para 4x4): ")
        N_VALOR = int(n_str)
    except ValueError:
        print("Entrada inválida. Usando padrão n=3 (9x9).")
        N_VALOR = 3

    print(f"\nIniciando entrada para grid {N_VALOR**2}x{N_VALOR**2}...")
    
    # Chama a função de input do utils
    sudoku_usuario = adicionar_sudoku_nsxns(N_VALOR)
    
    print("\nTabuleiro Inserido:")
    imprimir_grid(sudoku_usuario, N_VALOR)
    
    resolver_generico(sudoku_usuario, N_VALOR)


def resolver_generico(grid, n_valor):
    """Função auxiliar para resolver qualquer grid passado."""
    # 1. Instanciação
    graph = SudokuGraph(n=n_valor)
    
    # Usar SmartSolver para performance
    solver = SmartBacktrackingSolver() 
    
    # 2. Validação
    print("\nValidando consistência inicial...")
    if not validar_grid_inicial(grid, graph):
        print("O tabuleiro fornecido é inválido (tem conflitos iniciais)!")
        return

    # 3. Resolução
    print("Resolvendo...")
    start_time = time.time()
    
    sucesso = solver.solve(grid, graph)
    
    end_time = time.time()
    
    # 4. Resultados
    if sucesso:
        print(f"\n--- Solução Encontrada (em {end_time - start_time:.4f}s) ---")
        imprimir_grid(grid, n_valor)
    else:
        print("\nNão foi possível encontrar uma solução para este tabuleiro.")


# --- Bloco Principal ---
if __name__ == "__main__":
    while True:
        print("\n" + "="*30)
        print("   PROJETO SUDOKU & GRAFOS")
        print("="*30)
        print("1. Gerar um novo Sudoku")
        print("2. Resolver um Sudoku existente (Exemplo)")
        print("3. Adicionar Sudoku Manualmente")
        print("0. Sair")
        
        escolha = input("\nEscolha uma opção: ")
        
        if escolha == "1":
            caso_gerar_sudoku()
        elif escolha == "2":
            caso_resolver_existente()
        elif escolha == "3":
            caso_adicionar_manual()
        elif escolha == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")
